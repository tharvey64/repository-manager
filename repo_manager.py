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

def test_organizations_list_repos(github, page=1):
    path = 'orgs/{org}/repos'.format(org=_ORG)
    return github.get(path,params={'type':'all','per_page':'100','page':page})

def collect_all_repos(github):
    # path = 'orgs/{org}/repos'.format(org=_ORG)
    response = test_organizations_list_repos(github)
    repos = response.json()
    links = get_links(response.headers.get('Link'))
    while links.get('last',False):
        # print(response.content)
        print(response.headers)
        response = test_organizations_list_repos(github, page=links['next'])
        links = get_links(response.headers.get('Link'))
        repos+=response.json()
        print(len(repos))
def get_links(link_header_str):
    link_header = (parse_link(link_str) for link_str in link_header_str.split(','))
    # print(len(link_header))
    link_info = {link_info['rel']: link_info['page'] for link_info in link_header}
    return link_info

def parse_link(link):
    url, relation = link.split(';')
    return  {'page': get_page(url),'rel':relation.split('=')[1].strip('"')}

def get_page(url):
    return re.search(r'(?<=page=)(?<!per_page=)\d*',url).group()