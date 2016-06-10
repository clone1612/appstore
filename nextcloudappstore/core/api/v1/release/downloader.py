import requests
import uuid
import os


class MaximumDownloadSizeExceededException(Exception):
    pass


class ReleaseDownload:
    def __init__(self, filename):
        self.filename = filename

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.remove(self.filename)


class AppReleaseDownloader:
    def download_release(self, target_directory, url, timeout=60,
                         max_redirects=10, max_size=50 * (1024 ** 2)):
        """
        Downloads an app release from an url to a directory
        :argument target_directory directory where the downloaded archive
        should be saved, will be created if it does not exist yet
        :argument url to the archive
        :argument timeout maximum timeout in seconds
        :argument max_redirects number of maximum redirects to follow,
        defaults to 10
        :argument max_size how big the archive is allowed to be in bytes,
        defaults to 50Mb
        :raises MaximumDownloadSizeExceededException if the archive is bigger
        than allowed
        :raises requests.HttpError for non 2xx status codes
        :raises requests.ConnectionError for failed connections
        :raises requests.TooManyRedirects of too many redirects were made
        :return the path to the downloaded file
        """
        os.makedirs(target_directory, mode=0o755, exist_ok=True)

        unique_file_name = uuid.uuid4().hex
        filename = os.path.join(target_directory, unique_file_name)

        with requests.Session() as session:
            session.max_redirects = max_redirects
            req = session.get(url, stream=True, timeout=timeout)
            req.raise_for_status()
            if int(req.headers.get('Content-Length')) > max_size:
                raise MaximumDownloadSizeExceededException

            self._stream_to_file(filename, max_size, req)

        return ReleaseDownload(filename)

    def _stream_to_file(self, filename, max_size, req):
        # start streaming download
        finished = False
        try:
            with open(filename, 'wb') as fd:
                size = 0
                for chunk in req.iter_content(1024):
                    fd.write(chunk)
                    size += len(chunk)
                    if size > max_size:
                        raise MaximumDownloadSizeExceededException
            finished = True
        finally:
            # in case any errors occurred, get rid of the file
            if not finished:
                os.remove(filename)
