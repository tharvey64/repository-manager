import re
import json
import sys
import subprocess
from github_api import GithubAPI, GithubAPIExtension
from git_local import GitLocal
try:
    from local_config import config
except ImportError:
    sys.stderr.write(
'''
Warning: Can't find the file 'local_config.py' in the directory
containing {file}. It appears you've customized things. Create {file} in
the directory containing repo_manager.py following the format provided
in local_config.py.md.
'''.format(file=__file__))
    sys.stderr.write('\nFor debugging purposes, the exception was:\n\n')
    traceback.print_exc()


_ORG = config.get('organization')

github = GithubAPI(config.get('access_token'))


githubEXT = GithubAPIExtension(config.get('access_token'))

class Repository:
    def __init__(self,**kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self._info = {'_api_response_log': {} }

class FilterSet:
    def __init__(self, **kwargs):
        self.filters = [{'name':key,'filter':value} for key,value in kwargs.items()]
        self.match_all = True
    def clean(self, item):
        criteria = (rule['filter'](item) for rule in self.filters)
        if self.match_all:
            return all(criteria)
        else:
            return any(criteria)

    def add_filter(self, name, func):
        self.filters.append({'name':name,'filter':func})


class Collector:
    def __init__(self, github, org):
        self.github = github
        self.org = org
        self.repositories = []

    def collect_all_repos(self):
        links = {'last':True}
        repos = []
        while links.get('last', False):
            response = self.get_repos(page=links.get('next', 1))
            header_link = response.headers.get('Link')
            links = {} if not header_link else self.get_links(header_link)
            repos += response.json()
            print(len(repos))
        return repos
    
    def get_repos(self, page=1):
        path = 'orgs/{org}/repos'.format(org=self.org)
        return self.github.get(path,params={'type':'all','per_page':'100','page':page})
    
    def get_links(self, link_header_str):
        link_header = self.parse_link_header(link_header_str)
        link_info = {link_info['rel']: link_info['page'] for link_info in link_header}
        return link_info

    def parse_link_header(self, link_header):
        links = (link_str.split(';') for link_str in link_header.split(','))
        return  (
            {
                'page': re.search(r'(?<=page=)(?<!per_page=)\d*',url).group(),
                'rel': relation.split('=')[1].strip('"')
            }
            for url,relation in links
        )

    def run(self):
        self.repositories = self.collect_all_repos()
