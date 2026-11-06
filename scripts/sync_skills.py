"""Synchronize canonical shared skill content into installable provider bundles."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PROVIDERS = ('claude', 'openai', 'cursor', 'openclaw', 'test-plugin')
SKILLS = ('mobile-tasks',)
START = '<!-- BEGIN SHARED FIRST DEVICE -->'
END = '<!-- END SHARED FIRST DEVICE -->'


def _regular_file(root: Path, relative: str) -> Path:
    """Resolve a package-relative regular file while rejecting symlinks in its path."""
    root = Path(root).absolute()
    path = root / relative
    if root.is_symlink():
        raise ValueError(f'Refusing symlink root: {root}')
    current = root
    for part in Path(relative).parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f'Refusing symlink path: {current}')
    if not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'Expected regular file inside package: {path}')
    return path


def _replace_section(text: str, canonical: str, target: str) -> str:
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError(f'{target}: expected exactly one shared-section marker pair')
    start = text.index(START)
    end = text.index(END)
    if end < start:
        raise ValueError(f'{target}: shared-section markers are out of order')
    end += len(END)
    replacement = f'{START}\n{canonical.strip()}\n{END}'
    return text[:start] + replacement + text[end:]


def synchronize(root: Path = ROOT, check: bool = False, providers=PROVIDERS) -> list[str]:
    root = Path(root).absolute()
    shared_onboarding = _regular_file(root, 'shared/onboarding-first-device.md').read_text()
    canonical_skills = {
        name: _regular_file(root, f'shared/skills/{name}/SKILL.md').read_text()
        for name in SKILLS
    }
    pending = []
    updates = []
    for provider in providers:
        onboarding_rel = f'plugins/{provider}/skills/onboarding/SKILL.md'
        onboarding_path = _regular_file(root, onboarding_rel)
        skills_dir = root / 'plugins' / provider / 'skills'
        for ancestor in (root / 'plugins', root / 'plugins' / provider, skills_dir):
            if ancestor.is_symlink():
                raise ValueError(f'Refusing symlink path: {ancestor}')
        updated = _replace_section(onboarding_path.read_text(), shared_onboarding, onboarding_rel)
        if updated != onboarding_path.read_text():
            pending.append(onboarding_rel)
            updates.append((onboarding_path, updated))
        for name, canonical in canonical_skills.items():
            relative = f'plugins/{provider}/skills/{name}/SKILL.md'
            target = skills_dir / name / 'SKILL.md'
            skill_dir = target.parent
            if skill_dir.is_symlink():
                raise ValueError(f'Refusing symlink path: {skill_dir}')
            if target.exists() or target.is_symlink():
                target = _regular_file(root, relative)
            if not target.is_file() or target.read_text() != canonical:
                pending.append(relative)
                updates.append((target, canonical))
    if not check:
        for path, content in updates:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
    return pending


def check(root: Path = ROOT, providers=PROVIDERS) -> list[str]:
    """Return stale files without changing any provider package."""
    return synchronize(root, check=True, providers=providers)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='fail if any provider copy is out of sync')
    args = parser.parse_args(argv)
    try:
        pending = synchronize(ROOT, check=args.check)
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    if pending:
        print(('Out of sync: ' if args.check else 'Updated: ') + ', '.join(pending), file=sys.stderr if args.check else sys.stdout)
        return int(args.check)
    print('Shared skills are synchronized.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
