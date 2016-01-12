"""
Helper functions used by the Deis server.
"""
import base64
import hashlib
import random
from copy import deepcopy


def generate_app_name():
    """Return a randomly-generated memorable name."""
    adjectives = [
        'ablest', 'absurd', 'actual', 'aerial', 'allied', 'artful', 'atomic', 'august',
        'bamboo', 'benign', 'blonde', 'blurry', 'bolder', 'breezy', 'bubbly', 'burley',
        'candid', 'calmer', 'casual', 'cheery', 'classy', 'clever', 'convex', 'cubist',
        'dainty', 'dapper', 'decent', 'deluxe', 'docile', 'dogged', 'drafty', 'dreamy',
        'earthy', 'easier', 'echoed', 'edible', 'elfish', 'excess', 'exotic', 'expert',
        'fabled', 'famous', 'feline', 'finest', 'flaxen', 'folksy', 'frisky', 'frozen',
        'gaslit', 'gentle', 'gifted', 'ginger', 'global', 'golden', 'grassy', 'guided',
        'haptic', 'hearty', 'hidden', 'hipper', 'honest', 'humble', 'hungry', 'hushed',
        'iambic', 'iciest', 'iconic', 'indoor', 'inward', 'ironic', 'island', 'italic',
        'jagged', 'jangly', 'jaunty', 'jicama', 'jiggly', 'jovial', 'joyful', 'junior',
        'kabuki', 'karmic', 'keener', 'kiddie', 'kindly', 'kingly', 'klutzy', 'knotty',
        'lambda', 'latest', 'leader', 'linear', 'lively', 'lonely', 'loving', 'luxury',
        'madcap', 'madras', 'marble', 'mellow', 'metric', 'modest', 'molten', 'mystic',
        'native', 'nearby', 'nested', 'newish', 'nickel', 'nimbus', 'nonfat', 'normal',
        'oblong', 'oddest', 'offset', 'oldest', 'onside', 'orange', 'outlaw', 'owlish',
        'padded', 'pastry', 'peachy', 'pepper', 'player', 'preset', 'proper', 'pulsar',
        'quacky', 'quaint', 'quartz', 'queens', 'queued', 'quinoa', 'quirky', 'quoted',
        'racing', 'rental', 'ribbed', 'rising', 'rococo', 'rubber', 'rugged', 'rustic',
        'sanest', 'scenic', 'seeing', 'shadow', 'skiing', 'stable', 'steely', 'syrupy',
        'taller', 'tender', 'tested', 'timely', 'trendy', 'triple', 'truthy', 'twenty',
        'ultima', 'unbent', 'unisex', 'united', 'upbeat', 'uphill', 'usable', 'utmost',
        'vacuum', 'valued', 'vanity', 'velcro', 'velvet', 'verbal', 'violet', 'vulcan',
        'walkup', 'webbed', 'wicker', 'wiggly', 'wilder', 'wonder', 'wooden', 'woodsy',
        'yearly', 'yeasty', 'yellow', 'yeoman', 'yogurt', 'yonder', 'youthy', 'yuppie',
        'zaftig', 'zanier', 'zephyr', 'zeroed', 'zigzag', 'zipped', 'zircon', 'zydeco',
    ]
    nouns = [
        'addendum', 'anaconda', 'airfield', 'aqualung', 'armchair', 'asteroid', 'autoharp',
        'babushka', 'backbone', 'bagpiper', 'barbecue', 'bookworm', 'bullfrog', 'buttress',
        'caffeine', 'checkers', 'chinbone', 'countess', 'crawfish', 'cucumber', 'cutpurse',
        'daffodil', 'darkroom', 'deadbolt', 'doghouse', 'dragster', 'drumroll', 'duckling',
        'earrings', 'earthman', 'eggplant', 'electron', 'elephant', 'espresso', 'eyetooth',
        'falconer', 'farmland', 'ferryman', 'fireball', 'fishbone', 'footwear', 'frosting',
        'gadabout', 'gasworks', 'gatepost', 'gemstone', 'gladness', 'goldfish', 'greenery',
        'hacienda', 'handbill', 'hardtack', 'hawthorn', 'headwind', 'henhouse', 'huntress',
        'icehouse', 'idealist', 'inchworm', 'instinct', 'inventor', 'insignia', 'ironwood',
        'jailbird', 'jamboree', 'jerrycan', 'jetliner', 'jokester', 'joyrider', 'jumpsuit',
        'kangaroo', 'keepsake', 'kerchief', 'keypunch', 'kingfish', 'knapsack', 'knothole',
        'ladybird', 'lakeside', 'lambskin', 'landmass', 'larkspur', 'lollipop', 'lungfish',
        'macaroni', 'mackinaw', 'magician', 'mainsail', 'milepost', 'mongoose', 'moonrise',
        'nailhead', 'nautilus', 'neckwear', 'newsreel', 'nonesuch', 'novelist', 'nuthatch',
        'occupant', 'odometer', 'offering', 'offshoot', 'original', 'organism', 'overalls',
        'pachinko', 'painting', 'pamphlet', 'paneling', 'pendulum', 'playroom', 'ponytail',
        'quacking', 'quadrant', 'quantity', 'queendom', 'question', 'quilting', 'quotient',
        'rabbitry', 'radiator', 'renegade', 'ricochet', 'riverbed', 'rosewood', 'rucksack',
        'sailfish', 'sandwich', 'sculptor', 'seashore', 'seedcake', 'skylight', 'stickpin',
        'tabletop', 'tailbone', 'teamwork', 'teaspoon', 'tinkerer', 'traverse', 'turbojet',
        'umbrella', 'underdog', 'undertow', 'unicycle', 'universe', 'uptowner', 'utensils',
        'vacation', 'vagabond', 'valkyrie', 'variable', 'villager', 'vineyard', 'vocalist',
        'waggoner', 'waxworks', 'waterbed', 'wayfarer', 'whitecap', 'windmill', 'woodshed',
        'yachting', 'yardbird', 'yardwork', 'yearbook', 'yearling', 'yeomanry', 'yodeling',
        'zaniness', 'zeppelin', 'ziggurat', 'zillions', 'zirconia', 'zoologer', 'zucchini',
    ]
    return "{}-{}".format(
        random.choice(adjectives), random.choice(nouns))


