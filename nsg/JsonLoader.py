import json

class JsonLoader :

    def __init__(self):
        #print("json loader init")
        pass

    def load_data(self,filename):
        path = "./json/"+ filename +".json"
        with open(path) as json_file:
            json_data = json.load(json_file)
        return json_data
