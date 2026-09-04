-- Fixtures and their audit rows always roll back; assertion errors propagate.
DO $test$
DECLARE a uuid:=gen_random_uuid(); b uuid:=gen_random_uuid(); other_b uuid:=gen_random_uuid();
 w uuid:=gen_random_uuid(); v uuid:=gen_random_uuid(); incomplete uuid:=gen_random_uuid();
 venture uuid:=gen_random_uuid(); assumption uuid:=gen_random_uuid(); risk uuid:=gen_random_uuid();
 table_name text;
BEGIN
 BEGIN
  INSERT INTO core.actor(id,reference,name,actor_type) VALUES(a,'DEF-A','Owner','FOUNDER');
  INSERT INTO core.business(id,reference,name,default_currency,founder_actor_id)
   VALUES(b,'DEF-B','Business','USD',a),(other_b,'DEF-B2','Other','USD',a);
  INSERT INTO core.actor_business VALUES(b,a),(other_b,a); SET CONSTRAINTS ALL IMMEDIATE;
  INSERT INTO operations.workflow(id,reference,business_id,name,owner_actor_id) VALUES(w,'DEF-W',b,'Test',a);
  INSERT INTO operations.workflow_version(id,business_id,workflow_id,version_number,definition_reference,definition_hash)
   VALUES(v,b,w,'1','fixture:definition',repeat('a',64)),(incomplete,b,w,'2','fixture:incomplete',repeat('b',64));
  BEGIN
   INSERT INTO operations.workflow_definition_seal(business_id,workflow_version_id) VALUES(b,incomplete);
   RAISE SQLSTATE 'ZX030' USING MESSAGE='incomplete definition sealed';
  EXCEPTION WHEN check_violation THEN IF SQLERRM<>'WORKFLOW_DEFINITION_INCOMPLETE' THEN RAISE; END IF; END;
  BEGIN
   INSERT INTO operations.workflow_run(reference,business_id,workflow_version_id,owner_actor_id,trigger_reference)
    VALUES('DEF-NO-RUN',b,incomplete,a,'fixture');
   RAISE SQLSTATE 'ZX030' USING MESSAGE='unsealed run accepted';
  EXCEPTION WHEN foreign_key_violation THEN NULL; END;
  INSERT INTO operations.workflow_definition(business_id,workflow_version_id,name,owner_actor_id,trigger_specification,
   sla,expected_output,exception_rules,retry_rules,rollback_rules,completion_criteria,status)
   VALUES(b,v,'Definition v1',a,'Manual',interval '1 hour','Report','Escalate','No retries','No effects','Report verified','DRAFT');
  BEGIN
   INSERT INTO operations.workflow_definition_seal(business_id,workflow_version_id) VALUES(b,v);
   RAISE SQLSTATE 'ZX030' USING MESSAGE='definition without steps sealed';
  EXCEPTION WHEN check_violation THEN IF SQLERRM<>'WORKFLOW_DEFINITION_INCOMPLETE' THEN RAISE; END IF; END;
  INSERT INTO operations.workflow_step VALUES(b,v,1,'Research'),(b,v,2,'Report');
  INSERT INTO operations.workflow_definition_item VALUES
   (b,v,'INPUT',1,'fixture:input@1','Request'),(b,v,'DECISION_POINT',1,'fixture:decision@1','Quality gate'),
   (b,v,'POLICY',1,'fixture:policy@1','Required policy'),(b,v,'APPROVAL',1,'fixture:approval@1','Required approval'),
   (b,v,'TOOL',1,'fixture:tool@1','Read-only tool'),(b,v,'KPI',1,'fixture:kpi@1','Completion rate');
  INSERT INTO operations.workflow_step_dependency VALUES(b,v,2,1);
  BEGIN
   INSERT INTO operations.workflow_step_dependency VALUES(b,v,1,2);
   INSERT INTO operations.workflow_definition_seal(business_id,workflow_version_id) VALUES(b,v);
   RAISE SQLSTATE 'ZX030' USING MESSAGE='cyclic definition sealed';
  EXCEPTION WHEN check_violation THEN IF SQLERRM<>'WORKFLOW_DEFINITION_CYCLE' THEN RAISE; END IF; END;
  INSERT INTO operations.workflow_definition_seal(business_id,workflow_version_id,created_by)
   VALUES(b,v,'spoofed');
  IF (SELECT created_by FROM operations.workflow_definition_seal WHERE workflow_version_id=v) <> current_user THEN
   RAISE SQLSTATE 'ZX030' USING MESSAGE='seal actor spoofed'; END IF;
  INSERT INTO operations.workflow_run(reference,business_id,workflow_version_id,owner_actor_id,trigger_reference)
   VALUES('DEF-R',b,v,a,'fixture');
  BEGIN
   INSERT INTO operations.workflow_step VALUES(b,v,3,'Late step');
   RAISE SQLSTATE 'ZX030' USING MESSAGE='sealed definition extended';
  EXCEPTION WHEN check_violation THEN IF SQLERRM<>'WORKFLOW_DEFINITION_SEALED' THEN RAISE; END IF; END;
  BEGIN
   INSERT INTO operations.workflow_definition_item VALUES(b,v,'POLICY',2,'fixture:late','Late policy');
   RAISE SQLSTATE 'ZX030' USING MESSAGE='sealed requirements extended';
  EXCEPTION WHEN check_violation THEN IF SQLERRM<>'WORKFLOW_DEFINITION_SEALED' THEN RAISE; END IF; END;
  BEGIN
   INSERT INTO operations.workflow_step_dependency VALUES(b,v,1,2);
   RAISE SQLSTATE 'ZX030' USING MESSAGE='sealed dependencies extended';
  EXCEPTION WHEN check_violation THEN IF SQLERRM<>'WORKFLOW_DEFINITION_SEALED' THEN RAISE; END IF; END;
  FOREACH table_name IN ARRAY ARRAY['workflow_definition','workflow_step','workflow_definition_item',
                                  'workflow_step_dependency','workflow_definition_seal'] LOOP
   BEGIN
    EXECUTE format('TRUNCATE operations.%I',table_name);
    RAISE SQLSTATE 'ZX030' USING MESSAGE='definition truncate accepted';
   EXCEPTION WHEN SQLSTATE 'P0001' THEN IF SQLERRM<>'APPEND_ONLY_HISTORY' THEN RAISE; END IF;
    -- PostgreSQL can reject TRUNCATE first because a referenced table is omitted.
    WHEN feature_not_supported THEN IF position('foreign key' in SQLERRM)=0 THEN RAISE; END IF;
   END;
  END LOOP;
  BEGIN
   UPDATE operations.workflow_definition SET name='Rewritten' WHERE workflow_version_id=v;
   RAISE SQLSTATE 'ZX030' USING MESSAGE='definition changed';
  EXCEPTION WHEN SQLSTATE 'P0001' THEN IF SQLERRM<>'APPEND_ONLY_HISTORY' THEN RAISE; END IF; END;
  BEGIN
   DELETE FROM operations.workflow_definition_seal WHERE workflow_version_id=v;
   RAISE SQLSTATE 'ZX030' USING MESSAGE='seal removed';
  EXCEPTION WHEN SQLSTATE 'P0001' THEN IF SQLERRM<>'APPEND_ONLY_HISTORY' THEN RAISE; END IF; END;
  BEGIN
   INSERT INTO operations.workflow_definition_item VALUES(other_b,incomplete,'INPUT',1,'fixture:foreign','Foreign');
   RAISE SQLSTATE 'ZX030' USING MESSAGE='cross-business definition accepted';
  EXCEPTION WHEN foreign_key_violation THEN NULL; END;
  INSERT INTO core.venture(id,reference,business_id,name,owner_actor_id,currency) VALUES(venture,'DEF-V',b,'Venture',a,'USD');
  INSERT INTO governance.assumption(id,reference,business_id,owner_actor_id,statement) VALUES(assumption,'DEF-AS',b,a,'Hypothesis');
  INSERT INTO governance.risk(id,reference,business_id,owner_actor_id,description) VALUES(risk,'DEF-RISK',b,a,'Risk');
  INSERT INTO governance.venture_assumption VALUES(b,venture,assumption);
  INSERT INTO governance.venture_risk VALUES(b,venture,risk);
  BEGIN
   UPDATE governance.venture_risk SET business_id=other_b WHERE venture_id=venture;
   RAISE SQLSTATE 'ZX030' USING MESSAGE='cross-business venture risk accepted';
  EXCEPTION WHEN foreign_key_violation THEN NULL; END;
  DELETE FROM governance.venture_assumption WHERE venture_id=venture;
  IF (SELECT count(*) FROM audit.organization_relationship_history
      WHERE relation_name='venture_assumption' AND row_data->>'venture_id'=venture::text) <> 2 THEN
   RAISE SQLSTATE 'ZX030' USING MESSAGE='venture relationship history missing'; END IF;
  RAISE SQLSTATE 'ZX031';
 EXCEPTION WHEN SQLSTATE 'ZX031' THEN NULL; END;
END $test$;
