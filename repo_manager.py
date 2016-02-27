import re
from github_api import GithubAPI
try:
    from local_config import config
except ImportError:
    sys.stderr.write(
'''
Warning: Can't find the file 'local_config.py' in the directory
containing {}. It appears you've customized things. Create {} in
the directory containing repo_manager.py and file the format provided
in local_config.py.md.
'''.format(__file__))
    sys.stderr.write('\nFor debugging purposes, the exception was:\n\n')
    traceback.print_exc()


_ORG = 'ByteAcademyCo'


github = GithubAPI(config.get('access_token'))

def filter_repositories(repositories, *args):
    '''
    args will be filters
    they must be callable
    '''
    cleaned_repos = []
    for repo in repositories:
        if all(filter_(repo) for filter_ in args):
            cleaned_repos.append(repo)
    return cleaned_repos

def name_startswith_filter(string):
    def name_filter(item):
        return item.get('name','').startswith(string)
    return name_filter

def collect_all_repos(github):
    response = get_repos(github)
    repos = response.json()
    links = get_links(response.headers.get('Link'))
    while links.get('last',False):
        response = get_repos(github, page=links['next'])
        links = get_links(response.headers.get('Link'))
        repos+=response.json()
        print(len(repos))
    return repos

def get_repos(github, page=1):
    path = 'orgs/{org}/repos'.format(org=_ORG)
    return github.get(path,params={'type':'all','per_page':'100','page':page})

def get_links(link_header_str):
    link_header = parse_link_header(link_header_str)
    link_info = {link_info['rel']: link_info['page'] for link_info in link_header}
    return link_info

def parse_link_header(link_header):
    links = (link_str.split(';') for link_str in link_header.split(','))
    return  ({
        'page': get_page(url),
        'rel':relation.split('=')[1].strip('"')}
        for url,relation in links
    )

def get_page(url):
    return re.search(r'(?<=page=)(?<!per_page=)\d*',url).group()

