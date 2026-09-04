-- Fixtures run in a subtransaction and are rolled back even on success.
DO $test$
DECLARE a uuid := gen_random_uuid(); b uuid := gen_random_uuid();
        other_b uuid := gen_random_uuid(); v uuid := gen_random_uuid();
        outsider uuid := gen_random_uuid();
BEGIN
  BEGIN
    INSERT INTO core.actor(id,reference,name,actor_type) VALUES(a,'TEST-ACTOR','Test founder','FOUNDER');
    INSERT INTO core.business(id,reference,name,default_currency,founder_actor_id)
      VALUES(b,'TEST-BUSINESS','Test business','USD',a);
    INSERT INTO core.actor_business(business_id,actor_id) VALUES(b,a);
    INSERT INTO core.business(id,reference,name,default_currency,founder_actor_id)
      VALUES(other_b,'TEST-OTHER','Other business','USD',a);
    INSERT INTO core.actor_business(business_id,actor_id) VALUES(other_b,a);
    INSERT INTO core.actor(id,reference,name,actor_type) VALUES(outsider,'OUTSIDER','Other actor','HUMAN');
    INSERT INTO core.actor_business(business_id,actor_id) VALUES(other_b,outsider);
    SET CONSTRAINTS ALL IMMEDIATE;
    INSERT INTO core.venture(id,reference,business_id,name,owner_actor_id,currency)
      VALUES(v,'TEST-VENTURE',b,'Test venture',a,'USD');
    BEGIN
      INSERT INTO core.business(reference,name,default_currency,founder_actor_id)
        VALUES('TEST-BUSINESS','Duplicate','USD',a);
      RAISE EXCEPTION 'duplicate reference accepted';
    EXCEPTION WHEN unique_violation THEN NULL; END;
    BEGIN
      INSERT INTO core.legal_entity(reference,business_id,legal_name,jurisdiction)
        VALUES('ORPHAN',gen_random_uuid(),'Orphan','VN');
      RAISE EXCEPTION 'orphan business accepted';
    EXCEPTION WHEN foreign_key_violation THEN NULL; END;
    BEGIN
      INSERT INTO core.venture(reference,business_id,name,owner_actor_id,currency)
        VALUES('BAD-OWNER',b,'Bad owner',outsider,'USD');
      RAISE EXCEPTION 'unscoped owner accepted';
    EXCEPTION WHEN foreign_key_violation THEN NULL; END;
    BEGIN
      UPDATE core.venture SET allocated_capital=-1 WHERE id=v;
      RAISE EXCEPTION 'negative capital accepted';
    EXCEPTION WHEN check_violation THEN NULL; END;
    BEGIN
      UPDATE core.venture SET status='UNKNOWN' WHERE id=v;
      RAISE EXCEPTION 'invalid status accepted';
    EXCEPTION WHEN foreign_key_violation THEN NULL; END;
    UPDATE core.venture SET name='Updated' WHERE id=v;
    IF (SELECT version FROM core.venture WHERE id=v) <> 2 THEN
      RAISE EXCEPTION 'version not advanced';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM audit.organization_history WHERE object_id=v AND version=1) THEN
      RAISE EXCEPTION 'previous version not retained';
    END IF;
    BEGIN
      DELETE FROM core.venture WHERE id=v;
      RAISE EXCEPTION 'hard delete accepted';
    EXCEPTION WHEN SQLSTATE 'P0002' THEN NULL; END;
    RAISE SQLSTATE 'ZX001';
  EXCEPTION WHEN SQLSTATE 'ZX001' THEN NULL;
  END;
END $test$;
