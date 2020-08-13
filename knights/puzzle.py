from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
knowledge0 = And(
    # A is a knight if A is not a knave
    Biconditional(AKnight, Not(AKnave)),
    # A can only be a knight if he is both a knave and a knight
    Biconditional(AKnight, And(AKnight, AKnave))
    # A is a knave
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
knowledge1 = And(
    # A is a knight if A is not a knave
    Biconditional(AKnave, Not(AKnight)),
    # B is a knight if B is not a knave
    Biconditional(BKnave, Not(BKnight)),
    # A is only a knight if both A and B are knaves
    Biconditional(AKnight, And(AKnave, BKnave))
    # A is a knave
    # B is a knight
)

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
knowledge2 = And(
    # A is a knight if A is not a knave
    Biconditional(AKnight, Not(AKnave)),
    # B is a knight if B is not a knave
    Biconditional(BKnight, Not(BKnave)),
    # A is a knight if they are the same kind
    Biconditional(AKnight, Or(And(AKnave, BKnave), And(AKnight, BKnight))),
    # B is a knight if we are different kinds are true
    Biconditional(BKnight, Or(And(AKnave, BKnight), And(AKnight, BKnave)))
    # A is a knave
    # B is a knight
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
knowledge3 = And(

    Biconditional(AKnight, Not(AKnave)),
    Biconditional(BKnight, Not(BKnave)),
    Biconditional(CKnight, Not(CKnave)),
    # A can either be a knight if i am a knight is true and be a knave if i am a knave is true
    Or(Biconditional(AKnight, AKnight), Biconditional(AKnave, AKnave)),
    # B is a knight if A is a knave
    Biconditional(BKnight, Biconditional(AKnight, AKnave)),
    # B is a knave only if C is a knight
    Biconditional(BKnave, CKnight),
    # C is a knave only if A is a knave
    Biconditional(CKnave, AKnave)
    # A is a knight
    # B is a knave
    # C is a knight
)


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
