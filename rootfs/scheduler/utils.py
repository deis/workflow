from __future__ import unicode_literals
from copy import deepcopy


def dict_merge(origin, merge):
    """
    Recursively merges dict's. not just simple a["key"] = b["key"], if
    both a and b have a key who's value is a dict then dict_merge is called
    on both values and the result stored in the returned dictionary.
    Also handles merging lists if they occur within the dict
    """
    if not isinstance(merge, dict):
        return merge

    result = deepcopy(origin)
    for key, value in merge.iteritems():
        if key in result and isinstance(result[key], dict):
            result[key] = dict_merge(result[key], value)
        else:
            if isinstance(value, list):
                if key not in result:
                    result[key] = value
                else:
                    # merge lists without leaving potential duplicates
                    # result[key] = list(set(result[key] + value))  # changes the order as well
                    for item in value:
                        if item in result[key]:
                            continue

                        result[key].append(item)
            else:
                result[key] = deepcopy(value)
    return result


def flatten(collection):
    """
    Flatten an arbitrarily deep structure of dicts, lists and tuples and
    extract the strings at the leaves of the structures.
    """
    vals = []
    if isinstance(collection, basestring):
        vals.append(collection)
    elif isinstance(collection, (list, tuple)):
        for item in collection:
            vals.extend(flatten(item))
    elif isinstance(collection, dict):
        vals.extend(flatten(collection.values()))
    else:
        raise Exception(
            "Can't extract values from a %s" % collection.__class__
        )
    return vals
