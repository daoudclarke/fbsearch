from fbsearch.dataset import get_dataset

from StringIO import StringIO


def test_dataset_loading():
    data = """
        [
          {
            "url": "http://www.freebase.com/view/en/justin_bieber",
            "targetValue": "(list (description \\"Jazmyn Bieber\\") (description \\"Jaxon Bieber\\"))",
            "utterance": "what is the name of justin bieber brother?"
          }
        ]
    """
    
    dataset = get_dataset(StringIO(data))
    assert dataset == [('what is the name of justin bieber brother?',
                        ['Jazmyn Bieber', 'Jaxon Bieber'])]
