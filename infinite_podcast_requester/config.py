import json

configuration = {}

with open("config.json", "r") as json_file:
    configuration = json.loads(json_file.read())
