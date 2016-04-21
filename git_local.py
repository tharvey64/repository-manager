import subprocess

class GitLocal:
    @staticmethod
    def git_clone(repo, path_to_repo):
        command = 'cd {path} && git clone {clone_url}'.format(path=path_to_repo,clone_url=repo.clone_url)
        return subprocess.getoutput(command)
    
    @staticmethod
    def git_create_branch(repo, branch_name, path_to_repo):
        command = 'git -C {path} checkout -b {branch}'.format(path=path_to_repo+repo.name,branch=branch_name)
        return subprocess.getoutput(command)

    @staticmethod
    def git_switch_branch(repo, branch, path_to_repo):
        command = 'git -C {path} checkout {branch}'.format(path=path_to_repo+repo.name,branch=branch)
        return subprocess.getoutput(command)

    @staticmethod
    def git_add(repo, path_to_repo):
        command = 'git -C {path} add .'.format(path=path_to_repo+repo.name)
        return subprocess.getoutput(command)

    @staticmethod
    def git_commit(repo, message, path_to_repo):
        command = 'git -C {path} commit -m "{message}"'.format(path=path_to_repo+repo.name,message=message)
        return subprocess.getoutput(command)

    @staticmethod
    def git_push(repo, branch, path_to_repo):
        command = 'git -C {path} push origin {branch}'.format(path=path_to_repo+repo.name,branch=branch)
        return subprocess.getoutput(command)