import click
from subs.run import run
from subs.get import get

@click.group()
def solve():
    pass

if __name__ == '__main__':
    solve.add_command(run)
    solve.add_command(get)
    solve()
