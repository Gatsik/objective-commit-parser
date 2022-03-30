from github import Github
import json
from types import SimpleNamespace
import pickle
import yaml

github_token = "???"
g = Github(github_token)

repositories = g.search_repositories(query='language:c')

all_repositories = []

count = 0

try:
    for repo in repositories:
        print(repo.name)
        all_repositories.append(repo)
        count += 1
        if count > 60:
            break
except BaseException as e:
    print("For some reason, the program stopped. I think you can use Algorithms to display why, but I don't remember how and it's very late: {}".format(e))
finally:
    pickle.dump( all_repositories, open( "c_repositories.p", "wb" ) )
    with open("c_repositories.yml", "w") as file:
        file.write(yaml.dump(all_repositories))




