import os
import click
import logging
from pathlib import Path
import subprocess
from diff_processor import DiffProcessor
import colorama

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
console_h = logging.StreamHandler()
console_h.setLevel(logging.INFO)
debug_fh = logging.FileHandler('debug.log', mode='w')
debug_fh.setLevel(logging.DEBUG)
logger.addHandler(debug_fh)
logger.addHandler(console_h)

def git_diff(git_dir, rev1, rev2):
    if isinstance(git_dir, str):
        git_dir = Path(git_dir)
    repo = git.Repo(git_dir)
    a, b = repo.rev_parse(rev1), repo.rev_parse(rev2)
    logger.debug('Getting revision {}..{}'.format(a,b))
    return repo.diff(rev1, rev2)

def diff_file_paths(git_dir, rev1, rev2):
    if not isinstance(git_dir, Path):
        git_dir = Path(git_dir)
    env_copy = os.environ.copy()
    env_copy['GIT_DIR'] = git_dir
    result_patchfile = subprocess.run(['git', 'diff', '{}..{}'.format(rev1, rev2), '--name-only'], stdout=subprocess.PIPE, env=env_copy, check=True)
    files = result_patchfile.stdout.decode("utf-8")
    return files.splitlines(keepends=False)


def diff_file(git_dir, rev1, rev2, diff_path):
    if not isinstance(git_dir, Path):
        git_dir = Path(git_dir)
    env_copy = os.environ.copy()
    env_copy['GIT_DIR'] = git_dir
    result_patchfile = subprocess.run(['git', 'diff', '{}..{}'.format(rev1, rev2), '--', diff_path], stdout=subprocess.PIPE, env=env_copy, check=True)
    return result_patchfile.stdout.decode("utf-8")

def get_file_at_rev(git_dir, rev, p):
    if not isinstance(git_dir, Path):
        git_dir = Path(git_dir)
    env_copy = os.environ.copy()
    env_copy['GIT_DIR'] = git_dir
    f = subprocess.run(['git', 'show', '{}:{}'.format(rev, p)], stdout=subprocess.PIPE, env=env_copy, check=True)
    return f.stdout.decode("utf-8")

@click.group()
def cli():
    pass


@cli.command()
@click.argument('pre', type=str)
@click.argument('post', type=str)
@click.option('--write/--no-write', default=True)
@click.option('--prompt/--no-prompt', default=True)
@click.option('--output-dir', type=str, default=True)
@click.option('--yes', is_flag=True)
@click.option('--git-dir', '-d', type=click.Path(exists=True, file_okay=False, resolve_path=True))
def diff(git_dir, pre, post, output_dir, write, prompt, yes):
    def insert_trace(og, adds, what, use_sed=True, do_prompt=False, n_context=3):
        _fc = og.splitlines()
        if use_sed:
            sed_cmd = ['sed']
            for l in adds:
                if do_prompt:
                    _l, _r = max(0, l-n_context), min(len(_fc),l+n_context)
                    # Simple echoing
                    # _ctx = _fc[_l:_r]
                    # click.echo('Input here')
                    # click.echo('\n'.join(_ctx))
                    # ... or "fancy"
                    click.echo('\n'.join(_fc[_l:l]))
                    click.echo(colorama.Fore.GREEN + what +colorama.Fore.RESET)
                    click.echo('\n'.join(_fc[l+1:_r]))
                    if click.confirm('Add this trace in position:?'):
                        sed_cmd.append('-e'); sed_cmd.append(f'{l}i{what}')
                        logging.debug('Added line {} to output'.format(l))
                    else:
                        logging.debug('User chose not to add to output at line {}'.format(l))
                else:
                    sed_cmd.append('-e'); sed_cmd.append(f'{l}i{what}')
            if len(sed_cmd) == 1:
                logging.info('No chunk to change. Returning original input.')
                return og
            logger.debug('Command to run')
            logger.debug(' '.join(sed_cmd))
            r = subprocess.run(sed_cmd, stdout=subprocess.PIPE, input=og.encode('utf-8'), check=True)
            return r.stdout.decode("utf-8")
        else:
            raise NotImplementedError()

    output_dir = Path(output_dir)
    logging.debug('Output dir is {}'.format(output_dir))

    logging.debug('Passed revisions {} and {}'.format(pre,post))
    # x = git_diff(git_dir, pre, post)
    # logging.debug('Got diff {}'.format(x))
    files = diff_file_paths(git_dir, pre, post)
    logger.info('Files changed:')
    for f in files:
        logger.info(f)
    dp = DiffProcessor(git_dir)
    for f in files:
        logger.info('For file {}'.format(f))
        diff_for_f = diff_file(git_dir, pre, post, f)
        lines_changed = dp.findChangedLines(diff_for_f)
        # Get file content at revision
        logger.info('Lines {}'.format(' '.join(map(str,lines_changed))))
        fc = get_file_at_rev(git_dir, post, f)
        prompt_insert = not yes or prompt
        new_file_content = insert_trace(fc, lines_changed, '#========TRACER_CODE=========', do_prompt=prompt_insert)
        logger.debug('New content')
        logger.debug(new_file_content)

        if write:
            destination = output_dir.joinpath(f)
            destination = destination.resolve()
            def w():
                destination.parent.mkdir(parents=True, exist_ok=True)
                with open(destination, "w") as of:
                    of.write("{0}".format(new_file_content))
                logger.info('Wrote file to {}'.format(destination))
            # logger.debug(destination.relative_to(Path.cwd()))
            if yes:
                w()
            else:
                if prompt:
                    if click.confirm('Write to {}'.format(destination)):
                        w()
                    else:
                        logger.info('Cancelled write.')
                else:
                    w()
        else:
            logging.info('Not writing output.')

if __name__ == "__main__":
    cli()
