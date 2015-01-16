from fbsearch.evaluate import f1_score

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
    score = f1_score(actual, predicted)
    assert score == expected_score

