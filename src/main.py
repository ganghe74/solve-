import click
from src.subs.run import run
from src.subs.get import get
from src.subs.diff import diff

@click.group()
def cli():
    pass

cli.add_command(run)
cli.add_command(get)
cli.add_command(diff)
cli()
