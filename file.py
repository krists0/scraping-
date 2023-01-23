import json

def create_json_file(json_file):
   
    with open("Output.json", "a") as write_file:
        json.dump(json_file, write_file, indent=4, sort_keys=True,separators=(", ", " : "))
        write_file.close()
    print("Done writing Sorted and to JSON data into file")     


def open_json_file():
    with open('Output2copy.json') as json_f:
        json_data = json.load(json_f)
    return json_data