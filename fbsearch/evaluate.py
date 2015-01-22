import pytest
import json

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


def get_target_and_predicted_values(dataset, system):
    target_predicted_results = []
    for query, target_entities in dataset:
        system_entities = system.execute(query)
        target_predicted_results.append({'target': target_entities,
                                         'predicted': system_entities})
    return target_predicted_results




if __name__ == "__main__":
    results = get_target_and_predicted_values()
    target_predicted_results_file = open('target_predicted.json', 'w')
    json.dump(results, target_predicted_results_file)
    mean, error = evaluation.analyse_results(results)
    print "F1 average: %f +/- %f" % (mean, error)
