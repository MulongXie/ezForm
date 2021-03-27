import json

data = json.load(open('data.json', 'r'))
print(data)
inputs = data['inputs']
print(inputs)