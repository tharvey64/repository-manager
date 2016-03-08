import repo_manager
import repo_filters



# make pull repuest that pulls test-update into master
# close pull request
# get the SHA from closing that pull request
# create new release at this SHA
# FORK TO BYTE EXERCISES

def add_commit_edits(git, repos, branch, message):
    for r in repos:
        git.git_switch_branch(r, branch)
        git.git_add(r)
        git.git_commit(r, message)

def push_edits(git, repos, branch):
    raise "Are you sure?"
    for r in repos:
        git.git_push(r, branch)
        
def main(fiter_string):
    collector = repo_manager.Collector(repo_manager.github)
    collector.run()
    matchers = dict(name_startswith=repo_filters.name_startswith_filter(fiter_string))
    filter_set = repo_manager.FilterSet(**matchers)
    
    repositories = []
    for repo in collector.repositories:
        if filter_set.clean(repo):
            repositories.append(repo_manager.Repository(**repo))
    return repositories


if __name__ == "__main__":
    repos = main('exercise-python')
    git = repo_manager.GitLocal()
    git_update = repo_manager.githubEXT
