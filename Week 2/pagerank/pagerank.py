import os
import random
import re
import sys
import math

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    model = dict()  # Init empty dict
    if corpus[page]:  # If the page has links
        for p in corpus:  # For every page in corpus
            model[p] = (1 - damping_factor) / len(corpus)  # Assign model[p]
            if p in corpus[page]:  # If the page(p) is in links from corpus[page(parameter)]
                model[p] += damping_factor / len(corpus[page])  # Add to model[p]
    else:  # Else if the page has no links
        for p in corpus:  # Then assign each page equal probability
            model[p] = 1 / len(corpus)

    return model  # Return model


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    page_rank = dict()  # Init empty dict
    for key in corpus:  # Populate page_rank
        page_rank[key] = 0.0  # Set init values to 0.0

    random_page = random.choice((list(corpus.keys())))  # Start with random page of equal prob
    page_rank[random_page] = (1/len(corpus))  # Set init value to equal prob for the random page

    for i in range(n):  # Loop over n times
        sample_model = transition_model(corpus, random_page, damping_factor)  # Get a sample model with the random page
        for key in sample_model:  # For all keys in sample model
            page_rank[key] += sample_model[key]  # Add them to our page rank dict
        random_page = random.choices(list(corpus.keys()), weights=list(page_rank.values()), k=1)[0]  # Get the next page rank by a random choice based on the values of the pages

    for key in page_rank:  # For all keys
        page_rank[key] /= n  # Normalize them by dividing by n

    return page_rank  # Return page_rank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    page_rank = dict()  # Init empty dicts
    temp_rank = dict()  # ""
    for key in corpus:  # Loop through keys
        page_rank[key] = 1 / len(corpus)  # Assign initial value of equal prob

    repeat = True  # Bool condition

    while repeat:  # While repeat
        for page in page_rank:  # For each page in page_rank
            tot = 0.0  # Init & assign tot

            for p in corpus:  # For each page(p) in corpus
                if page in corpus[p]:  # If page is in corpus[p], meaning if page is in p's links
                    tot += page_rank[p] / len(corpus[p])  # Add the value of page_rank[p] / number of total links
                if not corpus[p]:  # Else if it doesn't have links
                    tot += page_rank[p] / len(corpus)  # The total is the value of p in page_rank / total number of pages
            temp_rank[page] = (1 - damping_factor) / len(corpus) + damping_factor * tot  # Assign temp_rank[page] values received by algorithm

        repeat = False  # Set repeat to false

        for page in page_rank:  # Loop
            if not math.isclose(temp_rank[page], page_rank[page], abs_tol=0.001):  # If the values are not converging (difference by 0.001)
                repeat = True  # Then repeat the loop
            page_rank[page] = temp_rank[page]  # Assign the values in temp_rank to page_rank

    return page_rank  # return page_rank


if __name__ == "__main__":
    main()
