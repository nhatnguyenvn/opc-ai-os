DO $test$
DECLARE a uuid:=gen_random_uuid(); b uuid:=gen_random_uuid(); b2 uuid:=gen_random_uuid();
 e uuid:=gen_random_uuid(); ass uuid:=gen_random_uuid(); d uuid:=gen_random_uuid();
BEGIN
 BEGIN
  INSERT INTO core.actor(id,reference,name,actor_type) VALUES(a,'SUP-A','Owner','FOUNDER');
  INSERT INTO core.business(id,reference,name,default_currency,founder_actor_id)
   VALUES(b,'SUP-B','Business','USD',a),(b2,'SUP-B2','Other','USD',a);
  INSERT INTO core.actor_business VALUES(b,a),(b2,a);
  SET CONSTRAINTS ALL IMMEDIATE;
  INSERT INTO governance.evidence(id,reference,business_id,owner_actor_id,source_type,source_ref,summary,captured_at)
   VALUES(e,'SUP-E',b,a,'DOCUMENT','fixture:document','Test source',now());
  INSERT INTO governance.assumption(id,reference,business_id,owner_actor_id,statement)
   VALUES(ass,'SUP-S',b,a,'Test statement');
  IF (SELECT status FROM governance.assumption WHERE id=ass)<>'UNTESTED' THEN RAISE EXCEPTION 'incorrect assumption default'; END IF;
  UPDATE governance.assumption SET status='SUPPORTED' WHERE id=ass;
  BEGIN
   UPDATE governance.assumption SET status='ACTIVE' WHERE id=ass;
   RAISE EXCEPTION 'noncanonical assumption state accepted';
  EXCEPTION WHEN foreign_key_violation THEN NULL; END;
  INSERT INTO governance.assumption_evidence VALUES(b,ass,e);
  INSERT INTO governance.decision(id,reference,business_id,owner_actor_id,question) VALUES(d,'SUP-D',b2,a,'Test');
  BEGIN
   INSERT INTO governance.decision_evidence VALUES(b2,d,e);
   RAISE EXCEPTION 'cross-business evidence accepted';
  EXCEPTION WHEN foreign_key_violation THEN NULL; END;
  BEGIN
   INSERT INTO governance.risk(reference,business_id,owner_actor_id,description,probability)
    VALUES('SUP-R',b,a,'Risk',1.01);
   RAISE EXCEPTION 'probability out of range accepted';
  EXCEPTION WHEN check_violation THEN NULL; END;
  BEGIN
   INSERT INTO governance.change_request(reference,business_id,owner_actor_id,requested_change,reason,target_reference,approval_id)
    VALUES('SUP-C',b,a,'Change','Reason','fixture:system',gen_random_uuid());
   RAISE EXCEPTION 'orphan approval accepted';
  EXCEPTION WHEN foreign_key_violation THEN NULL; END;
  INSERT INTO governance.exception(reference,business_id,owner_actor_id,description)
   VALUES('SUP-X',b,a,'Test exception');
  IF NOT EXISTS(SELECT 1 FROM audit.organization_history WHERE object_type='assumption' AND object_id=ass AND version=2) THEN
   RAISE EXCEPTION 'assumption history missing';
  END IF;
  RAISE SQLSTATE 'ZX007';
 EXCEPTION WHEN SQLSTATE 'ZX007' THEN NULL; END;
END $test$;
