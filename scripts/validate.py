"""Deterministic foundation validator; JSON-subset YAML, no runtime execution."""
import argparse
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ('chief-of-staff', 'product', 'sales', 'finance', 'operations', 'strategy')
ENVS = ('development', 'test', 'staging', 'production')
KEYWORDS = {'type', 'required', 'properties', 'additionalProperties', 'enum', 'const',
            'pattern', 'minLength', 'items', 'minItems', 'uniqueItems'}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def read(path):
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)


def check_schema(value, schema, where, errors):
    unknown = set(schema) - KEYWORDS
    if unknown:
        errors.append(f'{where}: unsupported schema keywords {sorted(unknown)}')
    types = {'object': dict, 'array': list, 'string': str, 'boolean': bool,
             'integer': int, 'null': type(None)}
    expected = schema.get('type')
    if expected:
        allowed = expected if isinstance(expected, list) else [expected]
        if not any(type(value) is types.get(t) for t in allowed):
            errors.append(f'{where}: invalid type; expected {allowed}')
            return
    if 'const' in schema and (type(value) is not type(schema['const']) or value != schema['const']):
        errors.append(f'{where}: invalid constant')
    if 'enum' in schema and value not in schema['enum']:
        errors.append(f'{where}: invalid enum')
    if isinstance(value, str):
        if len(value) < schema.get('minLength', 0):
            errors.append(f'{where}: empty required value')
        if 'pattern' in schema and re.fullmatch(schema['pattern'], value) is None:
            errors.append(f'{where}: invalid format')
    if isinstance(value, dict):
        for key in schema.get('required', []):
            if key not in value:
                errors.append(f'{where}: missing required field {key}')
        props = schema.get('properties', {})
        for key, child in value.items():
            if key in props:
                check_schema(child, props[key], f'{where}.{key}', errors)
            elif schema.get('additionalProperties') is False:
                errors.append(f'{where}: unexpected field {key}')
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0):
            errors.append(f'{where}: missing required package or items')
        if schema.get('uniqueItems') and len({json.dumps(x, sort_keys=True) for x in value}) != len(value):
            errors.append(f'{where}: duplicate items')
        for index, child in enumerate(value):
            if 'items' in schema:
                check_schema(child, schema['items'], f'{where}[{index}]', errors)


