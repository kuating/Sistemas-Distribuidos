import json

# Open the file for reading
with open("person.txt", "r") as fp:
    # Load the dictionary from the file
    person_dict = json.load(fp)

# Print the contents of the dictionary
print(person_dict)