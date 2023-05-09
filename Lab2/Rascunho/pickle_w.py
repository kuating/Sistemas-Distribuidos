import json

# assume you have the following dictionary
person = {"name": "Jessa", "country": "USA", "telephone": 1178}
print('Person dictionary')
print(person)

print("Started writing dictionary to a file")
with open("person.txt", "w") as fp:
    json.dump(person, fp)  # encode dict into JSON
print("Done writing dict into .txt file")