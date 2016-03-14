import pprint

import repo_manager
import repo_filters



# make pull repuest that pulls test-update into master
# close pull request
# get the SHA from closing that pull request
# create new release at this SHA
# FORK TO BYTE EXERCISES


def clone_checkout(git, repos, path_to_repo, branch_name):
    for r in repos:
        git.git_clone(r, path_to_repo)
        git.git_create_branch(r, branch_name, path_to_repo)

def add_commit_edits(git, repos, path_to_repo, branch, message):
    for r in repos:
        git.git_switch_branch(r, branch, path_to_repo)
        git.git_add(r, path_to_repo)
        git.git_commit(r, message, path_to_repo)

def push_edits(git, repos, path_to_repo, branch):
    raise "Are you sure?"
    for r in repos:
        git.git_push(r, branch, path_to_repo)

def build_repo_set_that_starts_with(fiter_string, org):
    collector = repo_manager.Collector(repo_manager.github, org)
    collector.run()
    starts_with_filter = repo_filters.name_startswith_filter(fiter_string)
    matchers = dict(name_startswith=starts_with_filter)
    filter_set = repo_manager.FilterSet(**matchers)
    Repository = repo_manager.Repository

    return [Repository(**repo) for repo in collector.repositories if filter_set.clean(repo)]

# NEW
# some of these should use the merge api
def make_pull_requests(magic, repos, *args):
    head_branch, head_org, base_branch, base_org, message = args
    for repo in repos:
        text = magic.git_api_pull_request(repo, head_branch, head_org, base_branch, base_org, message)
        if not repo._info.get('pull_request_number'):
            print("="*80)
            print(repo.name)
            print("-"*30)
            print(text)
            print("*"*80)

def merge_pull_request(magic, repos, message):
    for repo in repos:
        if repo._info.get('pull_request_number') and repo._info.get('head_sha'):
            text = magic.git_api_merge_pull_request(repo, message)
            if not repo._info.get('master_sha'):
                print("="*80)
                print(repo.name)
                print("-"*30)
                print(text)
                print("*"*80)


def create_new_releases(magic, repos, release_type, message_body):
    for repo in repos:
        if repo._info.get('master_sha'):
            text = magic.git_api_create_release(repo, release_type, message_body)
            if text == False:
                print("="*80)
                print(repo.name)
                print("-"*30)
                print(repo._info)
                print("*"*80)

def fork_latest_release_to_be(magic, byte_exercise_repos, byte_academy_repos, message):
    """
    for each repo
        get the latest release 
        make a pull request 
    """
    head_org = "ByteAcademyCo"
    # message = 'Patches.'

    releases = {repo.name:magic.git_api_get_latest_release(repo) for repo in byte_academy_repos}
    if len(releases) != len(byte_exercise_repos):
        raise "Out Of Sync"

    for repo in byte_exercise_repos:
        branch = releases.get(repo.name)
        if branch:
            text = magic.git_api_pull_request(repo, branch, head_org, repo.default_branch, repo.owner.get('login'), message)
            if not repo._info.get('pull_request_number'):
                print("="*80)
                print(repo.name)
                print("-"*30, text, "*"*80, sep='\n')
        else:
            print("="*80)
            print(repo.name)
            print("MISSING RELEASE","-"*30, "*"*80, sep='\n')


# def backup_ba(git, path_to_backup):
#     raise "I do not think you meant to do this."
#     collector = repo_manager.Collector(repo_manager.github)
#     collector.run()
#     repositories = [repo_manager.Repository(**repo) for repo in collector.repositories]

#     count = 0
#     for repo in repositories:
#         git.git_clone(repo, path_to_backup)
#         count += 1
#         if count % 10 == 0:
#             print(count)
#     print("Cloned: ", count, "repositories.")


if __name__ == "__main__":
    be_repos = build_repo_set_that_starts_with('exercise-python', 'ByteExercises')
    # ba_repos = build_repo_set_that_starts_with('exercise-python', 'ByteAcademyCo')
    # git = repo_manager.GitLocal()
    # clone_checkout(git, ba_repos, '../repositories/', 'patch-tests')
    # add_commit_edits(git, ba_repos, '../repositories/', 'patch-tests', 'Fixing bugs and errors in tests.')
    # push_edits(git, ba_repos, '../repositories/', 'patch-tests')
    # git_update = repo_manager.githubEXT
    # args = ['patch-tests','ByteAcademyCo', 'master', 'ByteAcademyCo', 'Patching bugs.']
    # make_pull_requests(git_update, ba_repos, *args)
    # merge_pull_request(git_update, ba_repos, 'Merging patches.')
    # create_new_releases(git_update, ba_repos, 'minor', 'Test patches and other edits.')
