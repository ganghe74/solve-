#!/usr/bin/env python3
import click
import glob
import requests
import re
import os
from bs4 import BeautifulSoup

sources = {
    'boj': {
        'url': 'https://acmicpc.net/problem/%s',
        'input': {'id':re.compile('sample-input-\d*')},
        'ans': {'id':re.compile('sample-output-\d*')}
    }
}

def guess_src(src):
    for key, val in sources.items():
        if key.startswith(src):
            return val
    raise click.ClickException('Invalid source ' + src)

@click.command()
@click.argument('source', nargs=1)
@click.argument('problem')
@click.option('--testcase-directory', '-tc', default='testcase', type=click.Path(),
              help='testcase directory')
@click.option('--no-subdirectory', '-N', is_flag = True,
              help='directly find TCs in "testcase-directory/"' +
              '\ndefault is "testcase-directory/{filename}"')
def get(source, problem, testcase_directory, no_subdirectory):
    """Fetch testcase"""
    src = guess_src(source)
    problem = re.sub('(_.*)|(\..*)', '', problem)
    webpage = requests.get(src['url']%problem)
    soup = BeautifulSoup(webpage.content, 'html.parser')
    INS = soup.find_all(attrs=src['input'])
    ANS = soup.find_all(attrs=src['ans'])

    if len(INS) == 0:
        raise click.ClickException('Cannot find testcases from ' + src['url']%problem)

    if not no_subdirectory:
        testcase_directory = os.path.join(testcase_directory, problem)
    testcase_directory.rstrip('/')
    testcase_directory += '/'
    if not os.path.exists(testcase_directory):
        os.makedirs(testcase_directory)

    for i, IN, AN in zip(map(str,range(1,len(INS)+1)), INS, ANS):
        with open(testcase_directory + str(i) + '.in', 'w') as f:
            f.write(IN.text.strip().replace('\r',''))
        with open(testcase_directory + str(i) + '.ans', 'w') as f:
            f.write(AN.text.strip().replace('\r',''))
    click.echo(f'Successfully crawled {len(INS)} testcases')

if __name__ == '__main__':
    get()
