from github_api import GithubAPI

try:
    from local_config import config
except ImportError:
    sys.stderr.write(
"""
Warning: Can't find the file 'local_config.py' in the directory
containing {}. It appears you've customized things. Create {} in
the directory containing repo_manager.py and file the format provided
in local_config.py.md.
""".format(__file__))
    sys.stderr.write("\nFor debugging purposes, the exception was:\n\n")
    traceback.print_exc()


_ORG = 'ByteAcademyCo'

def 