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