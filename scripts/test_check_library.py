from pathlib import Path
import tempfile
import unittest
from check_library import validate


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'prompts').mkdir()
        (self.root / 'README.md').write_text('[Sample](prompts/Sample.md)')
        (self.root / 'prompts/Sample.md').write_text('# Sample\n\n```text\nBuild a page.\n```\n')

    def test_valid(self):
        self.assertEqual(validate(self.root), [])

    def test_missing_file(self):
        (self.root / 'prompts/Sample.md').unlink()
        self.assertIn('missing prompt file: prompts/Sample.md', validate(self.root))

    def test_unlisted_prompt(self):
        (self.root / 'README.md').write_text('Gallery')
        self.assertIn('prompt missing from gallery: prompts/Sample.md', validate(self.root))

    def test_duplicate(self):
        with (self.root / 'README.md').open('a') as file:
            file.write('\n[Again](prompts/Sample.md)')
        self.assertIn('duplicate gallery link: prompts/Sample.md', validate(self.root))

    def test_wrong_declared_count(self):
        with (self.root / 'README.md').open('a') as file:
            file.write('\n65 Premium Prompts')
        self.assertIn('declared prompt count 65 differs from 1 files', validate(self.root))

    def test_empty_prompt(self):
        (self.root / 'prompts/Sample.md').write_text('# Sample\n```text\n\n```')
        self.assertIn('missing nonempty prompt block: prompts/Sample.md', validate(self.root))

    def test_hls_type(self):
        with (self.root / 'prompts/Sample.md').open('a') as file:
            file.write('<source src="https://example.test/video.m3u8" type="video/mp4">')
        self.assertIn('incorrect HLS source type: prompts/Sample.md', validate(self.root))


if __name__ == '__main__':
    unittest.main()
