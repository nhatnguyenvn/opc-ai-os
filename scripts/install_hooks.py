"""Install or verify checkout-local accident prevention; never global config."""
import argparse
import hashlib
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def inspect(root=ROOT):
    configured = subprocess.run(['git', '-C', str(root), 'config', '--local', '--get',
                                 'core.hooksPath'], capture_output=True, text=True)
    hook = root / '.githooks/pre-push'
    tracked = subprocess.run(['git', '-C', str(root), 'show', 'HEAD:.githooks/pre-push'],
                             capture_output=True)
    if configured.stdout.strip() != '.githooks' or not hook.is_file():
        raise ValueError('Missing checkout hook installation')
    if tracked.returncode or hook.read_bytes() != tracked.stdout:
        raise ValueError('Hook differs from committed version or is not committed')
    return hashlib.sha256(hook.read_bytes()).hexdigest()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--install', action='store_true')
    args = parser.parse_args()
    if args.install:
        old = subprocess.run(['git', '-C', str(ROOT), 'config', '--get', 'core.hooksPath'],
                             capture_output=True, text=True).stdout.strip()
        if old and old != '.githooks':
            raise SystemExit('HOLD: existing hook configuration requires explicit integration')
        subprocess.run(['git', '-C', str(ROOT), 'config', '--local', 'core.hooksPath',
                        '.githooks'], check=True)
    try:
        print('Hook installation PASS; SHA256=' + inspect())
    except ValueError as exc:
        raise SystemExit('HOLD: ' + str(exc))
