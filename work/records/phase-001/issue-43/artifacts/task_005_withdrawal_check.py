import unittest
from pathlib import Path


class CatalogWithdrawalTest(unittest.TestCase):
    def test_catalog_sources_are_absent_and_common_error_remains(self):
        package = Path('java/io/github/minokim/lumiawiki')
        source = Path('backend/src')
        remaining = sorted(
            file.as_posix()
            for layer in ('main', 'test')
            for file in (source / layer / package / 'catalog').rglob('*.java')
        )
        self.assertEqual([], remaining, 'Catalog Java sources still participate in the build')

        api = (source / 'main' / package / 'common/api/ApiFailure.java').read_text(encoding='utf-8')
        self.assertNotIn('record Target(', api)
        self.assertNotIn('String operation', api)
        self.assertIn('record FieldError(', api)
        self.assertIn('invalidInput(String field)', api)
        self.assertIn('notFound()', api)
