SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
DO $$ BEGIN
 BEGIN
  INSERT INTO operations.workflow_definition_seal(business_id,workflow_version_id)
   VALUES(gen_random_uuid(),gen_random_uuid());
  RAISE SQLSTATE 'ZX032' USING MESSAGE='unsupported isolation accepted';
 EXCEPTION WHEN check_violation THEN
  IF SQLERRM<>'WORKFLOW_DEFINITION_REQUIRES_READ_COMMITTED' THEN RAISE; END IF;
 END;
END $$;
