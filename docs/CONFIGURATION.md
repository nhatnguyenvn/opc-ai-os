# Configuration contracts

Machine-readable .yaml files use the JSON subset of YAML 1.2, parsed with Python standard-library json for deterministic, dependency-free validation. Ordinary YAML syntax is intentionally rejected for package files. CI itself uses native YAML.

Schemas use a documented JSON Schema subset: type, required, properties, additionalProperties, enum, const, pattern, minLength, items, minItems, uniqueItems. The validator rejects unknown schema keywords. Schema files are not loaded as business objects.

System VERSION starts 1.0.0-dev; approved specification 1.0 is normalized to independent package version 1.0.0. A change of package version must update exact dependency/manifest pins. No date-derived release versions.

IDs are immutable and unique at registry scope. Prefixes: AGENT, HC, PC, SC, FC, OC, SCG, POL, PERM, DT, WF, OBJ, TEST, REL, CR. References use repository-relative POSIX paths; path escapes are rejected.

Environment credentials are logical references only. Development/test/staging/production have distinct database and connector references. No execution is enabled in this foundation.
