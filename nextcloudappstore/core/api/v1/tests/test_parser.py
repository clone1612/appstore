from django.test import TestCase
from nextcloudappstore.core.api.v1.release.parser import \
    parse_app_metadata, GunZipAppMetadataExtractor, \
    InvalidAppPackageStructureException, \
    UnsupportedAppArchiveException, InvalidAppMetadataXmlException, \
    dict_to_data
from nextcloudappstore.core.facades import resolve_file_relative_path, \
    read_file_contents


class ParserTest(TestCase):
    def setUp(self):
        schema_file = self.get_path('../release/info.xsd')
        self.schema = read_file_contents(schema_file)

    def test_parse_minimal(self):
        xml = self._get_test_xml('data/infoxmls/minimal.xml')
        result = parse_app_metadata(xml, self.schema)
        expected = [
            {'children': [], 'tag': 'id', 'text': 'news'},
            {'children': [], 'tag': 'name', 'text': 'News'},
            {'children': [], 'tag': 'description',
             'text': 'An RSS/Atom feed reader'},
            {'children': [], 'tag': 'version', 'text': '8.8.2'},
            {'children': [], 'tag': 'licence', 'text': 'agpl'},
            {'children': [], 'tag': 'author', 'text': 'Bernhard Posselt'},
            {'children': [], 'tag': 'category', 'text': 'multimedia'},
            {'tag': 'dependencies', 'text': None, 'children': [
                {'@min-version': '9.0', 'children': [], 'tag': 'owncloud',
                 'text': None}
            ]}
        ]
        self.assertListEqual(expected, result)

    def test_validate_schema(self):
        xml = self._get_test_xml('data/infoxmls/invalid.xml')
        with (self.assertRaises(InvalidAppMetadataXmlException)):
            parse_app_metadata(xml, self.schema)

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
        result = parse_app_metadata(full, self.schema)
        data = dict_to_data(result)
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
