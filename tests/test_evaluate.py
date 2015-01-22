from fbsearch import evaluate

import pytest

F1_TESTS = [
    ({1, 2, 3}, {1, 2, 3}, 1.0),
    ({1, 2}, {2, 3}, 0.5),
    ({1, 2, 3}, {1}, 0.5),
    ({1}, {2}, 0.0),
    ({1}, set(), 0.0),
    ]

@pytest.mark.parametrize("actual, predicted, expected_score", F1_TESTS)
def test_f1_scores(actual, predicted, expected_score):
    score = evaluate.get_f1_score(actual, predicted)
    assert score == expected_score


class MockSystem(object):
    def __init__(self):
        self.results = [['Barack Obama'], ['Two', 'Three']]
        self.index = -1

    def execute(self, query):
        self.index += 1
        return self.results[self.index]

EXPECTED_RESULTS = [{'target': ['Barack Obama'], 'predicted': ['Barack Obama']},
                    {'target': ['Three', 'Four'], 'predicted': ['Two', 'Three']}]

def test_evaluation_run():
    dataset = [('hello?', ['Barack Obama']),
               ('what time?', ['Three', 'Four'])]

    system = MockSystem()

    results = evaluate.get_target_and_predicted_values(dataset, system)
    assert results == EXPECTED_RESULTS


def test_evaluation_analysis():
    mean, error = evaluate.analyse_results(EXPECTED_RESULTS)
    assert mean == 0.75






