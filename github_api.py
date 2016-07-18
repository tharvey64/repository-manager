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

    def git_api_pull_request(self, repo, head_branch, head_org, base_branch, base_org, title, body=''):
        '''
        edits are pulled from HEAD into BASE
        '''
        if base_org is None:
            base_org = head_org
        path = 'repos/{owner}/{repo}/pulls'
        data = json.dumps({
            'title': title,
            'head':'{organization}:{branch}'.format(organization=head_org,branch=head_branch),
            'base':'{branch}'.format(branch=base_branch),
            'body': body
        })
        response = self.post(
            path.format(
                owner=repo.owner.get('login'), 
                repo=repo.name
            ), 
            data=data
        )

        repo._info['_api_response_log']['pull_request'] = response.text
        if str(response.status_code)[0] == "2": 
            data = response.json()
        else:
            data = {}
        repo._info['pull_request_number'] = data.get('number')
        repo._info['head_sha'] = data.get('head',{}).get('sha')
        return response.text

    def git_api_confirm_pull_request(self, repo, org):
        """ 
        Get if a pull request has been merged
        GET repos/:owner/:repo/pulls/:number/merge
        """
        path = 'repos/{owner}/{repo}/pulls/{number}/merge'
        response = self.get(
            path.format(
                owner=repo.owner.get('login'),
                repo=repo.name,
                number=repo._info.get('pull_request_number')
            )
        )
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
        
        path = 'repos/{owner}/{repo}/pulls/{number}/merge'
        data = json.dumps({
            'commit_message': message,
            'sha': repo._info.get('head_sha')
        })
        response = self.put(
            path.format(
                owner=repo.owner.get('login'),
                repo=repo.name,
                number=repo._info.get('pull_request_number')
            ), 
            data=data
        )
        repo._info['_api_response_log']['merged_pull_request'] = response.text
        if str(response.status_code)[0] == "2": 
            data = response.json()
        else:
            data = {}
        repo._info['master_sha'] = data.get('sha')
        return response.text

    def git_api_create_fork(self, repo, organization):
        """
        https://developer.github.com/v3/repos/forks/#create-a-fork
        POST /repos/:owner/:repo/forks
        @param organization `string` Optional parameter to specify the organization name if forking into an organization.
        """
        path = "repos/{owner}/{repo}/forks"
        data = json.dumps({
            'organization': organization
        })
        response = self.post(
            path.format(
                owner=repo.owner.get('login'),
                repo=repo.name
            ),
            data=data
        )
        repo._info['_api_response_log']['create_fork'] = response.text
        if str(response.status_code)[0] == "2":
            data = response.json()
        else:
            data = {}
        return response.text

    def git_api_create_release(self, repo, release_type, message_body=''):
        """
        Create Release
        POST /repos/:owner/:repo/releases
        @param tag_name `string` Required. The name of the tag.
        @param target_commitish `string` Can be any branch or commit SHA
        @param name `string` name of the release
        @param body `string` Text describing the contents of the tag
        @param draft `boolean` True to create unpublished release. Default False
        @param prerelease `boolean` True to create release as prereleasae. Default False

        Example:
        {
          "tag_name": "v1.0.0",
          "target_commitish": "master",
          "name": "v1.0.0",
          "body": "Description of the release",
          "draft": false,
          "prerelease": false
        }
        """
        previous_release = self.git_api_get_latest_release(repo).get('tag_name')
        new_release = self.create_release_tag(previous_release, release_type)
        if 'message' in new_release:
            new_release['tag_name'] = previous_release
            repo._info['invalid_release'] = new_release
            return False
        new_tag = new_release.get('tag_name')
        
        path = "repos/{owner}/{repo}/releases"
        data = json.dumps({
          "tag_name": new_tag,
          "target_commitish": repo._info.get('master_sha'),
          "name": new_tag,
          "body": message_body,
        })
        response = self.post(path.format(
                owner=repo.owner.get('login'),
                repo=repo.name
            ),
            data=data
        )
        repo._info['_api_response_log']['create_release'] = response.text
        return response.text

    def git_api_get_master_sha(self, repo):
        path = 'repos/{owner}/{repo}/git/refs/{ref}'.format(
            owner=repo.owner.get('login'),
            repo=repo.name,
            ref='heads/master'
        )
        response = self.get(path)
        repo._info['_api_response_log']['get_master_sha'] = response.text
        if str(response.status_code)[0] == "2": 
            data = response.json().get('object')
        else:
            data = {}
        repo._info['master_sha'] = data.get('sha')
        return data.get('sha')


    def git_api_get_repository(self, repo):
        """
        https://developer.github.com/v3/repos/#get
        GET /repos/{owner}/{repo}
        """
        path = "repos/{owner}/{repo}".format(
            owner=repo.owner.get('login'),
            repo=repo.name
        )
        response = self.get(path)
        repo._info['_api_response_log']['get_repository'] = response.text
        if str(response.status_code)[0] == "2": 
            data = response.json()
        else:
            data = {}
        return data

    def git_api_get_latest_release(self, repo):
        """
        Get Latest Release
        GET /repos/:owner/:repo/releases/latest

        Response
        ['tag_name']
        """
        path = 'repos/{owner}/{repo}/releases/latest'
        response = self.get(
            path.format(
                owner=repo.owner.get('login'),
                repo=repo.name
            )
        )
        repo._info['_api_response_log']['get_latest_release'] = response.text
        if str(response.status_code)[0] == "2": 
            data = response.json()
        else:
            data = {}
        return data

    @staticmethod
    def create_release_tag(tag_name, release_type):
        """
        @param tag_name `string` the lastest release. Fromat `v<major>.<minor>.<patch>`
        @param release_type `string` can be `major`,  `minor` or `patch` 
        """
        
        cleaned_tag = [int(num) for num in tag_name.strip('v').split('.') if num.isdigit()]
        release_type = release_type.lower()
        if len(cleaned_tag) != 3:
            return {'message': 'Invalid tag_name.'}
        if release_type == "major":
            cleaned_tag[0] += 1
            cleaned_tag[1:] = 0,0
        elif release_type == "minor":
            cleaned_tag[1] += 1
            cleaned_tag[2] = 0
        elif release_type == "patch":
            cleaned_tag[2] += 1
        else:
            return {'message': 'Invalid `release_type`'}

        new_tag_name = 'v' + '.'.join(str(num) for num in cleaned_tag)
        return {'tag_name': new_tag_name}








