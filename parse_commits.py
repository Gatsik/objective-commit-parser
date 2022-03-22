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


def code_quantity(code):
    comments = re.findall(r"(?:--|(?<!:)\/\/|\/\*|#)(.*?)(?:-->|$|\*\/)", code)
    # if (len(comments) > 0):
    #     print(comments)
    #     print(code)

    ccoco = sum([len(r) for r in comments])

    statistics = {
        "coco": len(code),
        "ccoco": ccoco,
        "ϲcoco": len(re.findall(r"\s", code)),
        "scoco": len(re.findall(r"[^a-zA-Z0-9\s]", code)),
    }
    statistics["cococo"] = statistics["coco"] - statistics["ccoco"] - statistics["scoco"] - statistics["ϲcoco"]
    return statistics

def scrabble_score(word, modifier=None):
    word = word.lower()
    score = 0
    for idx, c in enumerate(word):
        if idx >= 7:
            # Large word limit
            break

        character_score = 0
        if c in [ 'a', 'e', 'i', 'o', 'u', 'l', 'n', 's', 't', 'r' ]:
            character_score = 1
        elif c in [ 'd', 'g' ]:
            character_score = 2
        elif c in [ 'b', 'c', 'm', 'p' ]:
            character_score = 3
        elif c in [ 'f', 'h', 'v', 'w', 'y' ]:
            character_score = 4
        elif c in [ 'k' ]:
            character_score = 5
        elif c in [ 'j', 'x' ]:
            character_score = 8
        elif c in [ 'q', 'z' ]:
            character_score = 10
        else:
            # Some number or symbol or emoji or something. These kinds of characters can be of very high quality, or not.
            # Let's just forget they exist at all
            character_score = 0
        score += character_score
    return score

def commit_quality(message):
    words = message.split()
    score = sum([scrabble_score(word) for word in words])
    return score

def parse_commit(commit: github.Commit.Commit):
    print(commit_quality(commit.commit.message))
    total_stats = Counter()
    for file in commit.files:
        patch = file.patch
        if not patch:
            continue
        diff = list(whatthepatch.parse_patch(patch))[0].changes
        for change in diff:
            if change.new != None:
                stats = code_quantity(change.line)
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



# Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis sit amet risus ut enim varius
# condimentum. Sed nisi nisl, fermentum vitae urna nec, maximus rhoncus tortor. Cras pretium
# facilisis augue nec fermentum. Aliquam lacus est, rutrum a efficitur id, varius a mi. Nullam
# suscipit, lacus eget luctus tincidunt, sem tellus pellentesque lectus, id aliquam dui purus
# ultrices risus. Donec finibus est diam, sed semper massa efficitur quis. Phasellus non laoreet
# ipsum. Phasellus eu hendrerit neque. In fermentum massa quis ipsum ullamcorper, sed sollicitudin
# nisi euismod. Curabitur vitae molestie libero. Maecenas neque urna, efficitur ac tincidunt ut,
# venenatis vitae metus. Etiam ipsum lectus, maximus sit amet venenatis vitae, posuere eget nulla.
# Nullam eu nisi pellentesque, luctus ipsum vitae, rhoncus augue.

# Fusce convallis massa id purus varius, vel tempus urna eleifend. Etiam ut venenatis quam.
# Suspendisse eu lacus tincidunt, porttitor enim eget, facilisis nibh. Donec elementum dapibus metus
# eget vulputate. Nulla hendrerit egestas sagittis. Quisque eget augue nec purus luctus tempor in eu
# leo. Curabitur vel nibh ut ligula vestibulum eleifend at et nibh. Integer vitae lectus sed augue
# viverra placerat eu efficitur sem. Donec egestas consequat magna eget lacinia. Phasellus nec
# vestibulum neque. Maecenas at turpis et enim dictum tristique pulvinar sit amet mauris. In hac
# habitasse platea dictumst. Etiam vitae ligula et risus vestibulum tempor id sed mi. Integer
# porttitor posuere mi, vel mattis enim. Donec accumsan pellentesque finibus. Curabitur nec
# convallis mi.

# Etiam tellus orci, bibendum a fringilla eget, blandit vel velit. Nulla malesuada nibh sit amet
# lacus egestas, eget egestas augue imperdiet. Fusce at volutpat ipsum. Duis a enim quis ligula
# posuere molestie. Curabitur dictum pretium ipsum sit amet mollis. Quisque sollicitudin lorem
# aliquet dictum gravida. Nunc at nisl fermentum, malesuada lacus at, eleifend lorem. Nulla at risus
# nec velit euismod vulputate eu quis nulla. Vivamus quis orci leo. Vestibulum nec nunc sem. Fusce
# non quam eget elit tempus mattis. Cras a tortor id ligula egestas posuere.

