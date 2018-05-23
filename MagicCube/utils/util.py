def listPlus(list1, list2, positive=True):
    result = []
    for item1, item2 in zip(list1, list2):
        if positive:
            result.append(item1 + item2)
        else:
            result.append(item1 - item2)

    return result


def divideList(list, n):
    result = []
    for item in list:
        result.append(float(item) / n)
    return result

def negativeList(list):
    result = []
    for item in list:
        result.append(-item)
    return result
