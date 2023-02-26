import click
from solve.subs.run import run
from solve.subs.get import get
from solve.subs.diff import diff
from solve.subs.tc import tc

@click.group()
def cli():
    pass

cli.add_command(run)
cli.add_command(get)
cli.add_command(diff)
cli.add_command(tc)
cli()