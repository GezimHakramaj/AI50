import sys
import copy
import math
import random

from crossword import *

# TODO
        #   FIX SORTING BY VALUES
        #   FIX SORTING BY ARCS
        #   RETURN VARIABLE
        #   CONTINUE OPTIMIZING
class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        for variable in self.domains: # Loop through each variable in domains
            for word in self.domains[variable].copy(): # Loop through each word in the set of domains[variable]
                if len(word) != variable.length: # If the word's length is not equal to the length of the row/column needed in crossword
                  self.domains[variable].remove(word) # Remove it as it cannot fit in that row/column deeming the word invalid for the possible words

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        revised = False # Set revised to false intiially
        overlap = self.crossword.overlaps[x,y] # Get the overlap of x and y
        if overlap == None: # If its none return false as no revision was made
            return revised

        for xword in self.domains[x].copy(): # Else for each word in x's domain
            consistent = False # Set consistent to false
            for yword in self.domains[y]: # For each word in y's domain
                if xword[overlap[0]] == yword[overlap[1]]: # If the overlap of both words is correct
                    consistent = True # That means this word works with one possibility in y's domain
                    break # Break out of the loop as we only care if it works with one possible word
            if not consistent: # If its not consistent
                revised = True # Set revised to true as we will make a revision
                self.domains[x].remove(xword) # Remove that word from x's domain as it is conflicting with its neighbors overlap.

        return revised # Return revised


    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue = [] # Intialize list
        if arcs == None: # If arcs = none
            for x in self.crossword.overlaps: # Add every arc possible in the problem
                queue.append(x)
        else: # Else the queue = arcs
            queue = arcs

        while len(queue) != 0: # While queue not empty
            variables = queue.pop(0) # Pop the first element
            x = variables[0]
            y = variables[1]
            if self.revise(x, y): # Check if the two need revision
                if self.domains[x] == None: # Check if x's domain is not None
                    return False # return False if it is
                neighbors = self.crossword.neighbors(x) # Otherwise get all the remaining neighbors of x
                for z in neighbors: # Loop through all
                    if z != y: # For all neighbors z that are not y
                        queue.append((z, x)) # Add to the queue z and x as a tuple to secure arc consistency between them as well because
                                             # since we made a revision to x and y, there is a chance that z and x will become inconsistent
        return True # Return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        if len(assignment) == len(self.domains): # If the assignment has every variable inside of it
            for x in assignment: # Check each variable for values
                if assignment[x] == None: # If each variable doesnt have a None value
                    return False # Return False if a value is None
            return True # Return True

        return False # Return False if the assignment isn't of same length as self.domains

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        for x in assignment: # Loop
            if len(assignment[x]) != x.length: # If the value of the variable is not equal to the required length
                return False # Return False
            for y in assignment: # Loop over each variable
                if x != y: # If x is not y continue with the loop
                    if assignment[x] == assignment[y]: # If each variable doesnt have a distinct value then return False
                        return False
                    overlap = self.crossword.overlaps[x, y] # Get the overlap for both variables
                    if overlap == None: # If the two variables do not have a overlap continue
                        continue
                    if assignment[x][overlap[0]] != assignment[y][overlap[1]]: # If there is a conflicting character between values then return false
                        return False
        return True # Otherwise return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        words = dict() # Create an empty dict
        for word in self.domains[var]: # Loop through each word in var's domain
            words[word] = 0 # Assign each word in words dict a value of 0 intialliy

        neighbors = self.crossword.neighbors(var) # Get all of var's neighbors
        for neighbor in neighbors: # Loop through each neighbor
            if neighbor in assignment: # If that neighbor already has been assigned continue
                continue
            for x in words: # Loop through all words in words
                for y in self.domains[neighbor]: # Loop through all of the words in the neighbor's domain
                    overlap = self.crossword.overlaps[var, neighbor] # Get the overlap between the neighbor and our var
                    if overlap == None: # If the overlap is none continue
                        continue
                    elif x[overlap[0]] != y[overlap[1]]: # Else if the overlap shows an issue
                        words[x] += 1 # Add one to the count of words[x] to indicate that this particular word in var's domain rules out a possibility in it's neighbors

        orderedDomainValues = sorted(words, key=lambda key: words[key]) # Sort the words dict by key to get a list with words ruling out the least amount of words to greatest
        return orderedDomainValues # Return that list.

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        temp = self.domains.copy()
        for var in temp.copy():
            if var in assignment:
                temp.pop(var)

        if self.checkMinDomain(temp): # If we do have a variable with the min length of domain choices
            sortedList = sorted(temp, key=lambda key: len(temp[key])) # We sort the dict based of the length of those domains
            return sortedList[0] # Return the first variable in our sortedList
        elif self.checkMaxArcs(temp): # Else if we have dont have a variable with a min length we check if one has a max length of arcs(neighbors)
            sortedList = sorted(temp, key=lambda key: len(self.crossword.neighbors(key))) # If we do we sort the dict based of the length of those neighbors
            return sortedList[-1] # And we return the last index in that list
        else: # Else if all nodes are equal in length of domain choices or arcs then we arbitrarily return a variable
            return random.choice(list(temp)) # Returning a random choice.

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        if self.assignment_complete(assignment): # If the assignment is complete
            return assignment # Return the assingment

        variable = self.select_unassigned_variable(assignment) # Else get a variable from any unnasigned variables
        for value in self.order_domain_values(variable, assignment): # Loop through that variables possible values
            assignment[variable] = value # Assign the variable that value
            inferences = self.inference(assignment)
            if inferences != None:
                for inference in inferences:
                    assignment[inference] = inferences[inference]
            if self.consistent(assignment): # Check if the assingment is consistent which will either return a recursive call or None
                result = self.backtrack(assignment) # Recursive call
                if result != None: # If the recursive call doesnt return None
                    return result # Return the result as the variable isn't conflicting with others.
                assignment[variable] = None
                for inference in inferences:
                    assignment[inference] = None
        return None # Return none if no possible solutions.

    def inference(self, assignment):
        inferences = dict()

        for variable in assignment: # Loop through variables in assignment
            neighbors = self.crossword.neighbors(variable) # Get the neighbors of that variable
            for neighbor in neighbors: # Loop through it's neighbors
                if neighbor in assignment: # If the variable is already assigned continue
                    continue
                overlap = self.crossword.overlaps[variable, neighbor] # Get the overlap
                if overlap != None: # If not none
                    for word in self.domains[neighbor].copy(): # Loop through its words
                        if assignment[variable][overlap[0]] != word[overlap[1]]: # If the word isnt consistent with the assignment
                            self.domains[neighbor].remove(word) # Remove the word from the domain
                    self.maintaining_arc_consistency(neighbor) # Call function to maintain arc consistency
                if len(self.domains[neighbor]) == 1: # If the domain only has one remaining choice then add it to assignment
                    inferences[neighbor] = next(iter(self.domains[neighbor])) # Add the assignment to inferences dict
        if len(inferences) != 0:
            return inferences # Return the inferences dict
        return None

    def maintaining_arc_consistency(self, variable):

        queue = [] # Initialize queue
        for neighbor in self.crossword.overlaps: # Loop through neighbors
            if neighbor[1] == variable: # If the pair of neighbors is x, variable
                queue.append(neighbor) # Add it to the queue
        return self.ac3(queue) # Call ac3 with the queue as a parameter.

    def checkMinDomain(self, dictionary):

        min = len(dictionary[next(iter(dictionary))]) # Assigning the length of temp[first key in temp], as the order every time doesnt matter we are just checking for a min value if present.
        for var in dictionary: # Loop over dict
            if len(dictionary[var]) != min: # Check if any domain has a different length of min indicating we have a minimum value.
                return True # Return true if we have different length domains
        return False # Return false if no min is found meaning that all domains are equal in length of choices


    def checkMaxArcs(self, dictionary):

        max = len(self.crossword.neighbors(next(iter(dictionary)))) # Assigning max to the lenght of the first iteration of dictionary, passed into neighbors func which returns a set of neighbors to that variable.
        for var in dictionary: # Loop over dict
            if len(self.crossword.neighbors(var)) != max: # Check if any variable has more or less neighbors than any other neighbor (Arcs)
                return True # Return true if we do have different lengths insinuating we have a variable with more arcs than another
        return False # Return false insinuating we have variables with # of equal arcs.

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
