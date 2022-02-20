#!/usr/bin/env python3
import click
import os
import glob
import subprocess
import time

commands = {
    'cpp': 'g++ %s -o run -O2 -Wall -static -std=gnu++20 -Wfatal-errors',
    'py': 'echo "#!/usr/bin/env python3" > run; cat %s >> run; chmod u+x run; python3 -c "import py_compile; py_compile.compile(\'run\')"'
}

@click.command()
@click.argument('filename', type=click.Path(exists=True))
@click.option('--testcase-directory', '-tc', default='testcase', type=click.Path(),
              help='testcase directory')
@click.option('--no-subdirectory', '-N', is_flag = True,
              help='directly find TCs in "testcase-directory/"' +
              '\ndefault is "testcase-directory/{filename}"')
@click.option('--runtime', '-r', is_flag=True, help='Ignore testcase, you write data manually')
@click.option('--timelimit', '-t', default=3, help='time limit')
def solve(filename, testcase_directory, no_subdirectory, runtime, timelimit):
    """Simple Judge Tool"""
    src_mtime = os.stat(filename).st_mtime
    bin_mtime = os.stat('run').st_mtime if os.path.isfile('run') else 0
    name, ext = os.path.splitext(filename)
    ext = ext[1:]
    if src_mtime < bin_mtime < src_mtime + 300:
        click.echo('Skipping Compile')
    else:
        if ext not in commands:
            raise click.ClickException(f'Cannot find compile command ({ext})')
        command = commands[ext]%filename
        click.echo(command)
        os.system('touch %s'%filename)
        return_code = os.system(command)
        if return_code != 0:
            raise click.ClickException('Compile Failed.')


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
        click.secho('Runtime Mode', fg='bright_cyan')
        os.system('./run')
        return


    maxtime = 0
    align_length = max([len(s) for s in input_paths]) - len(testcase_directory) - 3
    for input_path in input_paths:
        output_path = input_path[:-3] + '.out'
        answer_path = input_path[:-3] + '.ans'
        tc_name = input_path[len(testcase_directory):-3]
        click.echo(tc_name.rjust(align_length) + ' ', nl=False)
        start_time = time.time_ns()
        with open(input_path, 'r') as input_file, open(output_path, 'w') as output_file:
            try:
                result = subprocess.run(['./run'], stdin=input_file, stdout=output_file, timeout=timelimit)
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
        else:
            click.secho('AC  ', fg='bright_green', nl=False)
        click.echo(f'{tc_time}ms')
    click.secho(f'Maximum Time: {maxtime}ms', fg='bright_white')

if __name__ == '__main__':
    solve()
