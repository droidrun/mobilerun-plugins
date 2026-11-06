"""Export Test Plugin's runtime package with the local stdio bridge and no credentials."""
import argparse
from pathlib import Path
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.sync_skills import check as check_shared_skills
from scripts.sync_skills import _regular_file, _replace_section
DISTRIBUTION_FILES = (
    'plugin.json', 'mcp.json', 'README.md', 'LICENSE',
    'scripts/local-mcp.mjs', 'scripts/setup-local-auth.mjs',
    'skills/onboarding/SKILL.md', 'skills/mobile-tasks/SKILL.md',
)


def package_plugin(package: Path, destination: Path) -> None:
    package = Path(package).absolute()
    destination = Path(destination).absolute()
    if package.is_symlink():
        raise ValueError('Plugin directory must not be a symlink')
    contents = {}
    # Validate and read every allowlisted file before touching an existing ZIP.
    for name in DISTRIBUTION_FILES:
        path = package / name
        if any(part.is_symlink() for part in (path, *path.parents)
               if part == package or package in part.parents):
            raise ValueError(f'Refusing symlinked distribution file: {name}')
        if not path.is_file() or not path.resolve().is_relative_to(package.resolve()):
            raise ValueError(f'Missing regular distribution file: {name}')
        data = path.read_bytes()
        if not data:
            raise ValueError(f'Empty distribution file: {name}')
        contents[name] = data
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, prefix='.test-plugin-', suffix='.zip', delete=False) as file:
        temporary = Path(file.name)
    try:
        with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
            for name, data in contents.items():
                entry = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
                entry.compress_type = zipfile.ZIP_DEFLATED
                entry.external_attr = 0o100644 << 16
                archive.writestr(entry, data)
        with zipfile.ZipFile(temporary) as archive:
            if archive.testzip() is not None:
                raise ValueError('ZIP integrity check failed')
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=ROOT / 'plugins/test-plugin')
    parser.add_argument('--output', type=Path, default=ROOT / 'zip/test-plugin.zip')
    args = parser.parse_args(argv)
    try:
        pending = check_shared_skills(ROOT)
    except (OSError, ValueError) as error:
        print(f'Shared skill check failed: {error}', file=sys.stderr)
        return 1
    if pending:
        print('Shared skills are out of sync; run python3 scripts/sync_skills.py', file=sys.stderr)
        return 1
    try:
        onboarding = _regular_file(args.package, 'skills/onboarding/SKILL.md').read_text()
        canonical = _regular_file(ROOT, 'shared/onboarding-first-device.md').read_text()
        if onboarding != _replace_section(onboarding, canonical, str(args.package)):
            raise ValueError('Selected package shared skills are out of sync')
        for skill in ('mobile-tasks',):
            content = _regular_file(args.package, f'skills/{skill}/SKILL.md').read_text()
            expected = _regular_file(ROOT, f'shared/skills/{skill}/SKILL.md').read_text()
            if content != expected:
                raise ValueError('Selected package shared skills are out of sync')
    except (OSError, ValueError) as error:
        print(f'Shared skill check failed: {error}', file=sys.stderr)
        return 1
    package_plugin(args.package, args.output)
    print(f'Built {args.output.name}: {len(DISTRIBUTION_FILES)} runtime files, {args.output.stat().st_size:,} bytes')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
