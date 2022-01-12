import os
import requests


default_headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36',
    'Connection': 'keep-alive',
}


class DownloadError(Exception):
    pass


def get_response(url, headers=None):
    new_headers = dict(default_headers)
    if headers:
        new_headers.update(headers)
    resp = requests.get(url, headers=new_headers)
    return resp


def save_response_to_file(resp: requests.Response, file_path=None, dir_path=None, filename=None, mode='wb', stream=False, block_size=1024 * 512, logger=None):
    if not file_path and not dir_path:
        raise ValueError('file_path and dir_path must have at least one')
    if not file_path:
        file_path = os.path.join(dir_path, filename)
    if logger:
        logger.info(f'save response to {file_path}')
    with open(file_path, mode) as f:
        if stream:
            for block in resp.iter_content(block_size):
                f.write(block)
        else:
            f.write(resp.content)
