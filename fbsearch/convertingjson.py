import json

class ConvertingJSONEncoder(json.JSONEncoder):
    """
    Automatically convert sets etc to lists.
    """
    def default(self, input_object):
        if isinstance(input_object, set):
           return list(input_object)
        return JSONEncoder.default(self, o)


def dump(obj, fp, indent=None):
    encoder = ConvertingJSONEncoder()
    json.dump(obj, fp,
              cls=ConvertingJSONEncoder,
              indent=indent)
