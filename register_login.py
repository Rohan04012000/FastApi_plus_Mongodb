from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from pymongo import MongoClient
from bson.objectid import ObjectId
from passlib.context import CryptContext
from typing import Optional, List

# Initializing FastAPI app.
app = FastAPI()

#Making MongoDB connection to the account which is created on Mongodb Atlas.
client = MongoClient("mongodb+srv://eng17cs0013adityavardhansingh:wVhZxcosxUQGeLN2@cluster0.edvwloq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

# Database and collection names references for quick access.
db = client['user_db']
users_collection = db['users']
ids_collection = db['user_ids']

#Password encryption using bcrypt.
pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")


#User registration model using Pydantic.
class User(BaseModel):
    name: str
    phone: str
    email: EmailStr
    password: str
    profession: str


#User login model.
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ID linking model for a particular user and the provided linked_id.
class UserIDLink(BaseModel):
    user_id: str
    linked_id: str


# Function to hash passwords given during registeration.
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


#Function to verify passwords given during login and already stored hashed_password.
# Return True if mattches else returen False.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


#A post method for Register endpoint.
@app.post("/register")
async def register(user: User):
    # Check if the email already exists
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code = 400, detail = "Email already registered")

    #Hashing the entered password before storing it on Mongodb.
    hashed_password = hash_password(user.password)

    # Insert the new user into the users collection
    new_user = {
        "name": user.name,
        "phone": user.phone,
        "email": user.email,
        "password": hashed_password,
        "profession": user.profession
    }

    #Noe stroing this document in collection called users, which is store in users_collection.
    result = users_collection.insert_one(new_user)

    #Giving a successfully message. Now, you can access login endpoint.
    # I did not direct it to login because I wanted to implemented separated endpoints.
    return {"message": "User registered successfully", "user_id": str(result.inserted_id)}


# Similar to register, a post method for Login endpoint.
@app.post("/login")
async def login(user: UserLogin):
    #Take the email and look into database to see if Email is found or not.
    db_user = users_collection.find_one({"email": user.email})

    if not db_user:
        raise HTTPException(status_code=400, detail = "Invalid email or password")

    #Verifying the entered password and retrieved password.
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=400, detail = "Invalid email or password")

    # Return success message with user ID
    return {"message": "Login successful", "user_id": str(db_user["_id"])}


# Send userid and linked_id, in json format from postman.
# Endpoint for linking the sent linked_id to a user account.
@app.post("/link_id")
async def link_id(link_data: UserIDLink):
    #Looking for the user by user_id if it exists or not.
    # This used_id is created by default in Mongodb, which will be returned to you when you login.
    if not ObjectId.is_valid(link_data.user_id):
        raise HTTPException(status_code = 400, detail = "Invalid user ID")

    #The _id is auto created in Mongodb users collection.
    user = users_collection.find_one({"_id": ObjectId(link_data.user_id)})

    #If there exist no user with entered user_id, raises an error.
    if not user:
        raise HTTPException(status_code=404, detail = "User not found")

    #finally, Linking the ID securely to the given id of the user.
    linked_data = {
        "user_id": ObjectId(link_data.user_id),
        # Securely storing the linked ID
        "linked_id": hash_password(link_data.linked_id)
    }

    ids_collection.insert_one(linked_data)

    return {"message": "ID linked successfully"}


#Complex query endpoint to join data from multiple collections based on user_id.
@app.get("/user_data/{user_id}")
async def get_user_data(user_id: str):
    # Check if the user ID is valid
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail = "Invalid user ID")

    #Join user data with linked ID data
    #Filter the documents in the users_collection to find the one with the _id that matches the provided user_id.
    pipeline = [
        {"$match": {"_id": ObjectId(user_id)}},
        {"$lookup": {
            "from": "user_ids",
            "localField": "_id",
            "foreignField": "user_id",
            "as": "linked_ids"
        }},
        {"$project": {"password": 0}}  # Exclude the password field from the result
    ]

    user_data = list(users_collection.aggregate(pipeline))

    #If no user is found with the provided user_id, raise an error.
    if not user_data:
        raise HTTPException(status_code=404, detail = "User not found")

    return user_data[0]


#Endpoint for deleting a user and all it's associated information, based on user_id, which can be found in Mongodb (users).
@app.delete("/delete_user/{user_id}")
async def delete_user(user_id: str):
    # Checking if the entered user_id is valid.
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail = "Invalid user ID")

    #Now, Deleting the user from users collection based on user_id entered.
    result = users_collection.delete_one({"_id": ObjectId(user_id)})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail = "User not found")

    #After deleting a user based on user_id, then
    # Delete all linked_id's linked with the user_id.
    ids_collection.delete_many({"user_id": ObjectId(user_id)})

    return {"message": "User and associated related records are properly removed!"}
