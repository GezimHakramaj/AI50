import csv
import sys
import calendar

from csv import DictReader
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():
    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """

    with open(filename, 'r') as f:
        csv_reader = DictReader(f)

        int_keys = ["Administrative", "Informational", "ProductRelated", "OperatingSystems", "Browser", "Region",
                    "TrafficType"]  # Create a list of keys to cast those values to an int
        float_keys = ["Administrative_Duration", "Informational_Duration", "ProductRelated_Duration", "BounceRates",
                      "ExitRates", "PageValues", "SpecialDay"]  # Create a list of keys to cast those values to a float
        other_keys = ["Month", "VisitorType", "Weekend",
                      "Revenue"]  # Create a list of keys which need an extra step of checking
        months = {name: num - 1 for num, name in enumerate(calendar.month_abbr) if
                  num}  # Create a dict with names of the months(abbreviated) 0-11 (jan-dec)
        months["June"] = 5  # Add June with value 5 since the datafile has June rather than Jun.

        if csv_reader is not None:  # Checking if the file was loaded
            evidence = []  # Initialize empty list of evidence lists
            labels = []  # Empty label list
            for row in csv_reader:  # For each row in csv_reader
                temp = []  # Initialize empty evidence list
                for key in row:  # For each key in row
                    if key in int_keys:  # Mapping each key to which value they should be casted to.
                        temp.append(int(row[key]))  # Int casting
                    elif key in float_keys:
                        temp.append(float(row[key]))  # Float casting
                    elif key in other_keys:  # If the key is in other_keys
                        if key == other_keys[0]:  # If key is month
                            temp.append(months[row[key]])  # Get the numerical value for each month
                        elif key == other_keys[1]:  # If key is visitorType
                            if row[key] == "Returning":  # Check if value of key is returning
                                temp.append(1)  # Add a 1 for returning
                            else:
                                temp.append(0)  # 0 for not returning
                        else:  # If the key is either weekend or revenue(since they are both booleans)
                            if row[key] == "TRUE":  # If true
                                temp.append(1)  # Append 1
                                if key == "Revenue":  # If the key == revenue
                                    labels.append(1)  # Append a 1 in labels
                            else:  # Else false
                                temp.append(0)  # Append 0
                                if key == "Revenue":
                                    labels.append(0)  # Append a 0 in labels
                evidence.append(temp)  # Append the list to evidence

    return evidence, labels  # Return a tuple of evidence, labels


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """

    model = KNeighborsClassifier(n_neighbors=1)  # Create a model with KNeighbors...
    model.fit(evidence, labels)  # Call fit method on model
    return model  # Return fitted model.


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """

    pos_correct = 0  # Var to count how many times we predicted a user went through with a purchase and accurately matches with labels
    pos_total = 0  # Var to count total num of actual users who went through with a purchase in labels
    neg_correct = 0  # Var to count how many times we predicted a user did not got through with a purchase and matches labels as well
    neg_total = 0  # Var to count total num of actual users who did not go through with a purchase in labels

    for i in range(len(labels)):  # Loop through labels
        # 0 represents did no purchase in labels
        # 1 represents did purchase in labels
        if labels[i] == 0:  # If labels represents no purchase (0)
            neg_total += 1  # Add one to the neg total
            if predictions[i] == 0:  # If we predicted they didn't purchase as well
                neg_correct += 1  # Add one to the total count of neg_correct
        elif labels[i] == 1:  # Else if labels doesn't represent a purchase (1)
            pos_total += 1  # Add 1 to the pos total
            if predictions[i] == 1:  # If predictions matches with labels
                pos_correct += 1  # Add one to total of pos_correct

    sensitivity = float(pos_correct / pos_total)  # Cast the true positive rate into a float
    specificity = float(neg_correct / neg_total)  # Cast the true negative rate into a float

    return sensitivity, specificity


if __name__ == "__main__":
    main()
