-- Read-only Wave 0 qualification. Execute after the transaction planner.
DO $verify$
BEGIN
  IF (SELECT count(*) FROM pg_namespace
      WHERE nspname IN ('core','governance','product','sales','operations',
                       'finance','strategy','audit','integration')
        AND pg_get_userbyid(nspowner) = current_user) <> 9 THEN
    RAISE EXCEPTION 'MIG_NAMESPACE_DRIFT';
  END IF;
  IF (SELECT count(*) FROM audit.schema_migration) <> 1 OR NOT EXISTS (
    SELECT 1 FROM audit.schema_migration
    WHERE migration_id = '0001_namespaces.sql'
      AND sha256 = '96b060a33e0e11b386c49601d7d98480e30bc282596e9d8b2f258da95eaed44e'
  ) THEN
    RAISE EXCEPTION 'MIG_LEDGER_DRIFT';
  END IF;
END $verify$;
