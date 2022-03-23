from enum import Enum, auto
import enchant
import numpy as np

class Direction(Enum):
    Down = auto()
    Right = auto()

uk_dictionary = enchant.Dict("en_UK")
us_dictionary = enchant.Dict("en_US")

class Scrabble:
    DIMENSION = 15

    def __init__(self):
        self.matrix = np.array([[None for x in range(self.DIMENSION)] for y in range(self.DIMENSION)])

    def suggest_positions(self, word):
        word_size = len(word)
        word_endings_pos = []
        word_beginings_pos = []

        for i, letter in enumerate(word):
            print("LETTER", i, letter)
            positions = list(zip(*np.where(self.matrix == letter)))
            for row, col in positions:
                print(row, col)
                writeable = True

                # Determine if we have enough space to write the word horizontally
                if i <= row and row + word_size - i < self.DIMENSIONS:
                    print("Writing horizontally")
                    print("Before i")
                    for j in range(1, i + 1):
                        char = self.matrix[row - j][col]
                        if char != None or char != word[i - j]:
                            print("Aborting")
                            writeable = False
                            break
                    print("After i")
                    for j in range(1, word_size - i):
                        print(row + j, col)
                        char = self.matrix[row + j][col]
                        if char != None or char != word[i + j]:
                            print("Aborting")
                            writeable = False
                            break
                    if writeable:
                        return ([row, col, Direction.Down])
                # Attempt to write vertically
                if i <= column and row + word_size - i < self.DIMENSIONS:
                    print("Writing vertically")
                    print("Before i")
                    for j in range(1, i + 1):
                        char = self.matrix[row][col - j]
                        print(row, col-j)
                        if char != None or char != word[i - j]:
                            print("Aborting")
                            writeable = False
                            break
                    print("After i")
                    for j in range(1, word_size - i):
                        print(row, col+j)
                        char = self.matrix[row][col+j]
                        if char != None or char != word[i + j]:
                            print("Aborting")
                            writeable = False
                            break
                    if writeable:
                        return ([row, col, Direction.Right])
        return

    def put(self, word, location, direction):
        for idx, c in enumerate(word):
            x = location[0]
            y = location[1]
            if direction == Direction.Down:
                y += idx
            elif direction == Direction.Right:
                x += idx
            self.matrix[x][y] = c

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

    s.put("bar", (2,2), Direction.Down)
    s.put("baby", (2,2), Direction.Right)

    print(s)

    print(s.get_words())
    print(s.is_valid())
    print(s.suggest_positions("bar"))