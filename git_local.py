class GitLocal:
    @staticmethod
    def git_clone_and_create_branch(repo):
        command = 'cd ../repositories && git clone {clone_url}'.format(clone_url=repo.clone_url)
        subprocess.getoutput(command)
        command = 'git -C {path} checkout -b test-update'.format(path='../repositories/'+repo.name)
        subprocess.getoutput(command)

    @staticmethod
    def git_switch_branch(repo, branch):
        command = 'git -C {path} checkout {branch}'.format(path='../repositories/'+repo.name,branch=branch)
        subprocess.getoutput(command)

    @staticmethod
    def git_add(repo):
        command = 'git -C {path} add .'.format(path='../repositories/'+repo.name)
        subprocess.getoutput(command)

    @staticmethod
    def git_commit(repo, message):
        command = 'git -C {path} commit -m "{message}"'.format(path='../repositories/'+repo.name,message=message)
        subprocess.getoutput(command)

    @staticmethod
    def git_push(repo, branch):
        command = 'git -C {path} push origin {branch}'.format(path='../repositories/'+repo.name,branch=branch)
        return subprocess.getoutput(command)