def dict_diff(dict1, dict2):
    """
    Returns the added, changed, and deleted items in dict1 compared with dict2.

    :param dict1: a python dict
    :param dict2: an earlier version of the same python dict
    :return: a new dict, with 'added', 'changed', and 'removed' items if
             any were found.

    >>> d1 = {1: 'a'}
    >>> dict_diff(d1, d1)
    {}
    >>> d2 = {1: 'a', 2: 'b'}
    >>> dict_diff(d2, d1)
    {'added': {2: 'b'}}
    >>> d3 = {2: 'B', 3: 'c'}
    >>> expected = {'added': {3: 'c'}, 'changed': {2: 'B'}, 'deleted': {1: 'a'}}
    >>> dict_diff(d3, d2) == expected
    True
    """
    diff = {}
    set1, set2 = set(dict1), set(dict2)
    # Find items that were added to dict2
    diff['added'] = {k: dict1[k] for k in (set1 - set2)}
    # Find common items whose values differ between dict1 and dict2
    diff['changed'] = {
        k: dict1[k] for k in (set1 & set2) if dict1[k] != dict2[k]
    }
    # Find items that were deleted from dict2
    diff['deleted'] = {k: dict2[k] for k in (set2 - set1)}
    return {k: diff[k] for k in diff if diff[k]}


def fingerprint(key):
    """
    Return the fingerprint for an SSH Public Key
    """
    key = base64.b64decode(key.strip().split()[1].encode('ascii'))
    fp_plain = hashlib.md5(key).hexdigest()
    return ':'.join(a + b for a, b in zip(fp_plain[::2], fp_plain[1::2]))


def app_build_type(release):
    if not release.build.dockerfile:
        if not release.build.sha:
            return "deispull"
        else:
            return "buildpack"
    return "dockerfile"


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
    for key, value in merge.items():
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


if __name__ == "__main__":
    import doctest
    doctest.testmod()
