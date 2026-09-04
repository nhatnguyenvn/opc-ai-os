"""CI-only real PostgreSQL checks. Requires a new empty local opc_ci database."""
import os
import sys
from pathlib import Path
import psycopg
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))
from migration_chain import apply_pending, load_chain, read_history, transaction_plan, validate_history


def run():
    with psycopg.connect(os.environ['OPC_DATABASE_TEST_URL'], autocommit=True) as conn:
        if conn.info.host not in ('localhost', '127.0.0.1') or conn.info.dbname != 'opc_ci':
            raise RuntimeError('CI qualification requires local disposable opc_ci database')
        if conn.execute("SELECT count(*) FROM pg_namespace WHERE nspname NOT IN "
                        "('public','information_schema') AND nspname NOT LIKE 'pg_%'").fetchone()[0]:
            raise RuntimeError('CI database must be empty')
        chain = load_chain()
        # An error after every bootstrap statement must leave no partial schema.
        try:
            with conn.transaction():
                for statement in transaction_plan(chain, 0):
                    conn.execute(statement)
                conn.execute('SELECT 1 / 0')
        except psycopg.errors.DivisionByZero:
            pass
        else:
            raise AssertionError('Broken migration unexpectedly succeeded')
        assert conn.execute("SELECT to_regclass('audit.schema_migration')").fetchone()[0] is None
        assert conn.execute("SELECT count(*) FROM pg_namespace WHERE nspname='core'").fetchone()[0] == 0
        # Clean-to-latest, including intermediate version committed independently.
        assert apply_pending(conn, chain[:1]) == 1
        assert apply_pending(conn, chain) == len(chain) - 1
        assert apply_pending(conn, chain) == 0  # intentional no-op for an exact chain
        assert validate_history(chain, read_history(conn)) == len(chain)
        altered = [dict(p) for p in chain]
        altered[0]['sha256'] = '0' * 64
        try:
            apply_pending(conn, altered)
        except ValueError as error:
            assert 'CHECKSUM' in str(error)
        else:
            raise AssertionError('Checksum drift accepted')
        # Database-time guard must reject an incorrect prefix, even if a stale
        # caller prepared a plan without running the Python preflight.
        try:
            with conn.transaction():
                for statement in transaction_plan(altered, 1):
                    conn.execute(statement)
        except psycopg.errors.RaiseException as error:
            assert 'MIG_HISTORY_OR_CHECKSUM_CONFLICT' in str(error)
        else:
            raise AssertionError('Database guard accepted incorrect predecessor')
        conn.execute((Path(__file__).resolve().parents[2] / 'migrations/0001_namespaces.verify.sql').read_text())
        print('PASS: clean bootstrap, upgrade, replay no-op, rollback, checksum drift, database guard')


if __name__ == '__main__':
    run()
