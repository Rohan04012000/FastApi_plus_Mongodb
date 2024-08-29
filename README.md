# FastApi_plus_Mongodb
This project was implemented using Pycharm, Fastapi, Pydantic and MongoDB Atlas.

This system allows users to register, login, link an ID to their account only after login, perform complex queries by joining data from multiple collections, and delete users along with all associated data.

# Endpoints
## Registeration endpoint  (/register)
1. Set the method to POST and send the payload as:
Eg:<br>
{<br>
  "name": "Nikhil", <br>
  "phone": "1230456789",<br>
  "email": "nikhil@example.com",<br>
  "password": "your_password",<br>
  "profession": "Engineer"<br>
}

The response for above endpoint will be:<br>
{<br>
  "message": "User registered successfully",<br>
  "user_id": "603e1c3b9c1d4c23a1e4a1c4"<br>
}<br>
user_id is auto generated id and returned from Mongodb.


## Login endpoint (/login)
1. Set the method to POST and send the payload as:
Eg:<br>
{<br>
  "email": "nikhil@example.com",<br>
  "password": "your_password"<br>
}<br>

Response from above endpoint will be: <br>
{<br>
  "message": "Login successful",<br>
  "user_id": "603e1c3b9c1d4c23a1e4a1c4"<br>
}
Note down/ Copy the user_id, which is needed in next step.

## Endpoint for linking an ID. (/link_id)
1. Set the method to POST and send the payload as: user_id is the id which you copied previously and linked_id in id you want to link now.<br>
{<br>
  "user_id": "603e1c3b9c1d4c23a1e4a1c4",<br>
  "linked_id": "ID123456"<br>
}<br>

## Endpoint for getting User data with Linked_id (/user_data/{user_id}), where user_id should be replaced with the id you copied.
Set the method to GET.
The response from this endpoint will be:<br>
{<br>
  "_id": "603e1c3b9c1d4c23a1e4a1c4",<br>
  "name": "Nikhil",<br>
  "phone": "1230456789",<br>
  "email": "nikhil@example.com",<br>
  "profession": "Engineer",<br>
  "linked_ids": [<br>
  {<br>
      "user_id": "603e1c3b9c1d4c23a1e4a1c4",<br>
      "linked_id": "$2b$12$"<br>
    }<br>
  ]<br>
}<br>

The linked_id is encrypted for security purposes.

## Endpoint for deleting a user based on user_id. (/delete_user/{user_id})
Set the method to delete send the payload.

# The code is written in a single FastAPI file with detailed comments. It includes:
1. MongoClient for connecting to MongoDB.
2. FastAPI framework to create the RESTful API.
3. Pydantic models to validate request data.
4. Passlib for password hashing and verification.
5. Error handling using FastAPI's HTTPException.




