import pytest


def f1_score(actual, predicted):
    """
    Return the F1 score, given two sets of entities: the correct set,
    and those predicted.
    """
    intersection = float(len(set(actual) & set(predicted)))
    if intersection == 0.0:
        return 0.0

    precision = intersection/len(predicted)
    recall = intersection/len(actual)
    return 2*precision*recall/(precision + recall)

