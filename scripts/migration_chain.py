"""Ordered migration plans with transaction-time predecessor verification.

Migration JSON contains reviewed SQL statements, not untrusted input. The caller
must submit each returned statement array as a single database transaction.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path
from migration_plan import build_plan

ROOT = Path(__file__).resolve().parents[1]


def validate_history(expected, actual):
    if len(actual) > len(expected):
        raise ValueError('MIG_HISTORY_CONFLICT')
    for want, got in zip(expected, actual):
        if want['migration_id'] != got['migration_id']:
            raise ValueError('MIG_HISTORY_CONFLICT')
        if want['sha256'] != got['sha256']:
            raise ValueError('MIG_CHECKSUM_DRIFT')
    return len(actual)


def load_chain(directory=ROOT / 'migrations'):
    names = json.loads((directory / 'chain.json').read_text(encoding='utf-8'))['migrations']
    if not names or names[0] != '0001_namespaces.sql':
        raise ValueError('Invalid bootstrap')
    chain = []
    for index, name in enumerate(names, 1):
        if not re.fullmatch(rf'{index:04d}_[a-z0-9_]+\.(sql|json)', name):
            raise ValueError('Migration names must be contiguous and path-safe')
        source = (directory / name).read_text(encoding='utf-8').replace('\r\n', '\n').replace('\r', '\n')
        if index == 1:
            plan = build_plan(name, source)
        else:
            data = json.loads(source)
            statements = data['statements']
            if not isinstance(statements, list) or not statements or any(
                not isinstance(s, str) or not s.strip() for s in statements
            ):
                raise ValueError('Nonempty SQL statement array required')
            plan = {'migration_id': name,
                    'sha256': hashlib.sha256(source.encode('utf-8')).hexdigest(),
                    'sql_statements': statements}
        chain.append(plan)
    return chain


def transaction_plan(chain, index):
    if not 0 <= index < len(chain):
        raise ValueError('Invalid migration index')
    if index == 0:
        return chain[0]['sql_statements']
    prefix = [{k: p[k] for k in ('migration_id', 'sha256')} for p in chain[:index]]
    expected = json.dumps(prefix).replace("'", "''")
    table = 'audit.schema_migration' if index == 1 else 'audit.migration_history'
    guard = f"""DO $guard$
DECLARE actual jsonb;
BEGIN
  SELECT coalesce(jsonb_agg(jsonb_build_object('migration_id', migration_id,
    'sha256', sha256) ORDER BY migration_id), '[]'::jsonb) INTO actual FROM {table};
  IF actual <> '{expected}'::jsonb THEN
    RAISE EXCEPTION 'MIG_HISTORY_OR_CHECKSUM_CONFLICT';
  END IF;
END $guard$"""
    current = chain[index]
    return ["SET LOCAL lock_timeout = '5s'", "SET LOCAL statement_timeout = '30s'",
            'SELECT pg_advisory_xact_lock(168502155, 1)', guard,
            *current['sql_statements'],
            "INSERT INTO audit.migration_history (migration_id, sha256) "
            f"VALUES ('{current['migration_id']}', '{current['sha256']}')"]


def read_history(connection):
    row = connection.execute("SELECT to_regclass('audit.migration_history'), "
                             "to_regclass('audit.schema_migration')").fetchone()
    table = 'audit.migration_history' if row[0] else 'audit.schema_migration' if row[1] else None
    if not table:
        return []
    return [dict(migration_id=r[0], sha256=r[1]) for r in connection.execute(
        f'SELECT migration_id, sha256 FROM {table} ORDER BY migration_id').fetchall()]


def apply_pending(connection, chain):
    """Connection must be autocommit; one explicit transaction per migration."""
    if not connection.autocommit:
        raise ValueError('Autocommit connection required for explicit transactions')
    start = validate_history(chain, read_history(connection))
    for index in range(start, len(chain)):
        with connection.transaction():
            for statement in transaction_plan(chain, index):
                connection.execute(statement)
    validate_history(chain, read_history(connection))
    return len(chain) - start


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Emit a transaction plan; no database access')
    parser.add_argument('--index', type=int, required=True, help='Zero-based migration index')
    args = parser.parse_args()
    chain = load_chain()
    print(json.dumps({'migration_id': chain[args.index]['migration_id'],
                      'sha256': chain[args.index]['sha256'],
                      'sql_statements': transaction_plan(chain, args.index)}, indent=2))
