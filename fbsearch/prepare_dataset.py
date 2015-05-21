"""
Create a dataset in old format for use with offline evaluation.
"""

from fbsearch.connect import get_results_cache
from fbsearch.dataset import get_dataset
from fbsearch import settings
from fbsearch.tensor import TensorSystem
from fbsearch.oracle import OracleSystem
from fbsearch.analyse import get_f1_score
from fbsearch.connect import Connector

from fbsearch import convertingjson as json

def convert_dataset(dataset, results_cache):
    queries = dict(dataset)
    tensor_system = TensorSystem(OracleSystem)
    tensor_system.connector = Connector()
    i = 0
    for source, results_collection in results_cache:
        gold = queries[source]
        num_added = 0
        for result_info in results_collection:
            expression = result_info['expression']
            target = tensor_system.get_expression_sentence(expression)
            value = result_info['results']
            value -= {None}
            if not value:
                continue
            f1 = get_f1_score(value, gold)
            yield {
                "source": source,
                "target": target,
                "score": f1,
                "value": value,
                "gold": gold,
                }
            num_added += 1
            i += 1
            if i % 100 == 0:
                print "Processed %d rows" % i
        if num_added == 0:
            yield {
                "source": source,
                "score": 0.0,
                "gold": gold,
                }
            

def save_dataset(processed):
    with open(settings.PREPARED_DATASET, 'w') as dataset_file:
        for row in processed:
            json.dump(row, dataset_file)
            dataset_file.write('\n')
            dataset_file.flush()


if __name__ == "__main__":
    dataset_file = open(settings.DATASET_PATH)
    dataset = get_dataset(dataset_file)
    results_cache = get_results_cache()
    processed = convert_dataset(dataset, results_cache)
    save_dataset(processed)

