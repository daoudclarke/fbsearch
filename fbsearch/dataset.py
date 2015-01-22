import json
import sexpdata

def symbol_to_string(symbol):
    try:
        return symbol.value()
    except AttributeError:
        return symbol


def get_dataset(dataset_file):
    """
    Return data in the open dataset_file as a list of (query,
    target_value) tuples.
    """
    examples = json.load(dataset_file)
    dataset = []
    for example in examples:
        query = example['utterance']
        target_data = sexpdata.loads(example['targetValue'])
        targets = [symbol_to_string(description[1]) for description in target_data[1:]]
        dataset.append((query, targets))
    return dataset
