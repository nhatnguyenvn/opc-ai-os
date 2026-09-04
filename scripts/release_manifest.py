"""Generate a commit-bound local build manifest, never a production approval."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from validate import ROOT, read, validate


def generate(root=ROOT):
    errors = validate(root)
    if errors:
        raise ValueError('Foundation validation failed; manifest generation blocked')
    def git(*args):
        return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()
    if git('status', '--porcelain'):
        raise ValueError('Clean committed checkout required')
    commit = git('rev-parse', 'HEAD')
    manifest = read(root / 'release/manifest.template.yaml')
    manifest.update(status='BUILD_ONLY_NOT_DEPLOYABLE', build_commit=commit)
    manifest['artifact_hashes'] = {
        path: hashlib.sha256((root / path).read_bytes()).hexdigest()
        for path in git('ls-files').splitlines()
        if not path.startswith('release/manifests/')
    }
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    try:
        manifest = generate()
        if args.output.exists():
            raise ValueError('Refusing to overwrite an existing artifact')
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        print(f'Build-only manifest generated for {manifest["build_commit"]}')
    except (ValueError, subprocess.CalledProcessError) as exc:
        print(f'BLOCKED: {exc}')
        raise SystemExit(1)
