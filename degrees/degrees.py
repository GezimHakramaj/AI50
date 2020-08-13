import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "src/large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    start = Node(source, None, None) # Create start state with no action nor parent
    frontier = QueueFrontier() # Create a QueueFrontier which will be our queue for BFS
    explored = [] # Explored list so we dont reiterate over explored actor's IDs

    frontier.add(start) # Add our start state to the frontier

    while True:
        if frontier.empty(): # If our frontier is empty we return none which means no connection
            return None

        node = frontier.remove() # Otherwise remove our node first in queue
        if node.state not in explored: # Check if our node's state is not in explored to avoid adding for redundancy
            explored.append(node.state) # Add our node's state into explored

        neighbors = neighbors_for_person(node.state) # Get our neighbors with a helper function which returns all people associated with the movies that person starred in
        for neighbor in neighbors: # Loop over each neighbor
            if neighbor[1] in explored: # If our neighbor, which is a list of (movie_id, star_id) matches one of explored states
                continue

            child = Node(neighbor[1], node, neighbor[0]) # Otherwise create a child node with state the stars id, the parent is node and with action = movie_id
            if child.state == target: # Check if our child is our target to avoid extra steps
                connection = [] # Create a list
                connection.append((child.action, child.state)) # Append our target(child) in our list with the action then state (movie_id, star_id)

                while node.parent is not None: # Loop over each node's parent
                    connection.append((node.action, node.state)) # Append our node to create a chain from our target back to our source star
                    node = node.parent # Traverse the parents

                connection.reverse() # Reverse the list to get a chain from source to target.
                print(connection) # Test to see the list
                return connection # Return the list.

            else: # Otherwise our child is not the target
                explored.append(child.state) # Add to explored state
                frontier.add(child) # Add the child to the frontier


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()