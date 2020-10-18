import os
import io
import re
import logging
from collections import namedtuple, ChainMap
from github import Github, Repository, GitRelease
from pathlib import Path
from study_enums import StudyPhase1Field, StudyPhase2Field
import typing
import dataclasses

o = Path('out')
o.mkdir(exist_ok=True)
raw_dir, processed_dir = o / 'pytorch' / 'raw', o / 'pytorch' / 'processed'
raw_dir.mkdir(exist_ok=True, parents=True)
processed_dir.mkdir(exist_ok=True, parents=True)

logging.basicConfig(level=logging.DEBUG)
# Maybe should subclass Github.Github

def extract_release(github_client: Github, repo: str):
    pass

def get_all_releases(repo: Repository):
    # TODO: Maybe add support for various versions
    return repo.get_releases()

ScrapingInformation = namedtuple('ScrapingInformation', ['phase1', 'phase2', 'other'])


def get_bug_fixes_via_md_parse(release: GitRelease) -> typing.List[ScrapingInformation]:
    def extract_information_from_line(line):
        regex = r"^\s*\*\s?(?P<description>.*?)\s?(?:\((?P<link_text>\[.*?#?(?P<issue_number>\d+).*?\])\s?\((?P<link>[^ ]*?)\),?.*|\(#(?P<issue_number_alone>\d+)\)|)[* ]?$"
        # matches = re.finditer(regex, test_str, re.MULTILINE)
        match = re.match(regex, line, re.MULTILINE)
        # for matchNum, match in enumerate(matches, start=1):
            # print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
        logging.debug('Match is {}'.format(match))
        if match:
            extracted_groups = match.groupdict()
            logging.debug('groups are {}'.format(extracted_groups))
            return extracted_groups
        else:
            logging.debug('No match found for line: {}'.format(line))
            logging.debug('Returning None')
            return None
        # for groupNum in range(0, len(match.groups())):
        #     groupNum = groupNum + 1
        #     logging.debug("Group {groupNum} found at {start}-{end}: {group}".format(groupNum = groupNum, start = match.start(groupNum), end = match.end(groupNum), group = match.group(groupNum)))

    # TODO: Now we process the same way with all releases, we can specialize a parser for each release
    release_md = release.body

    md_heading_re = re.compile("^(?P<hashtags>#+)\s{0,}(?P<heading>.*)$")
    bug_fix_section_re = re.compile(r"^(#+)\s*Bug Fix", re.MULTILINE | re.IGNORECASE)
    bug_fix_section_activated, bug_fix_indentation_level = False, None
    bug_fix_ctx = 'root'

    # Destination
    bug_fixes = []

    release_handle = io.StringIO(release_md)
    for line in release_handle:
        line = line.replace('\r','').replace('\n','')
        if bug_fix_section_activated:
            heading_match = md_heading_re.match(line)
            if heading_match:
                g = heading_match.groupdict()
                heading_level = len(g['hashtags'])
                if heading_level <= bug_fix_indentation_level:
                    logging.debug('Found a heading level smaller than bug fix section.')
                    logging.info('Parse for bugs ended when found {}'.format(line))
                    break
                else:
                    bug_fix_ctx = g['heading']
            elif re.match('^\s*$', line):
                logging.debug('Found empty line: {}'.format(line))
                continue
            else:
                info = extract_information_from_line(line.rstrip())
                if info:
                    issue_number = info['issue_number'] or info['issue_number_alone']
                    logging.info('Extracted values {}'.format(info))

                    fields_1 = StudyPhase1Field(issue_number=issue_number)
                    # TODO: Transformation for release_note_description
                    fields_2 = StudyPhase2Field(link=info['link'], release_note_description=line)
                    bug_fixes.append(ScrapingInformation(fields_1, fields_2, {'issue_number': issue_number, 'link': info['link'], 'context': bug_fix_ctx, 'raw': line}))
        else:
            m = bug_fix_section_re.match(line)
            if m:
                bug_fix_section_activated, bug_fix_indentation_level = True, len(m.groups()[0])
                logging.debug('Found bug fix section')
                logging.debug(line)
                logging.debug('Level {}'.format(bug_fix_indentation_level))
    return bug_fixes

