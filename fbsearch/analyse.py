import numpy as np
from numpy import mean as get_mean
from scipy.stats import sem as get_error_in_mean
from fbsearch import settings
import json
import cPickle as pickle

def get_precision_recall_f1(actual, predicted):
    """
    Return the F1 score, given two sets of entities: the correct set,
    and those predicted.
    """
    intersection = float(len(set(actual) & set(predicted)))
    if intersection == 0.0:
        return 0.0, 0.0, 0.0

    precision = intersection/len(predicted)
    recall = intersection/len(actual)
    f1_score = 2*precision*recall/(precision + recall)
    return precision, recall, f1_score


def get_f1_score(actual, predicted):
    _, _, f1 = get_precision_recall_f1(actual, predicted)
    return f1


def analyse_results(results):
    scores = np.zeros((len(results), 3))
    for i, result in enumerate(results):
        precision, recall, f1_score = get_precision_recall_f1(
            result['target'], result['predicted'])
        scores[i, 0] = precision
        scores[i, 1] = recall
        scores[i, 2] = f1_score
    mean = get_mean(scores, axis=0)
    errors = get_error_in_mean(scores, axis=0)

    assert len(mean) == 3, "Actual length: %d" % len(mean)
    assert len(errors) == 3
    
    return {
        'precision': (mean[0], errors[0]),
        'recall': (mean[1], errors[1]),
        'f1_score': (mean[2], errors[2])
        }

def analyse(file_path=None):
    if file_path is None:
        file_path = settings.RESULTS_PATH
    results_file = open(file_path)
    results = json.load(results_file)
    analysis = analyse_results(results)
    print analysis
               
def analyse_ranks(file_path):
    results_file = open(file_path)
    results = json.load(results_file)
    ranks = [result['rank'] for result in results if result['rank'] >= 0]
    skipped = [result['rank'] for result in results if result['rank'] == -1]
    return {'average_rank': (get_mean(ranks), get_error_in_mean(ranks)),
            'skipped': len(skipped)}

def analyse_system_best(file_path):
    results_file = open(file_path)
    results = pickle.load(results_file)
    num_results = len(results)
    num_correct = 0
    for result in results:
        system_best = set(result['system'][:1])
        if system_best & set(result['oracle']):
            num_correct += 1
    return {'num_correct': num_correct,
            'total': num_results,
            'proportion': float(num_correct)/num_results}

if __name__ == "__main__":
    print analyse_system_best('system-best.json')