def tracked_and_untracked(root):
    result = subprocess.run(['git', '-C', str(root), 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
                            capture_output=True, check=True)
    return sorted(set(result.stdout.decode('utf-8').split('\0')) - {''})


def validate(root=ROOT):
    root = Path(root).resolve()
    errors, documents = [], {}
    def load(relative):
        if relative in documents:
            return documents[relative]
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            errors.append(f'{relative}: invalid reference outside repository')
            return {}
        try:
            value = read(path)
            if not isinstance(value, dict):
                raise ValueError('configuration must be an object')
            documents[relative] = value
            return value
        except (OSError, ValueError) as exc:
            errors.append(f'{relative}: missing or malformed configuration ({type(exc).__name__})')
            return {}

    required = ['README.md', 'VERSION', 'CHANGELOG.md', '.gitignore', '.env.example',
                'CONTRIBUTING.md', 'docs/CHANGE_CONTROL.md', 'docs/REPOSITORY_ADMIN.md',
                '.github/workflows/validate.yml', 'docs/change-request.template.yaml',
                'config/ownership.json', 'config/package-index.json']
    required += [f'agents/{a}/{f}' for a in AGENTS for f in
                 ('identity.md', 'domain-controls.yaml', 'boundaries.yaml', 'outputs.yaml', 'tests.yaml')]
    for path in required:
        if not (root / path).is_file():
            errors.append(f'{path}: required file missing')
    for directory in load('config/package-index.json').get('required_directories', []):
        if not (root / directory).is_dir():
            errors.append(f'{directory}: required directory missing')
    try:
        system_version = (root / 'VERSION').read_text().strip()
    except OSError:
        system_version = ''
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?', system_version):
        errors.append('VERSION: invalid semantic version')

    bindings = {
        'constitution/v1.0/constitution.yaml': 'constitution',
        'runtime/shared/v1.0/runtime.yaml': 'runtime',
        'runtime/hard-controls/v1.0/controls.yaml': 'hard-control',
        'release/manifest.template.yaml': 'release',
    }
    bindings.update({f'agents/{a}/manifest.yaml': 'agent' for a in AGENTS})
    bindings.update({f'permissions/{a}.yaml': 'permission' for a in AGENTS})
    bindings.update({f'config/{e}/environment.yaml': 'environment' for e in ENVS})
    for directory, kind in [('policies', 'policy'), ('decision-tables', 'decision-table'),
                            ('workflows', 'workflow'), ('connectors', 'connector'),
                            ('release/manifests', 'release')]:
        for path in (root / directory).rglob('*'):
            if path.suffix in ('.json', '.yaml', '.yml'):
                bindings[path.relative_to(root).as_posix()] = kind
    schemas = {}
    for kind in ('constitution', 'runtime', 'agent', 'permission', 'hard-control', 'environment',
                 'policy', 'decision-table', 'workflow', 'connector', 'release'):
        path = 'release/manifest.schema.yaml' if kind == 'release' else f'schemas/config/{kind}.schema.json'
        schemas[kind] = load(path)
    for path, kind in bindings.items():
        check_schema(load(path), schemas[kind], path, errors)

    try:
        inventory = tracked_and_untracked(root)
    except subprocess.CalledProcessError:
        errors.append('repository: cannot inspect Git inventory')
        inventory = []
    # Scan only tracked and nonignored candidate files, never print matching values.
    patterns = [r'gh[pousr]_[A-Za-z0-9]{20,}', r'github_pat_[A-Za-z0-9_]{20,}',
                r'sk-[A-Za-z0-9_-]{20,}', r'AKIA[A-Z0-9]{16}',
                r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
                r'postgres(?:ql)?://[^\s:/]+:[^\s@]+@',
                r'(?i)(?:api_key|password|client_secret|access_token)\s*[=:]\s*[\"\x27]?[A-Za-z0-9_+/=-]{12,}']
    for relative in inventory:
        path = root / relative
        parts = Path(relative).parts
        if path.is_symlink():
            errors.append(f'{relative}: symbolic links prohibited in foundation')
            continue
        if ((path.name.startswith('.env') and path.name != '.env.example') or
                path.suffix.lower() in ('.pem', '.key', '.p12', '.pfx') or
                any(x in parts for x in ('secrets', 'credentials', 'local-data'))):
            errors.append(f'{relative}: forbidden secret file')
        try:
            text = path.read_text(encoding='utf-8')
        except (UnicodeError, OSError):
            errors.append(f'{relative}: unreadable or binary file requires explicit review')
            continue
        if any(re.search(pattern, text) for pattern in patterns):
            errors.append(f'{relative}: secret pattern detected')
        if path.suffix in ('.json', '.yaml', '.yml') and relative != '.github/workflows/validate.yml':
            load(relative)

    ids = {}
    for path, document in documents.items():
        if path.startswith('release/') or path.startswith('schemas/'):
            continue
        identifier = document.get('id')
        if identifier:
            if identifier in ids:
                errors.append(f'{path}: duplicate ID {identifier}')
            ids[identifier] = path
    registry = load('runtime/hard-controls/v1.0/controls.yaml')
    source_path = root / 'docs/reference/e10830ed-8526-4a37-a56b-ddc1ce9d9c4a.md'
    try:
        source = source_path.read_text(encoding='utf-8')
    except OSError:
        source = ''
    approved_controls = {m[0]: m[1] for m in re.findall(
        r'\| \*\*(HC-[A-Z]+-\d+)\*\* \| [^|]+ \| (P[01]) \|', source)}
    actual_controls = {c.get('control_id'): c.get('severity') for c in registry.get('controls', [])}
    if len(approved_controls) != 30 or actual_controls != approved_controls:
        errors.append('hard-controls: approved control set or severity changed')
    seen = set()
    for control in registry.get('controls', []):
        cid = control.get('control_id')
        if cid in seen:
            errors.append(f'hard-controls: duplicate control ID {cid}')
        seen.add(cid)
    for control in load('constitution/v1.0/constitution.yaml').get('controls', []):
        for ref in control.get('hard_control_refs', []):
            if ref not in seen:
                errors.append(f'constitution: broken hard-control reference {ref}')
    runtime = load('runtime/shared/v1.0/runtime.yaml')
    agent_ids = set()
    for agent in AGENTS:
        manifest = load(f'agents/{agent}/manifest.yaml')
        agent_ids.add(manifest.get('id'))
        if manifest.get('requires_runtime') != runtime.get('version'):
            errors.append(f'{agent}: invalid runtime dependency')
        permission = load(f'permissions/{agent}.yaml')
        if manifest.get('permission_profile_id') != permission.get('id') or permission.get('agent_id') != manifest.get('id'):
            errors.append(f'{agent}: broken permission reference')
        for key in ('domain_control_registry', 'output_contract'):
            load(manifest.get(key, '__missing_reference__'))
        if permission.get('grants') or permission.get('scope'):
            errors.append(f'{agent}: permission activation outside foundation scope')
    db_refs, connector_refs = set(), set()
    for env in ENVS:
        config = load(f'config/{env}/environment.yaml')
        if config.get('environment') != env:
            errors.append(f'{env}: invalid environment mapping')
        db = config.get('database_reference')
        connector = config.get('connector_reference')
        if db in db_refs or connector in connector_refs:
            errors.append(f'{env}: environment references must be independent')
        db_refs.add(db)
        connector_refs.add(connector)
    for path, kind in bindings.items():
        if kind != 'release':
            continue
        release = load(path)
        if release.get('system_version') != system_version:
            errors.append(f'{path}: release system version mismatch')
        entries = release.get('agents', [])
        if {x.get('id') for x in entries} != agent_ids or len(entries) != 6:
            errors.append(f'{path}: missing required package or duplicate Agent')
        for key in ('constitution', 'runtime', 'hard_controls', 'agents', 'permission_profiles',
                    'policies', 'decision_tables', 'workflows', 'connectors'):
            refs = release.get(key, [])
            for ref in refs if isinstance(refs, list) else [refs]:
                target = load(ref.get('path', '__missing_reference__'))
                if ref.get('version') != target.get('version'):
                    errors.append(f'{path}: release manifest version mismatch ({key})')
                if 'id' in ref and ref['id'] != target.get('id'):
                    errors.append(f'{path}: release manifest ID mismatch ({key})')
    return sorted(set(errors))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        failures = validate(args.root)
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        failures = [f'FAIL CLOSED: malformed configuration ({type(exc).__name__})']
    for failure in failures:
        print(f'FAIL: {failure}')
    print(f'Foundation validation: {"FAIL" if failures else "PASS"} ({len(failures)} errors)')
    raise SystemExit(bool(failures))
