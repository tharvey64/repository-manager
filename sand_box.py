import repo_manager
import repo_filters

import subprocess


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
    git = repo_manager.githubEXT
    # for r in repos:
        # githubEXT