def get_bug_fixes(release: GitRelease, method='markdown') -> typing.List[ScrapingInformation]:
    # TODO: Could be a class
    if method != 'markdown' and method != 'html':
        raise ValueError

    with open(raw_dir / f'pytorch_{release.tag_name}.md', 'w') as f:
        f.write(release.body)

    if method == 'markdown':
        return get_bug_fixes_via_md_parse(release)
    elif method == 'html':
        return get_bug_fixes_via_html_parse(release)


def get_bug_fixes_via_html_parse(release: GitRelease):
    from bs4 import BeautifulSoup
    import markdown
    logging.warning('Scraping via HTML will not populate ScrapingInformation correctly.')
    # TODO: Maybe manually extract things with regex instead of transforming twice
    gen_html = markdown.markdown(release.body, output_format='html5')
    # logging.debug(gen_html)
    soup_parser = BeautifulSoup(gen_html, 'lxml')

    # We assume it will be in h1 after transformation
    headers = soup_parser.find_all('h1')
    logging.info(headers)
    bug_fixes = []
    for h in headers:
        logging.info(h)
        if h.text != 'Bug Fixes':
            logging.info(f'Passing header {h}')
            continue
        logging.info(f'Found header {h}')

        bugfix_context, current_tag_name = 'root', None
        for n in h.next_elements:
            current_tag_name = n.name
            if current_tag_name == 'h1':
                logging.debug('Found same level heading as bug fix, breaking...')
                break
            if current_tag_name in {'h2','h3','h4','h5','h6'}:
                logging.debug('Found deeper level heading, adding information')
                bugfix_context = n.text
            if current_tag_name == 'li':
                logging.info(f'[{bugfix_context}] Got bug fix {n}')
                issue_number = 'TODO'  # TODO
                l = n.find_all('a')
                link, pr_number = None, None
                if len(l) == 0:
                    logging.warning('No link for this one')
                else:
                    a = l[0]
                    link = a.attrs['href']
                    pr_number = a.attrs['href'].rsplit('/',1)[-1]
                logging.info(a)
                # TODO
                bug_fixes.append(ScrapingInformation(None, None, {'issue_number': pr_number, 'link': link, 'context': bugfix_context, 'raw': str(a)}))
    return bug_fixes


def get_client():
    from dotenv import load_dotenv
    load_dotenv()
    return Github(os.environ['GITHUB_PAT'])

def main(client):
    parse_method = 'markdown'
    repo_name = 'pytorch'
    repo = client.get_repo('pytorch/pytorch')
    releases = get_all_releases(repo)
    for release in releases:
        # if release.tag_name != 'v1.6.0':
        #     continue
        logging.info('Got {} ({})'.format(release.tag_name, release.html_url))
        # bug_fixes = get_bug_fixes_via_html_parse(release)
        bug_fixes = get_bug_fixes(release, method='markdown')

        logging.info('Release {} gathered information on {} bugs'.format(release.tag_name, len(bug_fixes)))
        if len(bug_fixes) == 0:
            logging.warn('No bugs found for release {}. Skipping...'.format(release.tag_name))
            continue
        
        flattened = []
        # Populate fields with correct information
        for bug in bug_fixes:
            bug.phase1.framework = repo_name
            bug.phase2.release = release.tag_name
            flattened.append(dict(ChainMap(dataclasses.asdict(bug.phase1), dataclasses.asdict(bug.phase2), bug.other)))
        with open(processed_dir / f'{repo_name}_{release.tag_name}.json', 'w') as of:
            import json
            json.dump(flattened, of)
        
        with open(processed_dir / f'{repo_name}_{release.tag_name}.csv', 'w', newline='') as csvfile:
            import pandas as pd
            df = pd.DataFrame.from_dict(flattened)
            df.to_csv(csvfile, index=False)

if __name__ == "__main__":
    main(get_client())
