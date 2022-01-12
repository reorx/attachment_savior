import re
import traceback
import logging
from pathlib import Path
from mimetypes import guess_extension
from .http_util import get_response, save_response_to_file, DownloadError
from .log import lg


class Link:
    def __init__(self, url, title):
        self.url = url
        self.title = title
        self.filename = None
        self.success = False

    def download(self, download_dir, prefix):
        resp = get_response(self.url)
        if resp.status_code != 200:
            lg.error(f'http error: url={self.url} status={resp.status_code} body={resp.content[:500]}')
            raise DownloadError(f'Response status {resp.status_code}')

        content_type = resp.headers['content-type']
        lg.info(f'content-type: {content_type}')
        ext = guess_extension(content_type.partition(';')[0].strip())
        self.filename = f'{prefix}{ext}'
        save_response_to_file(resp, dir_path=download_dir, filename=self.filename, logger=lg)

    def to_wikilink(self):
        return f'![[{self.filename}]]'

class MarkdownHandler:
    link_regex = re.compile(r'!\[(.*)\]\((http.+)\)')

    def __init__(
        self,
        filename,
        download_dir,
        variant,
    ):
        self.path = Path(filename)
        self.download_dir = download_dir
        self.variant = variant
        self.links = []

    def process(self, backup_dir=None):
        with open(self.path) as f:
            content = f.read()

        processed = re.sub(self.link_regex, self.handle_link_match, content)
        #print(f'processed: {len(processed)}\n{processed}')

        if backup_dir:
            backup_path = Path(backup_dir).joinpath(self.path.name)
            print(f'save backup file: {backup_path}')
            with open(backup_path, 'w') as f:
                f.write(content)
        print('save markdown file')
        with open(self.path, 'w') as f:
            f.write(processed)

    def handle_link_match(self, matched: re.Match):
        sequence = len(self.links) + 1
        lg.debug(f'handle link {sequence}: {matched}')

        prefix = f'{self.path.stem}-{sequence}'
        link = Link(matched.group(2), matched.group(1))
        self.links.append(link)

        try:
            link.download(self.download_dir, prefix)
        except Exception:
            traceback.print_exc()
            link.success = False
            return matched.group()

        link.success = True
        return link.to_wikilink()
