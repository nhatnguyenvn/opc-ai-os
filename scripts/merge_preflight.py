"""Read-only assessment of retained evidence, not a live GitHub authorization API.

PASS means snapshot consistency only. The operator must retrieve fresh evidence
from GitHub and recheck immediately before merging; this tool cannot enforce it.
"""
import argparse
import json
import re
from pathlib import Path

REPOSITORY = 'nhatnguyenvn/opc-ai-os'


def assess(evidence, approval):
    errors = []
    for field in ('head_sha', 'base_sha', 'merge_sha'):
        if not re.fullmatch(r'[0-9a-f]{40}', str(evidence.get(field, ''))):
            errors.append('invalid ' + field)
    if evidence.get('repository') != REPOSITORY:
        errors.append('wrong repository')
    if evidence.get('state') != 'OPEN' or evidence.get('draft') is not False:
        errors.append('PR not ready')
    if evidence.get('base_ref') != 'main' or evidence.get('mergeable') != 'MERGEABLE':
        errors.append('base or conflicts unresolved')
    if evidence.get('unresolved_threads') != 0 or evidence.get('review_query_complete') is not True:
        errors.append('review evidence incomplete')
    if evidence.get('retrieval_complete') is not True:
        errors.append('API evidence incomplete')
    checks = evidence.get('checks', [])
    valid = [c for c in checks if c.get('name') == 'foundation'
             and c.get('app_slug') == 'github-actions'
             and c.get('head_sha') == evidence.get('merge_sha')
             and c.get('event') == 'pull_request'
             and c.get('workflow_path') == '.github/workflows/validate.yml']
    if len(valid) != 1 or valid[0].get('conclusion') != 'success' or valid[0].get('status') != 'completed':
        errors.append('required CI missing, ambiguous or unsuccessful')
    for field in ('repository', 'pr_number', 'head_sha', 'base_sha'):
        if approval.get(field) != evidence.get(field) or not evidence.get(field):
            errors.append('approval mismatch: ' + field)
    if approval.get('decision') != 'APPROVED' or not approval.get('source_reference'):
        errors.append('Founder approval missing')
    if approval.get('accepts_a1_3_exception') is not True or approval.get('merge_method') != 'merge':
        errors.append('approval scope incomplete')
    return {'status': 'HOLD' if errors else 'SNAPSHOT_PASS_REQUIRES_LIVE_RECHECK',
            'errors': errors, 'head_sha': evidence.get('head_sha'), 'base_sha': evidence.get('base_sha')}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--approval', type=Path, required=True)
    args = parser.parse_args()
    try:
        result = assess(json.loads(args.evidence.read_text(encoding='utf-8')),
                        json.loads(args.approval.read_text(encoding='utf-8')))
    except (OSError, ValueError, TypeError, AttributeError):
        result = {'status': 'HOLD', 'errors': ['Unreadable or malformed evidence']}
    print(json.dumps(result))
    raise SystemExit(0 if result['status'].startswith('SNAPSHOT_PASS') else 1)
