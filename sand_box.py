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
    # raise "Are you sure?"
    for r in repos:
        git.git_push(r, branch, path_to_repo)

def build_repo_set_that_starts_with(org, fiter_string):
    collector = repo_manager.Collector(repo_manager.github, org)
    collector.run()
    starts_with_filter = repo_filters.name_startswith_filter(fiter_string)
    matchers = dict(name_startswith=starts_with_filter)
    filter_set = repo_manager.FilterSet(**matchers)
    Repository = repo_manager.Repository

    return [Repository(**repo) for repo in collector.repositories if filter_set.clean(repo)]

def build_repo_set_from_repos(org, *args):
    collector = repo_manager.Collector(repo_manager.github, org)
    collector.run()
    name_in_filter = repo_filters.name_in(*args)
    matchers = dict(name_in=name_in_filter)
    filter_set = repo_manager.FilterSet(**matchers)
    Repository = repo_manager.Repository

    return [Repository(**repo) for repo in collector.repositories if filter_set.clean(repo)]
# NEW
# some of these should use the merge api
def make_pull_requests(magic, repos, *args):
    head_branch, head_org, base_branch, base_org, title, message = args
    for repo in repos:
        text = magic.git_api_pull_request(repo, head_branch, head_org, base_branch, base_org, title, message)
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
    # if len(releases) != len(byte_exercise_repos):
    #     raise "Out Of Sync"

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

# def update_these_repos(*repo_names):
    
#     git_update = repo_manager.githubEXT
#     ba_repos = build_repo_set_that_starts_with('ByteAcademyCo', repo_names)
#     # for repo in ba_repos:
#     #     git_update.git_api_get_master_sha(repo)

#     be_repos = build_repo_set_that_starts_with('ByteExercises',repo_names)
#     # data = ['fix','ByteAcademyCo', 'master', 'ByteAcademyCo', 'Patches']
#     # make_pull_requests(git_update, ba_repos, *data)
    # merge_pull_request(git_update, ba_repos, 'Merging patches.')
    # create_new_releases(git_update, ba_repos, 'patch', 'Moved tests to subTest manager.')
    # fork_latest_release_to_be(git_update, be_repos, ba_repos, 'Syncing with upstream...')

def update_repos(branch_name, title, message, release_type="patch"):
    """
    Use this to pull edits from the `branch_name` into ByteAcademyCo
    and then have those forked to ByteExercises after creating the releases.
    Works well if the branch only exists on the repos you want to edit.
    """
    git_update = repo_manager.githubEXT
    ba_repos = build_repo_set_that_starts_with('ByteAcademyCo','exercise-')
    be_repos = build_repo_set_that_starts_with('ByteExercises','exercise-')
    data = [branch_name, 'ByteAcademyCo', 'master', 'ByteAcademyCo', title, message]
    make_pull_requests(git_update, ba_repos, *data)
    merge_pull_request(git_update, ba_repos, message)
    create_new_releases(git_update, ba_repos, release_type, message)
    fork_latest_release_to_be(git_update, be_repos, ba_repos, 'Syncing with upstream...')
    merge_pull_request(git_update, be_repos, message)

# def main():
#     repo_names = [
#         'exercise-python-variables-datatypes','exercise-python-datastructures',
#         'exercise-python-operators-booleans-functions','exercise-python-loops-conditionals',
#         'exercise-python-temp-convert', 'exercise-python-is-palindrome', 
#         'exercise-python-reverse-polish-notation','exercise-python-get-started-with',
#         'exercise-python-learn-about-byte-resource', 'exercise-python-make-some-variables',
#         'exercise-python-fizzbuzz','exercise-python-triangles','exercise-python-fibonacci',
#         'exercise-python-factorial', 'exercise-python-string-scramble', 
#         'exercise-python-largest-prime-factor', 'exercise-python-sieve-of-erathosthenes',
#         'exercise-python-make-a-list', 'exercise-python-make-a-dictionary','exercise-python-print-a-list',
#         'exercise-python-make-a-variable', 'exercise-python-make-a-boolean', 'exercise-python-make-a-function'
#     ]
#     return update_these_repos(*repo_names)

if __name__ == "__main__":
    # main()
    # update_repos('collapse', 'Creating collapsible sections in README.md.', 'minor')
    # ba_repos = build_repo_set_that_starts_with('ByteAcademyCo','exercise-python')
    ba_repos = build_repo_set_from_repos('ByteAcademyCo', *['exercise-python-make-a-function','exercise-python-fizzbuzz'])
    be_repos = build_repo_set_from_repos('ByteExercises', *['exercise-python-make-a-function','exercise-python-fizzbuzz'])
    # be_repos = build_repo_set_that_starts_with('ByteExercises','exercise-')
    print(len(ba_repos))
    print(len(be_repos))
    # git = repo_manager.GitLocal()
    # STEP ONE: CLONE
    # clone_checkout(git, ba_repos, '../repositories/', 'edit-python-tests-patch')

    # STEP TWO: Add Commit
    # add_commit_edits(git, ba_repos, '../repositories/', 'edit-python-tests-patch', 'Bug fixes.')
    # push_edits(git, ba_repos, '../repositories/', 'edit-python-tests-patch')
    
    git_update = repo_manager.githubEXT
    
    # STEP THREE: MAKE PULL REQUEST
    args = ['edit-python-tests-patch', 'ByteAcademyCo', 'master', 'ByteAcademyCo','Bug fixes.', 'Fixed variable names and leading newline characters.']
    make_pull_requests(git_update, ba_repos, *args)
    input("Merge Pull Requests")
    merge_pull_request(git_update, ba_repos, 'Merging patches.')
    print(ba_repos)
    input("Create New Releases")
    # STEP FOUR: CREATE RELEASE AND FORK
    create_new_releases(git_update, ba_repos, 'patch', 'Bug fixes.')
    input("Fork Latest Release To Byte Exercise")
    fork_latest_release_to_be(git_update, be_repos, ba_repos, 'Syncing with upstream...')
    input("Merge Pull Request In Byte Exercise")
    merge_pull_request(git_update, be_repos, 'Syncing with upstream...')