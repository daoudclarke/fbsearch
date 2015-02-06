import json
from itertools import groupby
from operator import itemgetter


def get_data(dataset_path):
    with open(dataset_path) as dataset_file:
        for row in dataset_file:
            if len(row.strip()) == 0:
                continue
            yield json.loads(row)

def find_errors(dataset_path):
    data = get_data(dataset_path)
    for source, group in groupby(data, itemgetter('source')):
        group = list(group)
        max_score = max(item['score'] for item in group)
        if max_score == 0:
            print source


if __name__ == "__main__":
    find_errors('/home/dc/Experiments/sempre-paraphrase-dataset/examples.json')
