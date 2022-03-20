import statistics
import yaml
import logging
import coloredlogs
import sys
import github
import re
import whatthepatch
from tqdm import tqdm
import pprint
from collections import Counter

coloredlogs.install(level='DEBUG')

filename = sys.argv[1]

logging.info("Welcome to the script, today we will open {}".format(filename))
file = open(filename, 'r')
lines = file.readlines()
# file.close()
logging.debug("File read! {} total lines".format(len(lines)))

commits = []
commit = ""
currentLines = [0,0]

def generate_statistics(code):
    comments = re.findall(r"(?:--|(?<!:)\/\/|\/\*|#)(.*?)(?:-->|$|\*\/)", code)
    # if (len(comments) > 0):
    #     print(comments)
    #     print(code)

    ccoco = sum([len(r[0]) for r in comments])

    statistics = {
        "coco": len(code),
        "ccoco": ccoco,
        "ϲcoco": len(re.findall(r"\s", code)),
        "scoco": len(re.findall(r"[^a-zA-Z0-9\s]", code)),
    }
    statistics["cococo"] = statistics["coco"] - statistics["ccoco"] - statistics["scoco"] - statistics["ϲcoco"]
    return statistics


def parse_commit(commit: github.Commit.Commit):
    total_stats = Counter()
    for file in commit.files:
        patch = file.patch
        if not patch:
            continue
        diff = list(whatthepatch.parse_patch(patch))[0].changes
        for change in diff:
            if change.new != None:
                stats = generate_statistics(change.line)
                total_stats.update(stats)
        # diff = PatchSet(patch)
    print(total_stats)

for idx, line in enumerate(tqdm(lines)):
    if line == "!!python/object:github.Commit.Commit\n":
        if (idx - currentLines[0]) > 0:
            currentLines[1] = idx - 1
            commit = ''.join(lines[currentLines[0]:currentLines[1]])
            commit = yaml.load(commit, Loader=yaml.Loader)

            parse_commit(commit)

            # commits.append(commit)
            currentLines[0] = idx
        # commit = ""

    # commit += line + "\n"


logging.info("Found {} commits".format(len(commits)))


# for commit in lines:
#     if len(commit.strip()) == 0:
#         continue

#     commit = '!!python/object:github.Commit.Commit\n' + commit
#     commit = yaml.load(commit, Loader=yaml.Loader)

#     logging.debug("I read commit {}".format(commit._sha))