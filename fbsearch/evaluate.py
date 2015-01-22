import pytest
import json




def get_target_and_predicted_values(dataset, system):
    target_predicted_results = []
    for query, target_entities in dataset:
        system_entities = system.execute(query)
        target_predicted_results.append({'target': target_entities,
                                         'predicted': system_entities})
    return target_predicted_results


class ConvertingJSONEncoder(json.JSONEncoder):
    """
    Automatically convert sets etc to lists.
    """
    def default(self, input_object):
        if isinstance(input_object, set):
           return list(input_object)
        return JSONEncoder.default(self, o)


def save(results, path):
    output_file = open(path, 'w')
    encoder = ConvertingJSONEncoder()
    json.dump(results, output_file,
              cls=ConvertingJSONEncoder,
              indent=4)


if __name__ == "__main__":
    from fbsearch import settings
    from fbsearch.oracle import OracleSystem
    from fbsearch.dataset import get_dataset

    dataset_file = open(settings.DATASET_PATH)
    dataset = get_dataset(dataset_file)[:50]
    system = OracleSystem(dataset)
    results = get_target_and_predicted_values(dataset, system)
    save(results, 'target_predicted.json')

    mean, error = analyse_results(results)
    print "F1 average: %f +/- %f" % (mean, error)
