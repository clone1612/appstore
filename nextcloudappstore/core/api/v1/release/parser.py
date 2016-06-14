from lxml import etree
from lxml.etree import DocumentInvalid
import tarfile


class InvalidAppMetadataXmlException(Exception):
    pass


class UnsupportedAppArchiveException(Exception):
    pass


class InvalidAppPackageStructureException(Exception):
    pass


class GunZipAppMetadataExtractor:
    def extract_app_metadata(self, archive_path, app_id):
        """
        Extracts the info.xml from an tar.gz archive
        :argument archive_path the path to the tar.gz archive
        :argument app_id the app id
        :raises InvalidAppPackageStructureException if the first level folder
        does not equal the app_id or no info.xml file could be found in the
        appinfo folder
        :return the info.xml as string
        """
        if not tarfile.is_tarfile(archive_path):
            msg = '%s is not a valid tar.gz archive ' % archive_path
            raise UnsupportedAppArchiveException(msg)

        with tarfile.open(archive_path, 'r:gz') as tar:
            result = self._parse_archive(tar, app_id)
        return result

    def _parse_archive(self, tar, app_id):
        info_path = '%s/appinfo/info.xml' % app_id
        try:
            info_member = tar.getmember(info_path)
            if info_member.issym() or info_member.islnk():
                msg = 'Symlinks and hard links can not be used for info.xml ' \
                      'files'
                raise InvalidAppPackageStructureException(msg)
            info_file = tar.extractfile(info_member)
            return info_file.read().decode('utf-8')
        except KeyError:
            msg = 'Could not find %s file inside the archive' % info_path
            raise InvalidAppPackageStructureException(msg)

def element_to_dict(element):
    type = element.get('type')
    if type == 'list':
        contents = list(map(element_to_dict, element.iterchildren()))
    elif type == 'l10n':
        lang = element.find('lang').text
        value = element.find('value').text
        contents = {
            lang: value
        }
    elif len(list(element)) > 0:
        contents = {}
        for child in element.iterchildren():
            contents.update(element_to_dict(child))
    else:
        contents = element.text
    return {
        element.tag.replace('-', '_'): contents
    }


def parse_app_metadata(xml, schema, xslt):
    """
    Parses, validates and maps the xml onto a dict
    :argument xml the info.xml string to parse
    :argument schema the schema xml as string
    :argument xslt the xslt to transform it to a matching structure
    :raises InvalidAppMetadataXmlException if the schema does not validate
    :return the parsed xml as dict
    """
    parser = etree.XMLParser(resolve_entities=False, no_network=True,
                             remove_comments=True, remove_blank_text=True)
    schema_doc = etree.fromstring(bytes(schema, encoding='utf-8'), parser)
    doc = etree.fromstring(bytes(xml, encoding='utf-8'), parser)
    schema = etree.XMLSchema(schema_doc)
    try:
        schema.assertValid(doc)
    except DocumentInvalid as e:
        raise InvalidAppMetadataXmlException(e)
    transform = etree.XSLT(etree.XML(xslt))
    transformed_doc = transform(doc)
    mapped = element_to_dict(transformed_doc.getroot())
    return mapped
