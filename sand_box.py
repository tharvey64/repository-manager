import pprint

import repo_manager
import repo_filters




######################################################
######################################################
# These Functions Utilize The Git To Clone Repos, 
# Add Changed/Created Files, Commit Changes, 
# And Push Changes To Remote
######################################################
######################################################

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
        git.git_switch_branch(r, branch, path_to_repo)
        git.git_push(r, branch, path_to_repo)


######################################################
######################################################
# These Functions Utilize The Github API To Make/Close 
# Pull Requests On Github And Create Realeases
######################################################
######################################################

# make pull repuest that pulls test-update into master
# close pull request
# get the SHA from closing that pull request
# create new release at this SHA
# FORK TO BYTE EXERCISES

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

# NOT DONE YET

def fork_exercises_to_be(magic, repo_map, fork_to_org, title, body=''):
    """
    for each repo
        get the latest release 
        make a pull request 
    """
    # # Refactor To Use Repo Mapping
    # head_org = "ByteAcademyCo"

    # releases = {repo.name: (repo.owner.get('login'), magic.git_api_get_latest_release(repo)) for repo in byte_academy_repos}

    for repo_name, repos in repo_map.items():
        parent = repos.get('parent')
        fork = repos.get('fork')
        if fork:
            text = magic.git_api_pull_request(
                repo=repo, 
                head_branch=parent.default_branch, head_org=parent.owner.get('login'), 
                base_branch=fork.default_branch, base_org=fork.owner.get('login'), 
                title=title, body=body
            )

            if not repo._info.get('pull_request_number'):
                print("="*80)
                print("FAILED",repo.name)
                print("-"*30, text, "*"*80, sep='\n')
        else:
            # fork parent to ByteExercises
            text = magic.git_api_create_fork(parent, fork_to_org)
            print("%--___--%"*80)
            print("NEW FORK", repo_name)
            print("-"*30, text, "*"*80, sep='\n')

######################################################
######################################################
# These Functions Create Sets Of Repos That 
# Match Specific Filters
######################################################
######################################################

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

def build_repo_map(magic, parents, forks):
    repo_map = {repo.name: {'parent': repo} for repo in parents}
    for repo in forks:
        repo_detail = magic.git_api_get_repository(repo)
        parent = repo_detail.get('parent')
        repo_map[parent.get('name')]['fork'] = repo
        # pprint.pprint(repo_detail)
    return repo_map

######################################################
######################################################
# First Function Clones All Repos On BA
# Second Function Performs Update On Specific List of Repos
# Third Function Should Be Reevaluated 
######################################################
######################################################


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
    ba_repos = build_repo_set_that_starts_with('ByteAcademyCo','exercise-javascript')
    be_repos = build_repo_set_that_starts_with('ByteExercises','exercise-javascript')
    # main()
    # ba_repos = build_repo_set_that_starts_with('ByteAcademyCo','exercise-python')
    # be_repos = build_repo_set_that_starts_with('ByteExercises','exercise-python')
    # ba_repos = build_repo_set_from_repos('ByteAcademyCo', *['exercise-python-make-a-function','exercise-python-fizzbuzz'])
    # be_repos = build_repo_set_from_repos('ByteExercises', *['exercise-python-make-a-function','exercise-python-fizzbuzz'])
    # be_repos = build_repo_set_that_starts_with('ByteExercises','exercise-javascript')
    print(len(ba_repos))
    print(len(be_repos))
    # LOCAL EDITS ONLY
    # git = repo_manager.GitLocal()
    # STEP ONE: CLONE
    # clone_checkout(git, ba_repos, '../repositories/', 'feedback-edits')

    # STEP TWO: Add Commit
    # add_commit_edits(git, ba_repos, '../repositories/', 'javascript-tests', 'Edits to lesson code snippets. Adding tests for all javascript exercises that require tests.')
    # push_edits(git, ba_repos, '../repositories/', 'javascript-tests')
    
    # GITHUB ACTIONS START HERE
    git_update = repo_manager.githubEXT
    repo_name_mapping = build_repo_map(git_update, ba_repos, be_repos)
    # # # STEP THREE: MAKE PULL REQUEST
    print("MAKE PULL REQUESTS")
    # # head_branch, head_org, base_branch, base_org, title, message = args
    
    ready = False
    while not ready:
        head_branch = input('Enter head branch for PR:\t').strip()
        head_org = input('Enter head branch Organization:\t').strip()
        base_branch = input('Enter base branch for PR:\t').strip()
        base_org = input('Enter base branch Organization:\t').strip()
        title = input('Enter the title that will appear on the PR:\t').strip()
        message = input('Enter the message that will appear on the PR:\t').strip()
        print('head_branch = '+head_branch, 'head_org = '+head_org, 'base_branch = '+base_branch, 'base_org = '+base_org, 'title = '+title, 'message = '+message, sep="\n")
        ready = input("Press Enter to make PRs.(Type anything to restart)") == ''
    # args = ['javascript-tests', 'ByteAcademyCo', 'master', 'ByteAcademyCo','Adding JavaScript tests.', 'Created initial set of JavaScript tests.']
    args = [head_branch, head_org, base_branch, base_org, title, message]
    
    make_pull_requests(git_update, ba_repos, *args)

    print("Merge Pull Requests")
    print("Enter message that will appear for the closeing of the PR")
    
    ready = False
    while not ready:
        commit_message = input("Message for merging PRs: (Extra detail to append to automatic commit message.)\n").strip()
        ready = input("Press Enter to merge PRs.(Type anything to change message)") == ''
    
    merge_pull_request(git_update, ba_repos, commit_message)
    
    # ??
    pprint.pprint(ba_repos)
    print("*"*100)
    print("*"*100,"BE")
    pprint.pprint(be_repos)
    input("Create New Releases(Press Enter)")
    # # # STEP FOUR: CREATE RELEASE AND FORK
    
    ready = False
    while not ready:
        release_type = input("Please enter release type(major/minor/patch):\t").strip()
        release_body = input("Enter tag body (`string` Text describing the contents of the tag):\n").strip()
        ready = input("Press Enter to create new releases.(Type anything to change release type and body)") == ''
    
    create_new_releases(git_update, ba_repos, release_type, release_body)
    
    pprint.pprint(ba_repos)
    print("*"*100)
    print("*"*100,"BE")
    pprint.pprint(ba_repos)

    input("Fork Latest Release To Byte Exercise(Press Enter)")
    input("Head must be a branch.(Set to master)")
    # Use Mapping Here
    # fork_latest_release_to_be(git_update, be_repos, ba_repos, 'Syncing with upstream...')
    # **New**
    fork_exercises_to_be(git_update, repo_name_mapping, "ByteExercises", title="Syncing with upstream...", body='')

    input("Merge Pull Request In Byte Exercise(Press Enter)")

    # Adjust for new work flow?
    merge_pull_request(git_update, be_repos, 'Syncing with upstream...')




