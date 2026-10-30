#!/usr/bin/env python3
"""Validate prompt discoverability and preview metadata without dependencies."""

from collections import Counter
from pathlib import Path
import re
import sys


def validate(root: Path) -> list[str]:
    readme = (root / 'README.md').read_text(encoding='utf-8')
    paths = re.findall(r'\]\((prompts/[^)]+\.md)\)', readme)
    existing = {str(path.relative_to(root)) for path in (root / 'prompts').glob('*.md')}
    errors = []
    for path, count in Counter(paths).items():
        if count > 1:
            errors.append(f'duplicate gallery link: {path}')
    for path in sorted(set(paths) - existing):
        errors.append(f'missing prompt file: {path}')
    for path in sorted(existing - set(paths)):
        errors.append(f'prompt missing from gallery: {path}')
    if not existing:
        errors.append('no prompt files found')
    declared = re.findall(r'\b(\d+)\s+(?:high-quality AI web design prompts|Premium Prompts|documented design prompts)', readme)
    for count in declared:
        if int(count) != len(existing):
            errors.append(f'declared prompt count {count} differs from {len(existing)} files')
    for path in sorted(existing):
        text = (root / path).read_text(encoding='utf-8')
        if not re.search(r'^#\s+\S', text, re.MULTILINE):
            errors.append(f'missing title: {path}')
        if not re.search(r'```text\s*\n\s*\S[\s\S]*?\n```', text):
            errors.append(f'missing nonempty prompt block: {path}')
        for source in re.findall(r'<source\b[^>]*>', text):
            src = re.search(r'src="([^"]+)"', source)
            if src and src.group(1).split('?')[0].endswith('.m3u8'):
                if 'type="application/vnd.apple.mpegurl"' not in source:
                    errors.append(f'incorrect HLS source type: {path}')
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors = validate(root)
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'Validated {len(list((root / "prompts").glob("*.md")))} prompts and gallery links.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
