_repos = dict()
_repos['pytorch'] = {
    'git'  : 'github',
    'link' : 'pytorch/pytorch',
    'api_full_url': 'https://api.github.com/repos/pytorch/pytorch'
}

def get_repo(framework):
    r = _repos[framework.lower()]
    if r is None:
        raise ValueError('Framework {} not valid'.format(framework))
    return r