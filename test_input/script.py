import json
from pprint import pprint

data_file = open('/home/icontreras/Documents/algos.json')
data = json.load(data_file)

pprint(data)
print("\n")
testList = []
for i in range(len(data["test_dicts"])):
    testList.append(data["test_dicts"][i])
pprint(testList)
