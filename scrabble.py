import copy
from enum import Enum, auto
import math
from typing import List
import enchant
import numpy as np
import re
from functools import lru_cache

class Direction(Enum):
    Down = auto()
    Right = auto()

uk_dictionary = enchant.Dict("en_UK")
us_dictionary = enchant.Dict("en_US")

class Scrabble:
    DIMENSION = 15

    def __init__(self):
        self.matrix = np.array([[None for x in range(self.DIMENSION)] for y in range(self.DIMENSION)])
        # matrix[x][y]
        #   x↑ = right
        #   y↑ = down

    def suggest_positions(self, word):
        word_size = len(word)
        candidate_positions = []

        for i, letter in enumerate(word):
            positions = list(zip(*np.where(self.matrix == letter)))

            for col, row in positions:
                writeable = True

                # Determine if we have enough space to write the word vertically
                if i <= row and row + word_size - i < self.DIMENSION:
                    for j in range(1, i + 1):
                        char = self.matrix[col][row - j]
                        if (char is not None) and char != word[i - j]:
                            writeable = False
                            break
                    for j in range(1, word_size - i):
                        char = self.matrix[col][row + j]
                        if (char is not None) and char != word[i + j]:
                            writeable = False
                            break
                    if writeable:
                        candidate_positions.append((col, row - i, Direction.Down))
                writeable = True
                # Attempt to write horizontally
                if i <= col and col + word_size - i < self.DIMENSION:
                    for j in range(1, i + 1):
                        char = self.matrix[col - j][row]
                        if (char is not None) and char != word[i - j]:
                            writeable = False
                            break
                    for j in range(1, word_size - i):
                        char = self.matrix[col+j][row]
                        if (char is not None) and char != word[i + j]:
                            writeable = False
                            break
                    if writeable:
                        candidate_positions.append((col - i, row, Direction.Right))
        return set(candidate_positions)

    def put(self, word, location, direction):
        word = word.lower()
        for idx, c in enumerate(word):
            x = location[0]
            y = location[1]
            if direction == Direction.Down:
                y += idx
            elif direction == Direction.Right:
                x += idx
            self.matrix[x][y] = c
        self.score.cache_clear()

    def put_best(self, word):
        word = word.lower()

        candidate_positions = self.suggest_positions(word)

        best_score = None
        best_scrabble = None
        for pos in candidate_positions:
            s2 = copy.deepcopy(self)
            s2.put(word, (pos[0], pos[1]), pos[2])
            if s2.is_valid():
                score = s2.score()
                if best_score is None or score > best_score:
                    best_score = score
                    best_scrabble = s2

        if best_scrabble is not None:
            self.matrix = best_scrabble.matrix
            self.score.cache_clear()
        else:
            return True

    def put_first_word(self, word):
        middle = math.floor(self.DIMENSION / 2)

        hor = copy.deepcopy(self)
        ver = copy.deepcopy(self)

        if len(word) + middle >= self.DIMENSION:
            start = self.DIMENSION - len(word)
            if start < 0:
                # fail
                return False
            hor.put(word, (start, middle), Direction.Right)
            ver.put(word, (middle, start), Direction.Down)
        else:
            hor.put(word, (middle, middle), Direction.Right)
            ver.put(word, (middle, middle), Direction.Down)

        results = [ hor, ver ]
        return [r for r in results if r.is_valid()]


    def put_best_many(self, words):
        all_candidates : List[Scrabble] = [ self ]

        # Put first word in the middle of scrabble
        while len(self.get_words()) == 0 and len(words) > 0:
            init_scrabble = self.put_first_word(words[0])
            words.pop(0)
            if init_scrabble is not False and len(init_scrabble) > 0:
                all_candidates = init_scrabble
                break

        # Add every word consecutively to the candidate Scrabbles
        for word in words:
            word = word.lower()
            new_candidates = []
            # For every candidate Scrabble, find all possible candidate
            # sub-Scrabbles
            for candidate in all_candidates:
                positions = candidate.suggest_positions(word)
                for pos in positions:
                    c = copy.deepcopy(candidate)
                    c.put(word, (pos[0], pos[1]), pos[2])
                    if c.is_valid():
                        new_candidates.append(c)
            if len(new_candidates) > 0:
                # No need to keep old Scrabbles, just store the latest good Scrabbles
                all_candidates = new_candidates
        # All possible Scrabbles calculated, now find the best one
        best = max(all_candidates, key=lambda c: c.score())
        self.matrix = best.matrix
        self.score.cache_clear()



    @lru_cache(maxsize=None)
    def score(self):
        return sum([ self._word_score(w) for w in self.get_words() ])

    def _word_score(self, word, modifier=None):
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

    def is_valid(self):
        return all([uk_dictionary.check(word) or us_dictionary.check(word) for word in self.get_words()])

    def get_words(self):
        words = []

        # Vertical words

        for i in range(self.DIMENSION):
            word = ""
            for j in range(self.DIMENSION):
                char = self.matrix[i][j]
                is_letter = char != ' ' and char is not None
                if is_letter:
                    # We have a normal character that will
                    # form the word
                    word += char

                if not is_letter or j == self.DIMENSION - 1:
                    # We have a new word!! maybe
                    if len(word.strip()) <= 1:
                        word = ""
                        continue

                    # We actually have a new word!
                    words.append(word)
                    word = ""
            word = ""
            for j in range(self.DIMENSION):
                char = self.matrix[j][i]
                is_letter = char != ' ' and char is not None
                if is_letter:
                    # We have a normal character that will
                    # form the word
                    word += char

                if not is_letter or i == self.DIMENSION - 1:
                    # We have a new word!! maybe
                    if len(word.strip()) <= 1:
                        word = ""
                        continue

                    # We actually have a new word!
                    words.append(word)
                    word = ""

        return words


    def process_commit_message(message):
         # First line of commit only
        message = message.partition('\n')[0]
        # First 80 git characters only
        message = message[0:80]
        words = re.findall(r"[A-Za-z]+", message)
        # First 7 characters from each word... No overdoing it
        words = [w[0:7] for w in words]

        return words


    def __str__(self):
        str = ""
        for y in range(self.DIMENSION):
            for x in range(self.DIMENSION):
                if self.matrix[x][y] is None:
                    str += ' '
                else:
                    str += self.matrix[x][y]
            str += "\n"
        return str

if __name__ == "__main__":
    s = Scrabble()

    # s.put("lite", (2,2), Direction.Down)
    # s.put("baby", (2,2), Direction.Right)
    # s.put("beard", (4,2), Direction.Down)

    s.put_best_many(["establish", "lite", "EnumAttr", "fault", "TFL_DimensionTypeAttr"])
    print(s)

    # for position in s.suggest_positions("daredevilitiness"):
    #     print("SUGGESTED POSITION:")
    #     s2 = copy.deepcopy(s)
    #     s2.put("daredevilitiness", (position[0], position[1]), position[2])
    #     print(s2)
    #     print(s2.is_valid())

    # print(s)

    # print(s.get_words())
    # print(s.is_valid())
    # print(s.suggest_positions("baeeby"))
    # print(s.suggest_positions("boy"))
