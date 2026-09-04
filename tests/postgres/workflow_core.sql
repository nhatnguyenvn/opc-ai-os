DO $test$
DECLARE a uuid:=gen_random_uuid(); b uuid:=gen_random_uuid(); w uuid:=gen_random_uuid();
 v uuid:=gen_random_uuid(); v2 uuid:=gen_random_uuid(); r uuid:=gen_random_uuid(); t uuid:=gen_random_uuid();
BEGIN
 BEGIN
  INSERT INTO core.actor(id,reference,name,actor_type) VALUES(a,'WF-A','Owner','FOUNDER');
  INSERT INTO core.business(id,reference,name,default_currency,founder_actor_id) VALUES(b,'WF-B','Business','USD',a);
  INSERT INTO core.actor_business VALUES(b,a); SET CONSTRAINTS ALL IMMEDIATE;
  INSERT INTO operations.workflow(id,reference,business_id,name,owner_actor_id) VALUES(w,'WF-TEST',b,'Test',a);
  INSERT INTO operations.workflow_version(id,business_id,workflow_id,version_number,definition_reference,definition_hash)
   VALUES(v,b,w,'1.0','fixture:v1',repeat('a',64)),(v2,b,w,'2.0','fixture:v2',repeat('b',64));
  INSERT INTO operations.workflow_definition(business_id,workflow_version_id,name,owner_actor_id,trigger_specification,
   sla,expected_output,exception_rules,retry_rules,rollback_rules,completion_criteria,status)
   SELECT b,id,'Fixture',a,'Manual',interval '1 hour','Result','Escalate','None','None','Verified','DRAFT'
    FROM operations.workflow_version WHERE business_id=b;
  INSERT INTO operations.workflow_step SELECT b,id,1,'Fixture step' FROM operations.workflow_version WHERE business_id=b;
  INSERT INTO operations.workflow_definition_seal(business_id,workflow_version_id)
   SELECT b,id FROM operations.workflow_version WHERE business_id=b;
  INSERT INTO operations.workflow_run(id,reference,business_id,workflow_version_id,owner_actor_id,trigger_reference)
   VALUES(r,'WF-R',b,v,a,'fixture:event');
  BEGIN
   UPDATE operations.workflow_version SET definition_reference='rewritten' WHERE id=v;
   RAISE SQLSTATE 'ZX011' USING MESSAGE='workflow version rewritten';
  EXCEPTION WHEN SQLSTATE 'P0001' THEN IF SQLERRM<>'APPEND_ONLY_HISTORY' THEN RAISE; END IF; END;
  BEGIN
   UPDATE operations.workflow_run SET workflow_version_id=v2 WHERE id=r;
   RAISE SQLSTATE 'ZX011' USING MESSAGE='run version rebound';
  EXCEPTION WHEN SQLSTATE 'P0001' THEN IF SQLERRM<>'PINNED_FIELD_CHANGED' THEN RAISE; END IF; END;
  INSERT INTO operations.task(id,reference,business_id,workflow_run_id,owner_actor_id,objective)
   VALUES(t,'WF-T',b,r,a,'Test objective');
  INSERT INTO operations.action(reference,business_id,task_id,actor_id,capability,intended_side_effect,idempotency_key)
   VALUES('WF-ACTION',b,t,a,'fixture','none','once');
  BEGIN
   INSERT INTO operations.action(reference,business_id,task_id,actor_id,capability,intended_side_effect,idempotency_key)
    VALUES('WF-ACTION2',b,t,a,'fixture','none','once');
   RAISE EXCEPTION 'duplicate action key accepted';
  EXCEPTION WHEN unique_violation THEN NULL; END;
  INSERT INTO operations.event(reference,business_id,event_type,source,idempotency_key,occurred_at,payload_reference)
   VALUES('WF-EVENT',b,'TEST','fixture','once',now(),'fixture:payload');
  BEGIN
   INSERT INTO operations.event(reference,business_id,event_type,source,idempotency_key,occurred_at,payload_reference)
    VALUES('WF-EVENT2',b,'TEST','fixture','once',now(),'fixture:payload');
   RAISE EXCEPTION 'duplicate event key accepted';
  EXCEPTION WHEN unique_violation THEN NULL; END;
  BEGIN
   UPDATE operations.action SET retry_count=-1 WHERE reference='WF-ACTION';
   RAISE EXCEPTION 'negative retries accepted';
  EXCEPTION WHEN check_violation THEN NULL; END;
  RAISE SQLSTATE 'ZX010';
 EXCEPTION WHEN SQLSTATE 'ZX010' THEN NULL; END;
END $test$;
