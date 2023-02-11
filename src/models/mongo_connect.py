import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["mydatabase"]
mycol = mydb["customers"]
mydict = {"name": "John", "address": "Highway 37"}

x = mycol.insert_one(mydict)
# Important: In MongoDB, a database is not created until it gets content!
print("hi")
