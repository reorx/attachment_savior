import os
import click
import logging
from .markdown import MarkdownHandler
from .log import lg, cli_lg


logging.basicConfig(level=logging.INFO)
lg.setLevel(logging.DEBUG)

backup_dir = os.environ.get('AS_BACKUP_DIR')


@click.group()
@click.option('--debug', is_flag=True)
def cli(debug):
    pass


@cli.command()
@click.argument('filenames', nargs=-1)
@click.option('--variant', '-x', default='obsidian', help='variant type of markdown, supports: obsidian')
@click.option('--download-dir', '-d', default='attachments', help='directory to download attachments')
def markdown(filenames, variant, download_dir):
    if not filenames:
        print('No filenames passed')
    for fn in filenames:
        cli_lg.info(f'markdown: filename={fn}')
        handler = MarkdownHandler(
            filename=fn,
            download_dir=download_dir,
            variant=variant,
        )
        handler.process(backup_dir)


@cli.command()
def dropdb():
    click.echo('Dropped the database')


if __name__ == '__main__':
    cli()
