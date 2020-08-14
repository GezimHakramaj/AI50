"""
Tic Tac Toe Player
"""

import copy
import random

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    if terminal(board): # If the game is over return None
        return None

    count = 0 # Counter
    for i in range(3): # Loop
        for j in range(3):
            if board[i][j] != EMPTY: # Count how many moves have been played
                count += 1 # Increment counter

    if count % 2 == 0: # Check if counter even/odd "X or O"
        return X # Return X is even or 0
    else:
        return O # Return O is odd


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actionSet = set()

    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                actionSet.add((i, j))

    return actionSet


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if board[action[0]][action[1]] != EMPTY: # If that move is already on board raise exception
        raise Exception

    temp = copy.deepcopy(board)
    temp[action[0]][action[1]] = player(board) # Other wise mark the spot with the player

    return temp  # Returning copies of the board for use through minimax recurison


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    if board is initial_state():  # If game just started return none
        return None
    else:
        diagonal_win = [[[0,0], [1,1], [2,2]], [[2,0], [1,1], [0,2]]]  # List for diagonal win cells

        for i in range(0, 3):  # Iterate 3 times
            if board[i][0] == board[i][1] == board[i][2]:  # Checked to see if each cell in row is equal to one another
                return board[i][0] if board[i][0] is not None else board[i][1] if board[i][1] is not None else board[i][2]  # Return first cell of the row, if none then second and then if none again the third cell of the row
            if board[0][i] == board[1][i] == board[2][i]:  # Checking to see if each cell in column is equal to one another
                return board[0][i] if board[0][i] is not None else board[1][i] if board[1][i] is not None else board[2][i]  # Same as above for rows but just for columns.

        for diagonal in diagonal_win:  # Each diagonal in diagonal_win
            if board[diagonal[0][0]][diagonal[0][1]] == board[diagonal[1][0]][diagonal[1][1]] == board[diagonal[2][0]][diagonal[2][1]]:  # If each cell in the diagonal matches
                return board[diagonal[1][0]][diagonal[1][1]]  # Return the middle cell of board as it is shared for both diaganol win possibilites


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None: # If we have a winner return True
        return True

    for i in range(3): # Loop through board and check for an empty slot and return False
        for j in range(3):
            if board[i][j] == EMPTY:
                return False

    return True # Return true if we dont find an empty slot or a winner meaning a Tie


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """

    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def minimax(board):

    if terminal(board):  # If terminal board return None
        return None

    if board == initial_state():  # If empty board (player is 0) choose random move initially
        return random.randrange(0,3), random.randrange(0, 3)

    best_action = None  # best_action is none initially
    best_value = float("-inf") if player(board) == X else float("inf")  # best_value is either -inf or inf depending on player

    for action in actions(board):  # Loop through all actions

        if terminal(result(board, action)):  # If action results in a terminal board return the action to avoid playing the game an extra step and still winnig
            return action

        new_value = (  # new_value is either the max/min of best_value and the value returned by calling min_max_value with the action depending on player
            max(best_value, min_max_value(result(board, action), best_value)) if player(board) == X else
            min(best_value, min_max_value(result(board, action), best_value))
        )

        if new_value != best_value:  # If the value does not equal best_value, since were using for both min and max players
            best_value = new_value  # Record the new best best_value
            best_action = action  # Record the best_action

    return best_action


def min_max_value(board, best_value):

    """
    Combines maxValue and minValue as in the lecture into one call which does the same thing in one function.
    Introduces Alpha-Beta pruning by returning the value if it is greater than the best value skipping checking
    the rest of the actions.
    """

    if terminal(board):  # If the board is terminal return the utility of the board
        return utility(board)

    value = float("-inf") if player(board) == X else float("inf")  # Assign inf and -inf initially

    for action in actions(board):  # For each action with the board state
        new_value = min_max_value(result(board, action), value)  # new_value = recursive call to min_max_val with that new action and value(-inf, inf)

        if player(board) == X and new_value > best_value:  # If we are the maximizing player and new_val is greater than the best_val
            return new_value  # Return new_value
        elif player(board) == O and new_value < best_value:  # If we are minimizing player and new_val is smaller than the best_val
            return new_value  # Return new_value
        else:  # Else depending on player assign the max/min of value and new_value
            value = (
                max(value, new_value) if player(board) == X else
                min(value, new_value)
            )

    return value  # Return value

