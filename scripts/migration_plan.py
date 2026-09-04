"""Plan the Wave 0 namespace bootstrap; no credentials or network access.

This deliberately accepts only CREATE SCHEMA statements, not arbitrary SQL.
Domain migration ordering requires a subsequent implementation before Wave 1.
Submit sql_statements as ONE transaction, never as separate committed calls.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path


def build_plan(filename, sql):
    if filename != '0001_namespaces.sql':
        raise ValueError('Only the Wave 0 bootstrap migration is supported')
    canonical = sql.replace('\r\n', '\n').replace('\r', '\n')
    checksum = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    clean = re.sub(r'--[^\n]*', '', canonical).strip()
    match = re.fullmatch(r'BEGIN;\s*(.*?)\s*COMMIT;', clean, re.S)
    if not match:
        raise ValueError('Migration must have one BEGIN/COMMIT wrapper')
    body = match.group(1)
    commands = re.findall(r'CREATE SCHEMA ([a-z][a-z0-9_]*);', body)
    residue = re.sub(r'CREATE SCHEMA [a-z][a-z0-9_]*;', '', body)
    if residue.strip() or not commands or len(set(commands)) != len(commands):
        raise ValueError('Only unique CREATE SCHEMA statements are allowed')
    guard = """DO $guard$
DECLARE recorded text;
BEGIN
  IF to_regclass('audit.schema_migration') IS NOT NULL THEN
    SELECT sha256 INTO recorded FROM audit.schema_migration
      WHERE migration_id = '0001_namespaces.sql';
    IF recorded IS NULL THEN
      RAISE EXCEPTION 'MIG_HISTORY_CONFLICT';
    ELSIF recorded <> '%s' THEN
      RAISE EXCEPTION 'MIG_CHECKSUM_DRIFT';
    ELSE
      RAISE EXCEPTION 'MIG_ALREADY_APPLIED';
    END IF;
  END IF;
END $guard$;""" % checksum
    statements = [
        "SET LOCAL lock_timeout = '5s'",
        "SET LOCAL statement_timeout = '30s'",
        'SELECT pg_advisory_xact_lock(168502155, 1)',
        guard,
        *[f'CREATE SCHEMA {name}' for name in commands],
        """CREATE TABLE audit.schema_migration (
          migration_id text PRIMARY KEY,
          sha256 text NOT NULL CHECK (sha256 ~ '^[a-f0-9]{64}$'),
          applied_at timestamptz NOT NULL DEFAULT clock_timestamp(),
          applied_by text NOT NULL DEFAULT current_user,
          CHECK (migration_id = '0001_namespaces.sql')
        )""",
        'REVOKE ALL ON audit.schema_migration FROM PUBLIC',
        "INSERT INTO audit.schema_migration (migration_id, sha256) "
        f"VALUES ('{filename}', '{checksum}')",
    ]
    return {'migration_id': filename, 'sha256': checksum,
            'checksum_encoding': 'UTF-8 with LF line endings',
            'transaction_required': True, 'schemas': commands,
            'sql_statements': statements}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('migration', type=Path)
    args = parser.parse_args()
    try:
        plan = build_plan(args.migration.name, args.migration.read_text(encoding='utf-8'))
    except (ValueError, OSError) as error:
        parser.exit(1, f'Migration plan rejected: {error}\n')
    print(json.dumps(plan, indent=2))


if __name__ == '__main__':
    main()
