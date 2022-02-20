#!/usr/bin/env python3
import click
import os
import glob
import subprocess
import time
from hashlib import sha1
import json

commands = {
    '.cpp': 'g++ {filename} -o {runame} -O2 -Wall -static -std=gnu++20 -Wfatal-errors',
    '.py': 'echo "#!/usr/bin/env python3" > {runame};'
        'cat {filename} >> {runame};chmod u+x {runame};'
        'python3 -c "import py_compile; py_compile.compile(\'{runame}\')"'
}

def compile(filename):
    # Prepare
    name, ext = os.path.splitext(filename)
    tmpdir = os.path.join(os.path.dirname(filename), '.tmp/')
    if not os.path.exists(tmpdir):
        os.mkdir(tmpdir)
    if ext not in commands:
        raise click.ClickException(f'Cannot find compile command ({ext})')

    # Hash
    with open(filename, 'rb') as f:
        data = f.read()
        h = sha1(data).hexdigest()
    runame = os.path.join(tmpdir, name + '_' + h[:6])

    if os.path.exists(runame):
        click.echo('Skipping Compile')
        return runame

    # Compile
    command = commands[ext].format(filename=filename, runame=runame)
    click.echo(command)
    return_code = os.system(command)
    if return_code != 0:
        raise click.ClickException('Compile Failed.')
    return runame


@click.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--testcase-directory', '-tc', default='testcase', type=click.Path(),
              help='testcase directory')
@click.option('--no-subdirectory', '-N', is_flag = True,
              help='directly find TCs in "testcase-directory/"' +
              '\ndefault is "testcase-directory/{filename}"')
@click.option('--runtime', '-r', is_flag=True, help='Ignore testcase, write data manually')
@click.option('--timelimit', '-t', default=3, help='time limit')
def run(filename, testcase_directory, no_subdirectory, runtime, timelimit):
    """Simple Judge Tool"""
    runame = compile(filename)

    name, ext = os.path.splitext(filename)

    if '_' in name:
        name = name[:name.find('_')]
    if not no_subdirectory:
        testcase_directory = os.path.join(testcase_directory, name)
    testcase_directory.rstrip('/')
    testcase_directory += '/'

    input_paths = sorted(glob.glob(f'{testcase_directory}/*.in'))
    if not runtime and len(input_paths) == 0:
        click.secho('No input data!', fg='bright_red')
        runtime = True
    if runtime:
        click.secho(f'Runtime Mode ({runame})', fg='bright_cyan')
        os.system(runame)
        return

    maxtime = 0
    align_length = max([len(s) for s in input_paths]) - len(testcase_directory) - 3
    wa_list = []
    for input_path in input_paths:
        output_path = input_path[:-3] + '.out'
        answer_path = input_path[:-3] + '.ans'
        tc_name = input_path[len(testcase_directory):-3]
        click.echo(tc_name.rjust(align_length) + ' ', nl=False)
        start_time = time.time_ns()
        with open(input_path, 'r') as input_file, open(output_path, 'w') as output_file:
            try:
                result = subprocess.run([runame], stdin=input_file, stdout=output_file, timeout=timelimit)
            except subprocess.TimeoutExpired:
                maxtime = timelimit * 1000
                click.secho('TLE', fg='bright_red')
                continue
        tc_time = (time.time_ns() - start_time) // 1000000
        maxtime = max(maxtime, tc_time)
        if result.returncode != 0:
            click.secho('RTE ', fg='bright_blue', nl=False)
        elif not os.path.isfile(answer_path):
            click.secho('? (no ans data)', fg='bright_black', nl=False)
        elif os.system(f'diff -wB {output_path} {answer_path} > /dev/null') != 0:
            click.secho('WA  ', fg='bright_red', nl=False)
            wa_list.append(tc_name)
        else:
            click.secho('AC  ', fg='bright_green', nl=False)
        click.echo(f'{tc_time}ms')
    click.secho(f'Maximum Time: {maxtime}ms', fg='bright_white')

    recent_path = os.path.join(os.path.dirname(filename), '.tmp/recent')
    recent = {
        'problem_name': name,
        'testcase_directory': os.path.abspath(testcase_directory),
        'wa_list': wa_list,
    }
    with open(recent_path, 'w') as f:
        json.dump(recent, f)


if __name__ == '__main__':
    run()
