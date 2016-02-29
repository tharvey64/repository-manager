import repo_manager
import repo_filters

import subprocess


def git_clone_and_create_branch(repo):
    command = 'cd ../repositories && git clone {clone_url}'.format(clone_url=repo.clone_url)
    subprocess.getoutput(command)
    command = 'git -C {path} checkout -b test-update'.format(path='../repositories/'+repo.name)
    subprocess.getoutput(command)

def git_add(repo):
    command = 'git -C {path} add .'.format(path='../repositories/'+repo.name)
    subprocess.getoutput(command)

def git_commit(repo):
    command = 'git -C {path} commit -m "adding edits"'.format(path='../repositories/'+repo.name)
    subprocess.getoutput(command)

def git_push(repo):
    command = 'git -C {path} push origin test-update'.format(path='../repositories/'+repo.name)
    subprocess.getoutput(command)

# make pull repuest that pulls test-update into master
# close pull request
# get the SHA from closing that pull request
# create new release at this SHA
# FORK TO BYTE EXERCISES

def main():
    collector = repo_manager.Collector(repo_manager.github)
    collector.run()
    matchers = dict(name_startswith=repo_filters.name_startswith_filter('exercise'))
    filter_set = repo_manager.FilterSet(**matchers)
    
    repositories = []
    for repo in collector.repositories:
        if filter_set.clean(repo):
            repositories.append(repo_manager.Repository(**repo))
    return repositories


if __name__ == "__main__":
    repos = main()
    for r in repos:
        clone_and_create_branch(r)