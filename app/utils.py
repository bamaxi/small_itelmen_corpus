import json


class MyEncoder(json.JSONEncoder):
    def default(self, o):
        return str(o)


def pretty_log(obj):
    return (json.dumps(obj, ensure_ascii=False, indent=2, cls=MyEncoder)
            if isinstance(obj, (dict, list)) else str(obj))