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
@click.option('--yes', is_flag=True, help="Choose sensible values and no prompt")
@click.option('--git-dir', '-d', type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.option('--trace-content', type=str, default="""tracef('TracePoint: BugTriggered');""")
@click.option('--trace-header', type=str, default="""#include <lttng/tracef.h>""")
def diff(git_dir, pre, post, output_dir, write, prompt, yes, trace_content, trace_header):
    def insert_trace(og, adds, what, do_prompt=False, n_context=3, filename=None, header=None):
        _fc = og.splitlines()
        def show_insertion(lines, ins_ix, content, n_context):
            _l, _r = max(0, ins_ix-n_context), min(len(lines),ins_ix+n_context)
            click.echo('\n'.join(lines[_l:ins_ix]))
            click.echo(colorama.Fore.GREEN + content +colorama.Fore.RESET)
            click.echo('\n'.join(lines[ins_ix+1:_r]))
        
        sed_cmd = ['sed']
        # Ask for header insertion
        header_insertions_line = []
        if filename.endswith('.h') or filename.endswith('.cu') or filename.endswith('cuh') or filename.endswith('cpp'):
            logger.info('Detected C++ file')
            include_ix = [i for i, line in enumerate(_fc) if line.startswith('#include')]
            def insert_auto_header():
                # Choose last insertion point
                header_ins = include_ix[-1]
                if header_ins == 0:
                    logger.warning('Automatic insertion of header tracing chose line 0. Will place at line 1.')
                    header_ins = 1
                else:
                    logger.info('Automatic insertion of header at line {}'.format(header_ins))
                header_insertions_line.append(header_ins)

            if len(include_ix) != 0:
                logger.info('Found include')
                for k in include_ix:
                    logger.debug('Line {}: Includes found {}'.format(k, _fc[k]))
                if yes:
                    insert_auto_header()
                else:
                    for i, line_no in enumerate(include_ix):
                        if line_no == 0:
                            logger.info('Insertion at 0 unsupported')
                            continue
                        if do_prompt:
                            show_insertion(_fc, line_no, header, n_context=n_context)
                            choice = click.prompt('[{}/{}] Add include here?'.format(i+1, len(include_ix)),
                                type=click.Choice(['y','n','a'], case_sensitive=False),
                                default='y', show_choices=True)
                            if choice == 'y':
                                header_insertions_line.append(line_no)
                                logger.debug('Added line {} to header output'.format(line_no))
                            elif choice == 'n':
                                logger.debug('User chose not to add header')
                            elif choice == 'a':
                                insert_auto_header()
                                logger.debug('Automatic insertion at last and skipping.')
                                break
                        else:
                            header_insertions_line.append(line_no)
                            logger.debug('Added line {} to header output'.format(line_no))
        else:
            logger.info('File {} not supported for header insertion'.format(filename))

        # Insert header
        if len(header_insertions_line) != 0:
            for header_lin in header_insertions_line:
                sed_cmd.append('-e'); sed_cmd.append(f'{header_lin}i{header}')
        else:
            logger.info('No suitable header insertion point was found')

        # Ask for trace insertion
        for i, line_no in enumerate(adds):
            if do_prompt:
                show_insertion(_fc, line_no, content=what, n_context=n_context)
                if click.confirm('[{}/{}] Add this trace in position:?'.format(i, len(adds))):
                    sed_cmd.append('-e'); sed_cmd.append(f'{line_no}i{what}')
                    logger.debug('Added line {} to output'.format(line_no))
                else:
                    logger.debug('User chose not to add to output at line {}'.format(line_no))
            else:
                sed_cmd.append('-e'); sed_cmd.append(f'{line_no}i{what}')
        if len(sed_cmd) == 1:
            logger.info('No chunk to change. Returning original input.')
            return og
        logger.debug('Command to run')
        logger.debug(' '.join(sed_cmd))
        r = subprocess.run(sed_cmd, stdout=subprocess.PIPE, input=og.encode('utf-8'), check=True)
        return r.stdout.decode("utf-8")

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
    written_files = []
    for f in files:
        logger.info('For file {}'.format(f))
        diff_for_f = diff_file(git_dir, pre, post, f)
        lines_changed = dp.findChangedLines(diff_for_f)
        # Get file content at revision
        logger.info('Lines {}'.format(' '.join(map(str,lines_changed))))
        fc = get_file_at_rev(git_dir, post, f)
        prompt_insert = (not yes) and prompt
        new_file_content = insert_trace(fc, lines_changed, what=trace_content, header=trace_header, do_prompt=prompt_insert, filename=f)
        logger.debug('New content')
        #logger.debug(new_file_content)

        if write:
            destination = output_dir.joinpath(f)
            destination = destination.resolve()
            def w():
                destination.parent.mkdir(parents=True, exist_ok=True)
                with open(destination, "w") as of:
                    of.write("{0}".format(new_file_content))
                logger.info('Wrote file to {}'.format(destination))
                written_files.append(destination)
            # logger.debug(destination.relative_to(Path.cwd()))
            if yes:
                w()
            else:
                if prompt:
                    if click.confirm('Write to {}'.format(destination), default=True):
                        w()
                    else:
                        logger.info('Cancelled write.')
                else:
                    w()
        else:
            logging.info('Not writing output.')
    for wf in written_files:
        logging.info('Wrote file {}'.format(wf))

if __name__ == "__main__":
    cli()
