from numpy import mean as get_mean
from scipy.stats import sem as get_error_in_mean


def get_f1_score(actual, predicted):
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


def analyse_results(results):
    scores = []
    for result in results:
        score = get_f1_score(result['target'], result['predicted'])
        scores.append(score)
    return get_mean(scores), get_error_in_mean(scores)

