from django.test import TestCase
from nextcloudappstore.core.api.v1.release.parser import \
    parse_app_metadata, GunZipAppMetadataExtractor, \
    InvalidAppPackageStructureException, \
    UnsupportedAppArchiveException, InvalidAppMetadataXmlException
from nextcloudappstore.core.facades import resolve_file_relative_path, \
    read_file_contents


class ParserTest(TestCase):
    def setUp(self):
        schema_file = self.get_path('../release/info.xsd')
        self.schema = read_file_contents(schema_file)
        xslt_file = self.get_path('../release/info.xslt')
        self.xslt = read_file_contents(xslt_file)
        self.maxDiff = None

    def test_parse_minimal(self):
        xml = self._get_test_xml('data/infoxmls/minimal.xml')
        result = parse_app_metadata(xml, self.schema, self.xslt)
        expected = {'app': {
            'id': 'news',
            'description': {'en': 'An RSS/Atom feed reader'},
            'name': {'en': 'News'},
            'admin_docs': None,
            'developer_docs': None,
            'user_docs': None,
            'website': None,
            'issue_tracker': None,
            'screenshots': [],
            'categories': [{'category': {'id': 'multimedia'}}],
            'release': {
                'authors': [{'author': {
                    'homepage': None,
                    'mail': None,
                    'name': 'Bernhard Posselt'
                }}],
                'databases': [{'database_dependencies': []}],
                'licenses': [{'license': {'id': 'agpl'}}],
                'min_int_size': None,
                'php_extensions': [{'php_extension_dependencies': []}],
                'php_max_version': None,
                'php_min_version': None,
                'platform_max_version': None,
                'platform_min_version': '9.0',
                'shell_commands': [],
                'version': '8.8.2'
            }
        }}
        self.assertDictEqual(expected, result)

    def test_validate_schema(self):
        xml = self._get_test_xml('data/infoxmls/invalid.xml')
        with (self.assertRaises(InvalidAppMetadataXmlException)):
            parse_app_metadata(xml, self.schema, self.xslt)

    def test_extract_gunzip_info(self):
        path = self.get_path('data/archives/full.tar.gz')
        extractor = GunZipAppMetadataExtractor()
        full_extracted = extractor.extract_app_metadata(path, 'news')
        full = self._get_test_xml('data/infoxmls/full.xml')
        self.assertEqual(full, full_extracted)

    def test_extract_gunzip_info_wrong_app_folder(self):
        path = self.get_path('data/archives/full.tar.gz')
        extractor = GunZipAppMetadataExtractor()
        with (self.assertRaises(InvalidAppPackageStructureException)):
            extractor.extract_app_metadata(path, 'newss')

    def test_extract_gunzip_no_appinfo(self):
        path = self.get_path('data/archives/invalid.tar.gz')
        extractor = GunZipAppMetadataExtractor()
        with (self.assertRaises(InvalidAppPackageStructureException)):
            extractor.extract_app_metadata(path, 'news')

    def test_extract_gunzip_symlink(self):
        path = self.get_path('data/archives/symlink.tar.gz')
        extractor = GunZipAppMetadataExtractor()
        with (self.assertRaises(InvalidAppPackageStructureException)):
            extractor.extract_app_metadata(path, 'news')

    def test_extract_zip(self):
        path = self.get_path('data/archives/empty.zip')
        extractor = GunZipAppMetadataExtractor()
        with (self.assertRaises(UnsupportedAppArchiveException)):
            extractor.extract_app_metadata(path, 'news')

    def test_map_data(self):
        full = self._get_test_xml('data/infoxmls/full.xml')
        result = parse_app_metadata(full, self.schema, self.xslt)
        data = ''  # dict_to_data(result)
        release = {
            'version': '8.8.2',
            'licenses': [{'id': 'agpl'}, {'id': 'mit'}],
            'authors': [
                {
                    'name': 'Bernhard Posselt',
                    'homepage': 'http://example.com',
                    'mail': 'mail@provider.com'
                },
                {'name': 'Alessandro Cosentino'},
                {'name': 'Jan-Christoph Borchardt'}
            ],
            'screenshots': [
                {'url': 'https://example.com/1.png', 'order': 0},
                {'url': 'https://example.com/2.png', 'order': 1},
            ],
            'libs': [{'id': 'curl'}, {'id': 'iconv'}, {'id': 'SimpleXML'},
                     {'id': 'libxml', 'min_version': '2.7.8'}],
            'databases': [{'id': 'sqlite'},
                          {'id': 'pgsql', 'min_version': '9.4'},
                          {'id': 'mysql', 'min_version': '5.5'}],
            'shell_commands': ['grep', 'ls'],
            'php_min_version': '5.6',
            'platform_min_version': '9.0',
            'platform_max_version': '9.1',
            'min_int_size': '64',
        }
        expected = {
            'id': 'news',
            'translations': {
                'de': {
                    'name': 'Nachrichten',
                    'description': 'Eine Nachrichten App, welche mit ['
                                   'RSS/Atom]('
                                   'https://en.wikipedia.org/wiki/RSS) '
                                   'umgehen kann'
                },
                'en': {
                    'name': 'News',
                    'description': 'An RSS/Atom feed reader'
                }
            },
            'user_docs': 'https://github.com/owncloud/news/wiki#user'
                         '-documentation',
            'admin_docs': 'https://github.com/owncloud/news#readme',
            'developer_docs':
                'https://github.com/owncloud/news/wiki#developer'
                '-documentation',
            'issue_tracker': 'https://github.com/owncloud/news/issues',
            'website': 'https://github.com/owncloud/news',
            'categories': [{'id': 'multimedia'}, {'id': 'tools'}],
            'release': release
        }
        self.assertDictEqual(expected, data)

    def _get_test_xml(self, target):
        path = self.get_path(target)
        return read_file_contents(path)

    def get_path(self, target):
        return resolve_file_relative_path(__file__, target)
