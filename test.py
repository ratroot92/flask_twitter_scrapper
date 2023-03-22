myList1 = [
    {"name": "mango", "type": "fruit"},
    {"name": "apple", "type": "fruit"},
    {"name": "lemon", "type": "vegetable"},
    {"name": "jani", "type": "vegetable"},



]


myList2 = [
    {"name": "mango", "type": "fruit"},
    {"name": "apple", "type": "fruit"},
    {"name": "lemon", "type": "vegetable"},


]

# exist = list(filter(lambda tweet: tweet["id"] == tweet['id'], target['tweets']))


print(list(filter(lambda x: len(list(filter(lambda y: y['name'] == x['name'], myList2))) == 0, myList1)))
