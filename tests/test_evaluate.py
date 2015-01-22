from fbsearch import evaluate


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







