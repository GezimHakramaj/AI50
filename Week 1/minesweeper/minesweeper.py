import itertools
import random
import copy


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def getNeighbors(self, cell):

        neighbors = set()

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) != cell and 0 <= i < self.height and 0 <= j < self.width:
                    neighbors.add((i, j))

        return neighbors


    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(self.cells): # If the sentence count is = to # of cells then they are all mines
            return self.cells # Return the set
        return None # Otherwise return none

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0: # If the count is 0 then all cells are 0
            return self.cells # Return the cell set
        return None # Return None otherwise

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells: # If the cell is in the sentences cell list
            self.cells.remove(cell) # Remove the cell
            self.count -= 1 # Decement the count by one to show the sentence has one less mine

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells: # If the cell is in the sentences cell list
            self.cells.remove(cell)  # Remove it

    def isSubSet(self, other): # Helper to check is subsets
        return self.cells.issubset(other.cells)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge.copy():
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        ms = Minesweeper()

        self.moves_made.add(cell)  # Add selected cell to moves made set
        self.mark_safe(cell)  # Add selected cell to safe cells
        self.knowledge.append(Sentence(ms.getNeighbors(cell), count))  # Add newly created sentence with neighboring cells and count of mines bordering said cell

        for sentence in self.knowledge.copy(): # Loop through each sentence
            self.updateKnowledge(sentence) # Update sentences based on the newly added sentence

        for sentence in self.knowledge.copy(): # Loop through each sentence
            for sentence2 in self.knowledge.copy(): # Loop through each sentence again
                if sentence != sentence2 and sentence.isSubSet(sentence2): # If the sentence is not the same and sentence1 is a subset of sentence2
                    subSentence = Sentence(sentence2.cells - sentence.cells, sentence2.count - sentence.count) # Create a new sentence with cells sentenc2-1 and count2-1
                    if subSentence not in self.knowledge: # If that new sentence is not already in knowledge
                        self.knowledge.append(subSentence) # Add it

        for sentence in self.knowledge.copy(): # Loop through each sentence
            self.updateKnowledge(sentence) # Update sentences based on newly added subsets if any

        # print("Safes", self.safes) # Test purposes to print out safes, mines and sentences
        # print("Mines", self.mines)
        # for sentence in self.knowledge:
           # print(sentence, end="\n")

    def updateKnowledge(self, sentence):
        if sentence.count == 0: # If the sentence's count is 0 that means that no mines are in that sentence
            for c in sentence.cells.copy(): # Loop through each cell
                self.mark_safe(c) # Mark each cell as safe also updating every other sentence containing the cell
            self.knowledge.remove(sentence) # Remove the sentence as it doesnt contain possible mine/safe moves
        elif sentence.count == len(sentence.cells): # If the sentence count is equal to # of cells than all cells are mines
            for c in sentence.cells.copy(): # Loop through each cell
                self.mark_mine(c) # Mark each cell as a mine
            self.knowledge.remove(sentence) # Remove the sentence
        else:  # Else the sentence contains possible mines or safe moves by count != to # of cells
            for c in sentence.cells.copy():  # Loop through cells
                if c in self.safes:  # If that cell is in safes
                    self.mark_safe(c)  # Mark that cell as safe for all other sentences
                elif c in self.mines:  # If the cell is in mines
                    self.mark_mine(c)  # Mark the cell as a mine for all other sentences

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes: # Loop through all safe nodes
            if cell not in self.moves_made: # Check if that node was already made
                return cell # Return it
        return None # Else return none

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        ms = Minesweeper()
        # To dynamically check for size of the minesweeper grid
        if ms.width * ms.height - len(ms.mines) == len(self.moves_made): # If size of the board (height*width) - # mines is equal to moves made then there are no possible moves remaining
            return None # Return none
        while True:
            move = (random.randint(0, 7), random.randint(0, 7)) # Create a random move (i, j)
            if move not in self.moves_made and move not in self.mines: # If the move is in moves already mad or is a mine
                return move # Return the move

