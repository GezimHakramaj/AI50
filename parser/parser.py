import nltk
import sys

# List of words given to program
TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

# Rule for parsing sentences
# Noun Phrase (NP)
# Verb Phrase (VP)
# Adjective Phrase (AP)
# Prepositional Phrase (PP)
# Adverb Phrase (ADP)
# Conjunction Phrase (CP)
NONTERMINALS = """
S -> NP VP

NP -> N | Det N | AP NP | N PP | Det AP NP | Det NP ADP | Det N CP | Det AP NP CP 
VP -> V | V NP | ADP VP | V PP | V ADP | V NP PP | 
AP -> Adj | Adj AP
PP -> P NP
ADP -> Adv | Adv VP | Adv NP | Adv CP
CP -> Conj | Conj NP | Conj VP | Conj NP VP 

"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """

    sentence = sentence.lower()  # Change sentence to lowercase
    sentence = nltk.word_tokenize(sentence)  # Tokenize each word with nltk function

    for word in sentence.copy():  # For each word
        if not word.isalnum():  # If the word is not alphanumeric
            sentence.remove(word)  # Remove the word

    return sentence  # Return the sentence


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """

    np_chunks = []  # Initilaize empty list

    for sub_trees in tree.subtrees(lambda tree: tree.label() == "NP"):  # Go over each sub tree in subtrees method part of nltk.tree class with lambda function "filter" Filtering by lables equaling NP
        if contains_np_chunk(sub_trees):  # Call helper
            np_chunks.append(sub_trees)  # Append if true

    return np_chunks  # Return np_chunks


def contains_np_chunk(sub_tree):  # Helper to check if a np_chunk contains another noun phrase sub tree

    for leaf in sub_tree:  # Iterate through each leaf in the tree
        if leaf.label() == "NP":  # And check if the leaf has a label containing NP
            return False  # Return false if it does
    return True  # Return true if doesnt insinuating there is no sub set with a noun phrase in our current noun phrase


if __name__ == "__main__":
    main()
