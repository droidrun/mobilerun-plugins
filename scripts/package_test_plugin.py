"""Export Test Plugin's hosted-profile package, excluding legacy local build files."""
import argparse
from pathlib import Path
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DISTRIBUTION_FILES = (
    'plugin.json', 'mcp.json', 'README.md', 'LICENSE',
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', type=Path, default=ROOT / 'plugins/test-plugin')
    parser.add_argument('--output', type=Path, default=ROOT / 'zip/test-plugin.zip')
    args = parser.parse_args()
    package_plugin(args.package, args.output)
    print(f'Built {args.output.name}: {len(DISTRIBUTION_FILES)} runtime files, {args.output.stat().st_size:,} bytes')
