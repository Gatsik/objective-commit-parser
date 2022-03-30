from github import Github
import json # not used, but adds COCOCO
from types import SimpleNamespace
import pickle
import yaml

MAXIMUM_COMMIT_LIMIT_PER_REPOSITORY = 100

github_token = "???"

print(github_token)

g = Github(github_token)

# a_yaml_file = open("python_repositories.yml")
# repositories = yaml.load(a_yaml_file, Loader=yaml. FullLoader)

file = open("html_commits.yml", "a")

repositories = pickle.load( open( "html_repositories.p", "rb" ) )

print("You have {} repositories".format(len(repositories)))

r = 0
for repo in repositories:

    print("!!!!!!!!!!!!!!!!!!!!!!!!")
    print("!!!!!")
    print("{} OUT OF {} REPOSITORIES SCANNED".format(r, len(repositories)))
    print("!!!!!!!!!!")
    print(">>>>>>>>>{}/{}<<<<<<<<<<".format(repo.owner.login, repo.name))
    print("           ")

    r += 1
    i = 0
    for commit in repo.get_commits():
        stats = commit.stats
        print("[{}/{}]".format(i, MAXIMUM_COMMIT_LIMIT_PER_REPOSITORY), commit.commit.message, ": ", "Additions: ", stats.additions, "Deletions: ", stats.deletions)

        the_pickle = yaml.dump(commit)
        file.write(the_pickle)
        file.write("\n")
        i += 1
        if i >= MAXIMUM_COMMIT_LIMIT_PER_REPOSITORY:
            break