import nltk
import sys
import os
import string
import math

FILE_MATCHES = 4
SENTENCE_MATCHES = 1


def main():
    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    corpus = dict()  # Init empty dict

    for file in os.listdir(directory):  # For each file in directory
        if file.endswith(".txt"):  # If the file ends with .txt
            f = open(os.path.join(directory, file), "r", encoding='utf8')  # Open the file
            corpus[file] = f.read()  # Read its contents in corpus
            f.close()  # Close the file

    return corpus  # Return corpus


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.
    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """

    words = nltk.word_tokenize(document)  # Tokenize the words

    words = [  # Words = all lowercase words that are not stopwords or punctuation.
            word.lower() for word in words
            if word not in nltk.corpus.stopwords.words("english")
            and not is_word_punctuation(word)
            ]

    return words  # Return list of lowercase words in words


def is_word_punctuation(word):  # Helper method for tokenize, checks if a word punctuation count is equal to the length of the word
                                # Signifying the word is only punctuation
    count = 0
    for char in word:
        if char in string.punctuation:
            count += 1

    return count == len(word)


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.
    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """

    counter = dict()  # Init empty dict

    for file in documents:  # For each file
        seen = set()  # Init empty set
        for word in documents[file]:  # For each word in the file
            if word not in seen:  # If not seen already
                seen.add(word)  # Add word to seen
                if word in counter:  # If word in counter
                    counter[word] += 1  # Add 1
                else:  # Else word not in counter
                    counter[word] = 1  # Assign one

    for word in counter:  # For word in counter
        counter[word] = math.log(len(documents) / counter[word])  # Assign desired algorithm value

    return counter  # Return counter


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tf_idfs = dict()  # Init empty dict

    for file in files:  # For each file in files
        for word in query:  # For each word in query
            tf_idfs[file] = files[file].count(word) * idfs[word]  # Assign dict[file] value

    return [key[0] for key in sorted(tf_idfs.items(), key=lambda key: key[1], reverse=True)][:n]  # Return the key from the sorted dict by values of the top n elements


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sentence_ranks = list()  # Init empty list

    for sentence in sentences:  # For each sentence in sentences
        sentence_values = [sentence, 0, 0]  # Assign a list of the sentence and two initial values of 0

        for word in query:  # For each word in query
            if word in sentences[sentence]:  # If word in sentences[sentence]
                sentence_values[1] += idfs[word]  # Assign index 1 matching word measure
                sentence_values[2] += sentences[sentence].count(word) / len(sentences[sentence])  # Assign index 2 query term density

        sentence_ranks.append(sentence_values)  # Append the sentence

    return [key[0] for key in sorted(sentence_ranks, key=lambda key: (key[1], key[2]), reverse=True)][:n]  # Return the first index of the n top sentences ranked by their matching word measure and query term density in descending order


if __name__ == "__main__":
    main()