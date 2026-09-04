-- OPC-BUILD-002 Wave 0: logical namespaces, no extension dependencies.
-- Non-production qualification required; an existing schema must fail reviewably.
BEGIN;
CREATE SCHEMA core;
CREATE SCHEMA governance;
CREATE SCHEMA product;
CREATE SCHEMA sales;
CREATE SCHEMA operations;
CREATE SCHEMA finance;
CREATE SCHEMA strategy;
CREATE SCHEMA audit;
CREATE SCHEMA integration;
COMMIT;
