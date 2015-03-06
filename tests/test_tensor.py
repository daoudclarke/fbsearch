from fbsearch.tensor import TensorSystem



def test_tensor_system_can_learn():
    query = 'what is the name of justin bieber brother?'
    target = ['Jazmyn Bieber', 'Jaxon Bieber']

    dataset = [(query, target),
               ('who does joakim noah play for?', ['Chicago Bulls']),
               ('what kind of money to take to bahamas?', ['Bahamian dollar'])]

    tensor = TensorSystem()
    tensor.train(dataset)

    result = tensor.execute(query)
    
    tensor.connector.related.save_cache()

    assert result >= {u'Jazmyn Bieber', u'Jaxon Bieber'}
