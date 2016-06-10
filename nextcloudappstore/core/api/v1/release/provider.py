from nextcloudappstore.core.api.v1.release.downloader import \
    AppReleaseDownloader
from nextcloudappstore.core.api.v1.release.parser import \
    GunZipAppMetadataExtractor, parse_app_metadata
from nextcloudappstore.core.facades import resolve_file_relative_path


class AppReleaseProvider:
    def __init__(self):
        self.downloader = AppReleaseDownloader()
        self.extractor = GunZipAppMetadataExtractor()
        schema = 'release/platform/10.0/info.xsd'
        self.schema_file = resolve_file_relative_path(__file__, schema)

    def get_release_info(self, app, version, url, tmp_dir):
        with self.downloader.download_release(url, tmp_dir) as download:
            xml = self.extractor.extract_app_metadata(download.filename, app)
            info = parse_app_metadata(xml, self.schema_file)
        return info
