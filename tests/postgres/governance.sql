-- All fixtures roll back, including generated audit history.
DO $test$
DECLARE a uuid:=gen_random_uuid(); b uuid:=gen_random_uuid();
        recipient uuid:=gen_random_uuid(); d uuid:=gen_random_uuid(); p uuid:=gen_random_uuid();
BEGIN
 BEGIN
  INSERT INTO core.actor(id,reference,name,actor_type) VALUES(a,'GOV-A','Founder','FOUNDER'),(recipient,'GOV-R','Recipient','HUMAN');
  INSERT INTO core.business(id,reference,name,default_currency,founder_actor_id) VALUES(b,'GOV-B','Business','USD',a);
  INSERT INTO core.actor_business VALUES(b,a),(b,recipient);
  SET CONSTRAINTS ALL IMMEDIATE;
  INSERT INTO governance.delegation(id,reference,business_id,from_actor_id,to_actor_id,authority,scope,terms_hash,effective_from,expires_at)
   VALUES(d,'GOV-D',b,a,recipient,'TEST_ONLY','fixture-scope',repeat('a',64),now()-interval '1 hour',now()+interval '1 hour');
  IF EXISTS(SELECT 1 FROM governance.effective_delegation WHERE id=d) THEN RAISE EXCEPTION 'unapproved delegation effective'; END IF;
  BEGIN
   UPDATE governance.delegation SET approval_id=gen_random_uuid() WHERE id=d;
   RAISE EXCEPTION 'orphan approval accepted';
  EXCEPTION WHEN foreign_key_violation THEN NULL; END;
  INSERT INTO governance.approval(id,reference,business_id,requestor_actor_id,authority_actor_id,recipient_actor_id,action_type,object_type,object_id,object_version,scope,authority,exact_terms_hash,status,approved_at,expires_at)
   VALUES(p,'GOV-P',b,a,a,recipient,'DELEGATE','delegation',d,2,'fixture-scope','TEST_ONLY',repeat('a',64),'APPROVED',now()-interval '1 minute',now()+interval '1 hour');
  UPDATE governance.delegation SET approval_id=p,status='ACTIVE' WHERE id=d;
  IF NOT EXISTS(SELECT 1 FROM governance.effective_delegation WHERE id=d) THEN RAISE EXCEPTION 'matching delegation not effective'; END IF;
  BEGIN
   INSERT INTO governance.approval(reference,business_id,requestor_actor_id,authority_actor_id,recipient_actor_id,action_type,object_type,object_id,object_version,scope,authority,exact_terms_hash,status,approved_at,expires_at)
    VALUES('GOV-EXPIRED',b,a,a,recipient,'DELEGATE','delegation',d,3,'fixture-scope','TEST_ONLY',repeat('a',64),'APPROVED',now()-interval '2 hours',now()-interval '1 hour');
   UPDATE governance.delegation SET approval_id=(SELECT id FROM governance.approval WHERE reference='GOV-EXPIRED' AND business_id=b) WHERE id=d;
   IF EXISTS(SELECT 1 FROM governance.effective_delegation WHERE id=d) THEN RAISE EXCEPTION 'expired approval effective'; END IF;
   RAISE SQLSTATE 'ZX005';
  EXCEPTION WHEN SQLSTATE 'ZX005' THEN NULL; END;
  BEGIN
   UPDATE governance.approval SET scope='rewritten' WHERE id=p;
   RAISE SQLSTATE 'ZX006' USING MESSAGE='issued approval rewritten';
  EXCEPTION WHEN SQLSTATE 'P0001' THEN
   IF SQLERRM <> 'ISSUED_APPROVAL_IMMUTABLE' THEN RAISE; END IF;
  END;
  BEGIN
   UPDATE governance.approval SET status='REVOKED' WHERE id=p;
   IF EXISTS(SELECT 1 FROM governance.effective_delegation WHERE id=d) THEN RAISE EXCEPTION 'revoked approval effective'; END IF;
   RAISE SQLSTATE 'ZX004';
  EXCEPTION WHEN SQLSTATE 'ZX004' THEN NULL; END;
  UPDATE governance.delegation SET scope='changed' WHERE id=d;
  IF EXISTS(SELECT 1 FROM governance.effective_delegation WHERE id=d) THEN RAISE EXCEPTION 'changed scope/version reused approval'; END IF;
  BEGIN
   INSERT INTO governance.decision(reference,business_id,owner_actor_id,question,confidence)
    VALUES('GOV-BAD',b,a,'Test',1.1);
   RAISE EXCEPTION 'invalid confidence accepted';
  EXCEPTION WHEN check_violation THEN NULL; END;
  RAISE SQLSTATE 'ZX003';
 EXCEPTION WHEN SQLSTATE 'ZX003' THEN NULL; END;
END $test$;
