import requests
import json

class GithubAPI:
    def __init__(self, access_token):
        self.access_token = access_token

    def get(self, api_path, **kwargs):
        params = kwargs['params'] if type(kwargs.get('params')) == dict else {}
        headers = kwargs['headers'] if type(kwargs.get('headers')) == dict else {}

        params.update({'access_token': self.access_token})

        return requests.get('https://api.github.com/'+api_path, params=params, headers=headers)

    def post(self, api_path, **kwargs):
        params = kwargs['params'] if type(kwargs.get('params')) == dict else {}
        headers = kwargs['headers'] if type(kwargs.get('headers')) == dict else {}
        data = kwargs['data'] if kwargs.get('data', None) else None
        
        params.update({'access_token': self.access_token})

        return requests.post('https://api.github.com/'+api_path, params=params, data=data, headers=headers)

    def put(self, api_path, **kwargs):
        params = kwargs['params'] if type(kwargs.get('params')) == dict else {}
        headers = kwargs['headers'] if type(kwargs.get('headers')) == dict else {}
        data = kwargs['data'] if kwargs.get('data', None) else None

        params.update({'access_token': self.access_token})

        return requests.put('https://api.github.com/'+api_path, params=params, headers=headers, data=data)

    def patch(self, api_path, **kwargs):
        params = kwargs['params'] if type(kwargs.get('params')) == dict else {}
        headers = kwargs['headers'] if type(kwargs.get('headers')) == dict else {}
        data = kwargs['data'] if kwargs.get('data', None) else None

        params.update({'access_token': self.access_token})

        return requests.patch('https://api.github.com/'+api_path, params=params, headers=headers, data=data)


    def contents(self, owner, repo, path, MTtype='json'):
        url = 'repos/{owner}/{repo}/contents/{path}'.format(
            owner=owner,
            repo=repo,
            path = path
        )
        headers = {
            'Accept': 'application/vnd.github.v3.{}'.format(MTtype)
        }

        return self.get(url, headers=headers)

class GithubAPIExtension(GithubAPI):
    def __init__(self, access_token):
        super().__init__(access_token)

    def git_api_pull_request(self, repo, head_org, base_org=None):
        '''
        edits are pulled from HEAD into BASE
        '''
        if base_org is None:
            base_org = head_org
        path = 'repos/{owner}/{repo}/pulls'.format(owner=base_org, repo=repo.name)
        data = json.loads({
            'title':'Adding Tests.',
            'head':'{organization}:test-update'.format(organization=head_org),
            'base':'{organization}:master'.format(organization=base_org),
            'body':'First iteration of test error messages.'
        })
        response = self.post(path, data=data)

        repo._info['_api_response_log']['pull_request'] = response.text
        if str(response.status_code)[0] == "2": 
            data = response.json()
        else:
            data = {}
        repo._info['merge_number'] = data.get('number')
        repo._info['head_sha'] = data.get('head',{}).get('sha')
        return response.text

    def git_api_confirm_pull_request(self, repo, org):
        """ 
        Get if a pull request has been merged
        GET repos/:owner/:repo/pulls/:number/merge
        """
        path = 'repos/{owner}/{repo}/pulls/{number}/merge'.format(owner=org,repo=repo.name,number=repo._info.get('merge_number'))
        response = self.get(path)
        repo._info['_api_response_log']['merge_status'] = response.text
        return response.text

    def git_api_merge_pull_request(self, repo, message):
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
        
        path = 'repos/{owner}/{repo}/pulls/{number}/merge'.format(owner=org,repo=repo.name,number=repo._info.get('merge_number'))
        data = json.loads({
            'commit_message': message,
            'sha': repo._info.get('sha')
        })
        self.put(path, data=data)
        repo._info['_api_response_log']['merged_pull_request'] = response.text
                if str(response.status_code)[0] == "2": 
            data = response.json()
        else:
            data = {}
        repo._info['master_sha'] = data.get('sha')
        return response.text

    def git_api_create_release(self, repo):
        """
        Create Release
        POST /repos/:owner/:repo/releases
        @param tag_name `string` 
        @param target_commitish `string`
        @param name `string`
        @param body `string`
        @param draft `boolean`
        @param prerelease `boolean`
        """
