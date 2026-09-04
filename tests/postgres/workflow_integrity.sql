DO $test$
DECLARE a uuid:=gen_random_uuid(); b uuid:=gen_random_uuid(); w uuid:=gen_random_uuid();
 v uuid:=gen_random_uuid(); r uuid:=gen_random_uuid(); t1 uuid:=gen_random_uuid();
 t2 uuid:=gen_random_uuid(); t3 uuid:=gen_random_uuid();
BEGIN
 BEGIN
  INSERT INTO core.actor(id,reference,name,actor_type) VALUES(a,'DAG-A','Owner','FOUNDER');
  INSERT INTO core.business(id,reference,name,default_currency,founder_actor_id) VALUES(b,'DAG-B','Business','USD',a);
  INSERT INTO core.actor_business VALUES(b,a); SET CONSTRAINTS ALL IMMEDIATE;
  INSERT INTO operations.workflow(id,reference,business_id,name,owner_actor_id) VALUES(w,'DAG-W',b,'Test',a);
  INSERT INTO operations.workflow_version(id,business_id,workflow_id,version_number,definition_reference,definition_hash)
   VALUES(v,b,w,'1','fixture:dag',repeat('a',64));
  INSERT INTO operations.workflow_run(id,reference,business_id,workflow_version_id,owner_actor_id,trigger_reference)
   VALUES(r,'DAG-R',b,v,a,'fixture');
  INSERT INTO operations.task(id,reference,business_id,workflow_run_id,owner_actor_id,objective)
   VALUES(t1,'DAG-T1',b,r,a,'One'),(t2,'DAG-T2',b,r,a,'Two'),(t3,'DAG-T3',b,r,a,'Three');
  INSERT INTO operations.task_dependency VALUES(b,t1,t2),(b,t2,t3);
  BEGIN
   INSERT INTO operations.task_dependency VALUES(b,t3,t1);
   RAISE SQLSTATE 'ZX020' USING MESSAGE='dependency cycle accepted';
  EXCEPTION WHEN SQLSTATE '23514' THEN
   IF SQLERRM<>'TASK_DEPENDENCY_CYCLE' THEN RAISE; END IF;
  END;
  DELETE FROM operations.task_dependency WHERE task_id=t1 AND depends_on_id=t2;
  IF (SELECT count(*) FROM audit.organization_relationship_history
      WHERE relation_name='task_dependency' AND row_data->>'task_id'=t1::text) <> 2 THEN
   RAISE EXCEPTION 'dependency history missing';
  END IF;
  RAISE SQLSTATE 'ZX021';
 EXCEPTION WHEN SQLSTATE 'ZX021' THEN NULL; END;
END $test$;