# Nullam dui nunc, faucibus placerat eros nec, volutpat rhoncus purus. Proin eget vehicula lorem, a
# auctor mi. Proin lobortis turpis a justo aliquam, eu fringilla diam ultricies. Vestibulum
# facilisis lectus quis dolor elementum consequat. Maecenas vitae aliquet sem. Curabitur dictum orci
# ut porta efficitur. Quisque pretium, enim sed convallis dictum, est eros iaculis magna, ac tempor
# tellus massa id lacus. Nullam blandit turpis vitae felis suscipit sagittis. Cras a nisi hendrerit,
# fringilla sem at, rutrum eros. Pellentesque sit amet auctor ipsum.

# Nam sed vehicula tellus, vitae lobortis nisl. Donec id posuere libero. Vestibulum volutpat
# accumsan libero, suscipit aliquam nisl maximus in. Nulla a condimentum ex, sed vulputate turpis.
# Suspendisse malesuada sapien a pulvinar convallis. Donec id congue nisi, in consequat sem. Cras
# purus metus, pellentesque id purus a, sagittis interdum risus. Etiam venenatis, neque id pharetra
# pellentesque, nisi augue lacinia orci, quis laoreet ipsum nisi volutpat libero. Duis ac interdum
# erat. Aliquam eget varius nisi. Donec vehicula lobortis nulla, sed congue ligula porta et. Aenean
# egestas diam eget massa aliquet, vel fermentum elit porttitor. Duis luctus, sapien et luctus
# interdum, velit dui porttitor neque, a tristique tellus elit in elit. Nunc pellentesque eros id
# velit suscipit, vitae suscipit nisi gravida. Aliquam at tempor velit, quis suscipit felis. Nullam
# tempor vel diam et tempus.

# Morbi id sem et ligula pulvinar luctus. Nunc eu elit lorem. Suspendisse arcu elit, bibendum at
# orci in, consectetur aliquet justo. Morbi mattis aliquet velit quis gravida. Proin purus justo,
# tristique ac mollis nec, pellentesque non urna. Nullam et purus faucibus, maximus turpis in,
# convallis mauris. Vivamus iaculis, sem quis posuere egestas, ipsum odio feugiat libero, vitae
# hendrerit purus nisl mattis mi. Cras vel metus at urna dapibus gravida. Donec nec egestas arcu.
# Praesent nec quam sed ante hendrerit sollicitudin. Cras ornare nibh nec mauris ultrices suscipit.

# Proin volutpat dolor lorem, vel bibendum orci tempus vitae. Proin finibus vel neque et luctus. Sed
# feugiat, libero at commodo semper, turpis justo condimentum elit, eget fermentum neque augue non
# risus. Duis non finibus metus, sit amet imperdiet leo. Aenean fermentum semper faucibus. Orci
# varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Vivamus sit amet
# diam a lacus convallis efficitur et eu quam. Fusce eget dapibus ligula, non feugiat dui. Vivamus
# feugiat sapien in aliquet bibendum. Curabitur sit amet sapien non justo sollicitudin interdum
# commodo in urna. Aenean libero erat, ultrices vitae cursus pharetra, efficitur non odio. Sed
# mattis lacus sollicitudin, lobortis mauris at, ullamcorper diam. Ut porttitor vel diam vel
# malesuada. Fusce viverra tellus a felis tempor maximus. Mauris metus mauris, tincidunt eget
# gravida vitae, pellentesque id quam. Vivamus tristique ligula vel venenatis consequat.

# Vestibulum feugiat dolor vitae massa hendrerit suscipit. Maecenas et mauris tellus. Nunc accumsan
# sagittis fringilla. Maecenas pretium id metus id porta. Proin interdum mauris non lectus
# convallis, et fermentum tellus facilisis. Vestibulum felis ligula, condimentum sed efficitur et,
# efficitur id tortor. Donec hendrerit justo at enim hendrerit volutpat eget vitae velit. Vestibulum
# pharetra sollicitudin mauris, nec dapibus nisi volutpat vitae. Aenean sollicitudin massa non
# libero cursus, id fermentum urna eleifend.

