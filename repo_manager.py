import re
import json
from github_api import GithubAPI
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

class GitLocal:
    @staticmethod
    def git_clone_and_create_branch(repo):
        command = 'cd ../repositories && git clone {clone_url}'.format(clone_url=repo.clone_url)
        subprocess.getoutput(command)
        command = 'git -C {path} checkout -b test-update'.format(path='../repositories/'+repo.name)
        subprocess.getoutput(command)

    @staticmethod
    def git_add(repo):
        command = 'git -C {path} add .'.format(path='../repositories/'+repo.name)
        subprocess.getoutput(command)

    @staticmethod
    def git_commit(repo):
        command = 'git -C {path} commit -m "adding edits"'.format(path='../repositories/'+repo.name)
        subprocess.getoutput(command)

    @staticmethod
    def git_push(repo):
        command = 'git -C {path} push origin test-update'.format(path='../repositories/'+repo.name)
        subprocess.getoutput(command)


class GithubAPIExtension(GithubAPI):
    def __init__(self, access_token):
        super().__init__(access_token)
        self.__log = []

    def get_log(self):
        self.__log, temp = [], self.__log
        return temp

    def git_api_pull_request(self, repo, org):
        path = 'repos/{owner}/{repo}/pulls'.format(owner=_ORG, repo=repo.name)
        data = json.loads({
            'title':'Adding Tests.',
            'head':'{organization}:test-update'.format(organization=_ORG),
            'base':'{organization}:master'.format(organization=_ORG),
            'body':'First iteration of test error messages.'
        })
        response = self.post(path, data=data)

        self.__log.append(response)

        if str(response.status_code)[0] == "2": 
            data = response.json()
        else:
            data = {}
        return data.get('number')

    def git_api_confirm_pull_request(self, repo):
        """ 
        Get if a pull request has been merged
        GET repos/:owner/:repo/pulls/:number/merge
        """
        path = 'repos/{owner}/{repo}/pulls/{number}/merge'.format(owner=_ORG,repo=repo.name,number=repo.info.get('number'))
        response = self.get(path)
        if str(response.status_code)[0] == "2": 
            data = response.json()
        else:
            data = {}
        return data

    def git_api_merge_pull_request(self, repo):
        """
        merge pull request
        PUT /repos/:owner/:repo/pulls/:number/merge
        @param commit_message  string  Extra detail to append to automatic commit message.
        @param sha string  SHA that pull request head must match to allow merge 
        Response if successful 
        Status 200
        {
          "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e",
          "merged": true,
          "message": "Pull Request successfully merged"
        }


        Response if merge cannot be performed
        Status 405 Method Not Allowed
        {
          "message": "Pull Request is not mergeable",
          "documentation_url": "https://developer.github.com/v3/pulls/#merge-a-pull-request-merge-button"
        }

        Response if sha was provided and pull request head did not match
        Status 409 Conflict
        {
          "message": "Head branch was modified. Review and try the merge again.",
          "documentation_url": "https://developer.github.com/v3/pulls/#merge-a-pull-request-merge-button"
        }
        """

githubEXT = GithubAPIExtension(config.get('access_token'))

class Repository:
    def __init__(self,**kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.info = {}

class FilterSet:
    def __init__(self, **kwargs):
        self.filters = [{'name':key,'filter':value} for key,value in kwargs.items()]

    def clean(self, item):
        return all(rule['filter'](item) for rule in self.filters)

    def add_filter(self, name, func):
        self.filters.append({'name':name,'filter':func})


class Collector:
    def __init__(self, github):
        self.github = github
        self.org = _ORG
        self.repositories = []

    def collect_all_repos(self):
        response = self.get_repos()
        repos = response.json()
        links = self.get_links(response.headers.get('Link'))

        while links.get('last', False):
            response = self.get_repos(page=links['next'])
            links = self.get_links(response.headers.get('Link'))
            repos += response.json()
            print(len(repos))
        return repos
    
    def get_repos(self, page=1):
        path = 'orgs/{org}/repos'.format(org=_ORG)
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
