DO $test$
DECLARE human uuid:=gen_random_uuid(); ai uuid:=gen_random_uuid();
        biz uuid:=gen_random_uuid(); agent uuid:=gen_random_uuid();
BEGIN
 BEGIN
  INSERT INTO core.actor(id,reference,name,actor_type) VALUES(human,'HARD-HUMAN','Human','HUMAN');
  BEGIN
   INSERT INTO core.agent(reference,actor_id,domain,instruction_version,permission_profile_id)
    VALUES('BAD-AGENT',human,'test','1','test');
   RAISE EXCEPTION 'non-AI actor accepted for Agent';
  EXCEPTION WHEN foreign_key_violation THEN NULL; END;
  INSERT INTO core.actor(id,reference,name,actor_type,version,created_by)
   VALUES(ai,'HARD-AI','AI','AI_AGENT',999,'spoof');
  IF NOT EXISTS(SELECT 1 FROM core.actor WHERE id=ai AND version=1 AND created_by=current_user) THEN
   RAISE EXCEPTION 'initial provenance/version spoof accepted';
  END IF;
  INSERT INTO core.agent(id,reference,actor_id,domain,instruction_version,permission_profile_id)
   VALUES(agent,'GOOD-AGENT',ai,'test','1','test');
  BEGIN
   UPDATE core.actor SET actor_type='HUMAN' WHERE id=ai;
   RAISE EXCEPTION 'linked actor type changed';
  EXCEPTION WHEN foreign_key_violation THEN NULL; END;
  INSERT INTO core.business(id,reference,name,default_currency,founder_actor_id)
   VALUES(biz,'HARD-BIZ','Business','USD',human);
  INSERT INTO core.actor_business VALUES(biz,human);
  INSERT INTO core.actor_business VALUES(biz,ai);
  SET CONSTRAINTS ALL IMMEDIATE;
  INSERT INTO core.agent_business VALUES(agent,ai,biz);
  DELETE FROM core.agent_business WHERE agent_id=agent AND business_id=biz;
  IF (SELECT count(*) FROM audit.organization_relationship_history
      WHERE relation_name='agent_business' AND row_data->>'agent_id'=agent::text) <> 2 THEN
   RAISE EXCEPTION 'scope history missing';
  END IF;
  BEGIN
   TRUNCATE core.venture;
   RAISE EXCEPTION 'TRUNCATE accepted';
  EXCEPTION WHEN SQLSTATE 'P0002' THEN NULL; END;
  RAISE SQLSTATE 'ZX002';
 EXCEPTION WHEN SQLSTATE 'ZX002' THEN NULL; END;
END $test$;