# Integer pellentesque lorem eu sapien condimentum, ac scelerisque enim blandit. Ut accumsan ac nibh
# nec sodales. Fusce id metus ut ligula aliquet elementum. Maecenas in justo tristique, malesuada
# eros id, consectetur est. Praesent est velit, sagittis ut elementum vel, consectetur ut nisi. Ut
# condimentum, orci sodales dignissim rhoncus, ex purus porttitor lacus, ut euismod augue ante ut
# ante. Suspendisse potenti. Sed eget augue ante. Ut hendrerit ipsum sed sem suscipit, eu suscipit
# nunc gravida. Sed erat arcu, posuere in commodo vel, convallis in neque. Sed bibendum mi quam,
# pellentesque sagittis tortor faucibus at. Sed neque erat, dictum et mi a, consequat rutrum elit.
# Pellentesque nulla justo, finibus eget arcu feugiat, fermentum pulvinar augue. Quisque vestibulum,
# nunc et viverra efficitur, velit augue facilisis sem, nec fermentum libero ante et sem.

# Maecenas orci nibh, mattis a pulvinar at, convallis sed nunc. Fusce consequat quis quam non
# vehicula. Cras ultrices tellus sapien, quis consequat dui luctus id. Aliquam dapibus, quam quis
# sagittis pretium, quam mi pretium tellus, non facilisis mauris tortor sed felis. Aliquam eu lorem
# non justo sodales imperdiet vel quis massa. Donec at maximus magna. Etiam vehicula venenatis
# dignissim. Donec sollicitudin est orci, vel ultricies ligula pharetra hendrerit.

# Interdum et malesuada fames ac ante ipsum primis in faucibus. Nullam commodo lectus in neque
# consequat congue. Nunc aliquam sem nec aliquet blandit. Mauris elementum ipsum ipsum, non
# pellentesque purus porttitor vitae. Cras malesuada dui nec ante vulputate efficitur. Vivamus
# lobortis dolor non fermentum ullamcorper. Nunc egestas velit eget venenatis fermentum. Nam
# sagittis urna quam, vel vehicula turpis pellentesque non.

# Curabitur quis tempus sem, eget interdum felis. Sed ac ipsum eget tortor dignissim aliquam a non
# nisl. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis
# egestas. Aenean pulvinar quam tellus, sit amet aliquam turpis auctor a. Morbi sollicitudin quam
# quis est congue, vitae tincidunt ipsum vulputate. Curabitur feugiat enim odio, ut tristique eros
# consectetur vitae. Sed ultricies purus ut ligula sollicitudin tempus.

# Maecenas mattis euismod eleifend. Nullam varius, arcu et posuere commodo, risus magna congue odio,
# in rutrum libero dui vel nunc. Sed et enim volutpat tortor imperdiet lacinia. Vestibulum et
# efficitur nisl, sed aliquam velit. Nunc at sem vitae sem placerat tincidunt in eu mauris. Etiam
# volutpat id velit quis vulputate. Donec finibus sem in lorem auctor dictum. Vivamus est odio,
# lobortis hendrerit mollis vitae, sodales feugiat tellus. Fusce vulputate diam rhoncus pulvinar
# finibus. Sed id nibh sagittis est vehicula commodo. Duis eget libero viverra, posuere velit et,
# bibendum ante. Sed id sagittis ipsum, eu venenatis tellus. Maecenas eget gravida leo. Ut congue
# aliquet feugiat. Sed varius hendrerit tellus non interdum.

# Ut venenatis, enim eget mattis finibus, mauris urna congue nunc, quis tristique elit ante
# condimentum ligula. Suspendisse in scelerisque tellus, non vulputate lectus. Maecenas consectetur
# tortor sit amet vulputate molestie. Proin et diam lorem. Morbi id ex tempor, pellentesque diam ut,
# consectetur tortor. Ut id erat eget magna mattis dignissim. Cras congue, lacus facilisis auctor
# pellentesque, metus magna faucibus eros, quis rhoncus libero sem quis nisi. Aliquam erat volutpat.
# Nam id nulla id leo condimentum elementum. Vestibulum porttitor, sapien eget placerat fringilla,
# metus tellus varius neque, vel rhoncus augue diam sodales ante. Maecenas malesuada aliquam
# hendrerit. Curabitur sodales tincidunt leo, non convallis risus ultricies semper. Quisque molestie
# vestibulum ex, non auctor felis pellentesque in. Mauris faucibus dignissim volutpat. Interdum et
# malesuada fames ac ante ipsum primis in faucibus. Mauris ligula quam, viverra eu ex at, facilisis
# sollicitudin ipsum.

# Donec ut odio eu libero laoreet commodo. Aliquam pulvinar sapien ipsum, quis porttitor purus
# aliquam vel. Praesent tincidunt viverra dolor eu auctor. Ut risus neque, ornare non massa sit
# amet, tincidunt pharetra ipsum. Vestibulum molestie quis ligula quis aliquam. Nam interdum, ante
# in congue varius, diam felis laoreet urna, et cursus mi velit et leo. Nunc scelerisque neque at
# lorem mollis blandit. Nullam aliquet lacus sit amet ante semper, sit amet mattis elit congue.