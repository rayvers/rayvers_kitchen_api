
# Rayvers-Kitchen-API Documentation 🚀

Welcome to the coolest API in town! Here, we take authentication and user profiles to a whole new level. Buckle up and let the fun begin!

---

 ## Reference
1. [Token Generation](#token-generation)
1. [Logout](#logout)
1. [User Profile](#user-profile)
1. [Create New user](#create-new-user)
1. [Verify User](#verify-user)
1. [Reset Password](#reset-password)
1. [Create Driver](#create-driver)
1. [Login The Driver](#login-the-driver)
1. [Create Restaurant](#create-restaurant)
1. [Login The Restaurant](#login-the-restaurant)
1. [Change User Password](#change-user-password)
1. [Changer Driver & Kitchen IDs](#change-user-driver-and-kitchen-ids)
1. [Update Restaurant](#get-and-update-restaurant-profile-information)
1. [Deduct From Restaurant Balance](#how-to-deduct-from-restaurant-balance)
1. [Save Withdrawal History](#save-restaurant-withdrawal-history)
1. [Update Driver](#get-and-update-driver-profile-information)
1. [List of Restaurants & Dishes](#list-of-restaurants-and-dishes)
1. [Ingredients](#ingredients)
1. [Dishes](#dishes)
1. [Categories](#categories)
1. [Pagination](#pagination)
1. [❌ Payment Integration With Stripe - no longer required](#payment-integration-with-stripe)
1. [Create Orders](#create-orders)
1. [Get Rescent Order Items](#get-rescent-order-items)
1. [Using Query Parameters to determine the nature of response](#using-query-parameters-to-determine-the-nature-of-response)
1. [Rating dishes](#rating-dishes)
1. [Get Rating for a single Dish](#get-the-rating-data-for-a-particular-dish)
1. [Rating Restaurants](#rating-restaurants)
1. [Get Rating for a single Restaurant](#get-the-rating-data-for-a-particular-restaurant)
1. [Rating Drivers](#rating-drivers)
1. [Get Rating for a single Driver](#get-the-rating-data-for-a-particular-driver)
1. [Analtics - Restaurants/Drivers](#get-the-analytics-data-for-a-particular-driver-or-restaurant)
---

## Token Generation 🔐

### `POST /auth/token/`

Generate a magic token to access our wonderland. Send your email and password to get the golden key.

**Request:**
```json
{
  "email": "your.email@example.com",
  "password": "supersecret"
}


```

### Response:

```json

{
  "user_id": 99,
  "email": "new.hero@example.com",
  "token": "your-magical-token"
}


```

## Logout 🚪

## POST /auth/logout/
Time to say goodbye. Use this endpoint to log out gracefully and secure the castle.
### Request:
{}  # No need for any payload, just hit the endpoint.


### Response:
```json
{
  "detail": "Logged out successfully."
}
```
Farewell, brave adventurer! Your session has ended.


## User Profile 🧑‍🚀


## GET /auth/users/me/
Retrieve your superhero profile details. Only for the chosen ones with a valid token.

### Response:

```json
{
  "email": "your.email@example.com",
  "name": "Captain Awesome",
  "date_of_birth": "1990-01-01",
  "is_superuser": true,
  "is_staff": false,
  "is_active": true,
  "profile_picture": "https://your.avatar.com",
  "bio": "Saving the world, one API call at a time."
}
```

## PUT /auth/users/me/
Update your superhero profile. Because even superheroes need a makeover!

Request:

```json
{
  "name": "New Hero Name",
  "date_of_birth": "1995-05-05",
  "bio": "A mysterious hero with a touch of humor."
}
```
### Response:

```json

{
  "email": "your.email@example.com",
  "name": "New Hero Name",
  "date_of_birth": "1995-05-05",
  "is_superuser": true,
  "is_staff": false,
  "is_active": true,
  "profile_picture": "https://your.avatar.com",
  "bio": "A mysterious hero with a touch of humor."
}
```

# Create New User 🦸‍♂️
  </summary>
## POST /auth/users/
Join the league of extraordinary individuals. Create your account and become a hero!

### Request:

```json
{
  "email": "new.hero@example.com",
  "password": "strongpassword"
}

```

### Response:
```json

{
  "message": "A verification code has been sent to talk2james@gmail.com.",
  "user_id": 5,
  "email": "talk2james@gmail.com",
  "role": "customer"
}

```

Pro Tip: Don't forget your token; it's the secret sauce to unlock the treasures!

## Verify User
</summary>
POST /auth/users/verify/
A code will be send the user's email
The user_id must be sent along the code

```json
{
  "code": 4432,
  "user_id": 4
}
```

If the user's email is correct:
```json
{
  "message": "Account has been verified successfully. Proceed to login."
}
```

If user decides to apply for another verification code,
they can use this endpoint
### POST /auth/users/verify/resend-code/
```json

  {
    "user_id": 2
  }

```

### The Response

```json
{"message": "Code was resent to your email"}
```

### Error Handling
In case of an error, any of the following format is sent back to user

```json
{"message": "Code was resent to your email"}
{"message": "Encountered an issue sending email. Retry!"}
{"message": "Invalid user id. User does not exist."}
```

If the code is incorrect, you'll get a variety of responses:

```json
{
  "message": "User code is invalid"
}
{
  "message": "User does not exist."
}

```


## Reset Password

  
This is the endpoint for the forget password functionality

## POST /auth/users/reset/password/

```json
{
  "email": "john@doe.com"
}

```
### Response
```json
  {"message": "Code was sent to your email", "user_id": 2}
```
After the reset password endpoint is sent, the user can still use the resend-code endpoint to receive another code


### Error Handling
In case of an error, any of the following format is sent back to user FOR INCORRECT USER ID or EMAIL was not sent successfully.


```json
{"message": "User with email does not exist"} - 
{"message": "Encountered an issue sending email. Retry!", "user_id": 3}
```

## Reset Password with Code
</summary>

  
### POST /auth/users/reset/password/code/

Here, we require a valid user_id, verification code, password and re_password fields to reset the password

```json

    {
      "user_id": 3,
      "code": 1238,
      "password": "newpassword",
      "re_password": "newpassword"
    }

```


### Error Handling
In case of an error, any of the following format is sent back to user.


```json
{"message": "Please enter the code sent to your mail."} 
{"message": "Unidentified user. Please send the user_id in payload."}
{"password": ["Password is required"]}
{"password": ["Password Confirmation is required"]}
{
"password": ["Please enter your password for both fields: password and re_password"]
}
{"password": ["Passwords must be valid strings"]}
{"password": ["Passwords do not match"]}
{"message": "User does not exist"}
{"message": "Code is incorrect"}
{"message": "Password was reset successfully."}
```




#### That's it for now, fearless explorer! If you have more quests, check our URLs for additional adventures. May your API calls be swift and your tokens never expire! 🚀✨


## Create Driver
</summary>
  
In order to create driver you must provide `email` and `password`.
Note that only restaurants and admins have the permissions to create drivers.
You must have the authorization token in the header when attempting to create a driver.

If the authenticated user is not a restaurant or admin, `invalid token` response will be raised.
### Endpoint: /auth/drivers/  POST
```json
  {
    "email": "dummy@gmail.com",
    "password": "newpassword",
    "vehicle_image": "<FileData>",
    "vehicle_color": "red",
    "vehicle_description": "This is the vehicle description",
    "vehicle_number": "HGF203JS",
    "available": true
  }
```
After driver has been created, a verification code will be sent to the provided email
### Response
```json
{
  "message": "A verification code has been sent to dummy@gmail.com.",
  "user_id": 13,
  "driver_id": "qEBMwSQE",
  "role": "logistics"
}
```
### You can use the /auth/users/verify/ Endpoint to verify driver
```json
{
  "code": 2377,
  "user_id": 13
}
```

## Login the driver
</summary>
  
After the driver has been verified, he can log in with his`driver_id` and `password`.
### Endpoint: /auth/drivers/token/ POST

```json
{
  "driver_id": "qEBMwSQE",
  "password": "newpassword"
}
```

#### Response -- Success

```json
{
  "token": "3be550010c177b16209c9aabe9a28717d46870a3",
  "user_id": 13,
  "driver_id": "qEBMwSQE"
}

```

## Create Restaurant
</summary>
  
In order to create restaurant you must provide email and password

Note that only admins have the permissions to create restaurants.
You must have the authorization token in the header when attempting to create a restaurant.

If the authenticated user is not an admin, `invalid token` response will be raised.
### Endpoint: /auth/restaurants/  POST
```json
  {
    "email": "dummy@gmail.com",
    "password": "newpassword",
    "name": "Reyvers Restaurant",
    "description": "Best restaurant out there",
    "address": "Ijebu"
  }
```

After restaurant has been created, a verification code will be sent to the provided email

### Response
```json
{
  "message": "A verification code has been sent to dummy@gmail.com.",
  "user_id": 13,
  "kitchen_id": "qEBMwSQE",
  "role": "chef"
}
```
### You can use the /auth/users/verify/ Endpoint to verify restaurant
```json
{
  "code": 2377,
  "user_id": 13
}
```

## Login the restaurant
  
After the restaurant has been verified, he can log in with his`kitchen_id` and `password`.
### Endpoint: /auth/restaurants/token/ POST

```json
{
  "kitchen_id": "qEBMwSQE",
  "password": "newpassword"
}
```

#### Response -- Success

```json
{
  "token": "3be550010c177b16209c9aabe9a28717d46870a3",
  "user_id": 13,
  "kitchen_id": "qEBMwSQE"
}

```

## Change User Password
  
In order to change users password, the user token must be provided in the Authorization header.
## Endpoint /auth/users/change/password/ POST
### Payload
```json
  {
    "old_password": "myoldpassword",
    "new_password": "mynewestpassword",
    "confirm_new_password": "mynewestpassword"
  }

```

### Successful Response:

```json
  {"message": "Password was successfully updated."}
```

The following response will be received if an error occured:

```json
  {"password": ["old_password, new_password and confirm_new_password fields are required."]}
  {"password": ["Passwords do not match."]}
  {"password": ["Invalid user credentials. User does not exist."]}
  {"password": ["New password must be different from the previous passwords. "]}
  {"password": ["Old Password entered is incorrect"]}
  {"message": "Password was successfully updated."}
```
Some other password validation error will also occur when user password does not meet the validation score.

## Change User Driver and Kitchen IDs

In order to change users password, the user token must be provided in the Authorization header.
This endpoint changes the Ids for both kitchen and driver ids.
It can also change the username of the customer
## Endpoint /auth/users/change/username/

### Payload
```json
  {
    "username": "james"
  }

```
### Successful Response:

```json
  {"message": "Username was successfully updated."}
```

The following response will be received if an error occured:
```json
{"username": ["username field is required."]}
{"username": ["A user with username already exists. "]}
{"username": ["User does not exist."]}
```
  

## Get and Update Restaurant Profile information  
  
To get restaurant info, you need to provide a valid token in the authorization header.
And you must ensure that user is a restaurant/kitchen. If it's not a restaurant you will receive a permission denied message.

Note that this view is for the logged in restaurant user is updating its data.
This user can also update profile information like profile picture and others
with this endpoint: `/auth/users/me/`. Remember this enpoint is used to retrieve and modify profile data.
### Endpoint /auth/restaurants/me/ GET

No payload required for a GET request.
The Response gotten from the GET request is:

```json

  {
    "id": 1,
    "name": "Reyvers Kitchen",
    "description": "This is the Reyvers Kitchen.",
    "ratings": 0,
    "image": "/media/restaurant/image5-author.jpeg",
    "image_url": "https://image.com/po.png",
    "address": "Love address",
    "balance": "5600.00",
    "permissions": {
        "is_superuser": true,
        "is_driver": false,
        "is_restaurant": true,
        "is_customer": false
    }
}
```




### Endpoint /auth/restaurants/me/ PUT
Payload should look like this:
```json
{
  "name": "Reyvers Kitchen",
  "image": "<FileData>",
  "address": "1234 Sunny str. Ijebu",
  "rating": "3",
  "description": "This is the description"
}
```

Do not add kitchen_id here. This endpoint is for changing kitchen details, not changing kitchen_id.
To change kitchen_id, use the previous endpoint given: `/auth/users/change/username/`.

The following response will be received if an error occured:
```json
{"message": "User was not found"}
{"message": "User must be a chef. Permission denied."}
{"message":"You are not allowed to update kitchen id via this route"}
```

Some other error responses will also occur if the user data do not meet the validation score.

## How to Deduct The Restaurant Balance
  
### Endpoint /auth/restaurants/me/deduct/ PUT
In order to properly use this deduct endpoint, you must send an `amount` value from the following
payload:

```json
  {
    "amount": 2000
  }
```

The value sent over `amount` must be an integer or number. If it's not, it will return an error.
The value must not be greater than the restaurant amount. If it's not, it will return an error message.
Only restaurants have access to this endpoint or route.

If, on the other hand, the request was successful, the `amount` value sent will be deducted from the current amount of the restaurant with a success response.

### Error Response

```json
{
    "message": "amount is greater than current balance",
    "current_balance": 0.0
}
{"message": "User was not found"}

{"message": "User must be a chef. Permission denied."}

{"message": "amount is required"}

{"message": "amount must be an integer"}


```

### Successful Response
```json
{"message": "Balance has been updated successfully!", "current_balance": 3000.50}

```

## Save restaurant withdrawal history
  
After the deductions have been made in the restaurant it is only meaningful to send
the request update the withdrawal history of the restaurant.
This can be achieved thus:
### Endpoint /auth/restaurants/me/withdrawals/ POST and GET
A POST request will send the list of withdrawals made by a particular restaurant given 
the token is correct. Note that, like every other restaurant view, only restaurant users
can make this request to the backend. Note that this is actually the withdrawal deduction made from 
flutterwave.

### GET Response - An Array of withdrawal history:
```json
[
    {
        "id": 2,
        "account_bank": "9001",
        "account_number": "54534543490",
        "amount": 600,
        "currency": "NGN",
        "narration": "Payment for things",
        "reference": "XYJKSGJJAHHSHJKSJ",
        "restaurant": {
            "id": 1,
            "name": "",
            "description": "",
            "ratings": 0,
            "image_url": null,
            "address": "",
            "balance": 0.0
        },
        "user": 1
    },
    {
        "id": 3,
        "account_bank": "044",
        "account_number": null,
        "amount": 200,
        "currency": "NGN",
        "narration": "Payment for things",
        "reference": "XYJKSGJJAHHSHJKSJ",
        "restaurant": {
            "id": 1,
            "name": "",
            "description": "",
            "ratings": 0,
            "image_url": null,
            "address": "",
            "balance": 0.0
        },
        "user": 1
    },
    {
        "id": 4,
        "account_bank": "9001",
        "account_number": "78967767667",
        "amount": 600,
        "currency": "NGN",
        "narration": "Payment for things",
        "reference": "XYJKSGJJAHHSHJKSJ",
        "restaurant": {
            "id": 1,
            "name": "",
            "description": "",
            "ratings": 0,
            "image_url": null,
            "address": "",
            "balance": 0.0
        },
        "user": 1
    }
]


```

## POST Request:
The POST request only requires five items in the payload as seen below:

```json
{
  "account_bank": "9001",
  "account_number": "54534543490",
  "amount": 600,
  "currency": "NGN",
  "narration": "Payment for things"
}
```

## Detail PUT and DELETE request --- 
### Endpoint /auth/restaurants/me/withdrawals/(id)/ PUT and GET and DELETE

This returns a single item from the withdrawal history as:

```json

{
        "id": 2,
        "account_bank": "9001",
        "account_number": "54534543490",
        "amount": 600,
        "currency": "NGN",
        "narration": "Payment for things",
        "reference": "XYJKSGJJAHHSHJKSJ",
        "restaurant": {
            "id": 1,
            "name": "",
            "description": "",
            "ratings": 0,
            "image_url": null,
            "address": "",
            "balance": 0.0
        },
        "user": 1
    }

```
The endpoint takes in the `id` of a single item in the withdrawal history and 
returns it as the above json object.

A `DELETE` operation can also be performed on the withdrawal history by calling the `DELETE` HTTP Method.




### Error Response:

```json
{"messge": "User must be a restaurant or chef"}
{"message": "Restaurant does not exists."}
{"message": "Http method not allowed"}
{"message": "Restaurant Withdrawal does not exists."}


```


## Successful Response:

```json
{"message": "Restaurant withdrawal history deleted successfully"}
```
A successful response could also return the object created and a successful
status code of 200 OK Response.


###

## Get and Update Driver Profile information
  
To get driver info, you need to provide a valid token in the authorization header.
And you must ensure that user is a driver/logistics. If it's not a driver you will receive a permission denied message.

Note that this view is for the logged in driver user is updating its data.
This user can also update profile information like profile picture and others
with this endpoint: `/auth/users/me/`. Remember this enpoint is used to retrieve and modify profile data.
### Endpoint /auth/drivers/me/ GET

No payload required for a GET request.
### Endpoint /auth/drivers/me/ PUT
Payload should look like this:
```json
{
  
  "vehicle_color": "Gold",
  "vehicle_description": "Vehicle Description",
  "vehicle_number": "GLU23HS",
  "available": true,
  
}
```

Do not add `driver_id` here. This endpoint is for changing kitchen details, not changing kitchen_id.
To change driver_id, use the previous endpoint given: `/auth/users/change/username/`.

The following response will be received if an error occured:
```json
{"message": "User was not found"}
{"message": "User must be a chef. Permission denied."}
{"message":"You are not allowed to update driver id via this route"}
```

Some other error responses will also occur if the user data do not meet the validation score.


# List of Restaurants and Dishes
  
For all endpoints, the client must make request with a valid token in the Authorization header.

## Restaurants
### /api/restaurants/ GET
The above enpoint retrieves the list of restaurants and their information for all users to see.
The only constraint here is that users are only allowed to access it with their token in the `Authorization` header. If no token is found in the Authorization request header, a  `Authentication credentials were not provided` response  will be raised or a `Invalid token` response if the token in the header is invalid. The JSON object returned from this request as response is as follow:

```json

{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 2,
            "name": "Kada Plaza",
            "description": "This is Kada Plaza",
            "ratings": "0.0",
            "image": null,
            "address": "ReyversKitchen's Kitchen Address"
        },
        {
            "id": 1,
            "name": "ReyversKitchen",
            "description": "This is ReyversKitchen",
            "ratings": "3.0",
            "image": "https://res.cloudinary.com/dqevhwn0e/image/upload/v1/media/restaurant/Screen_Shot_2024-01-24_at_3.16.15_PM_hyvbl7",
            "address": "ReyversKitchen's Kitchen Address"
        }
    ]
}

```
The response above `count` represents the number of items in the list or array data structure. 
The `next` indicate the endpoint for the next set of items; `prev` does quite the opposite.


### /api/restaurants/(id)/ GET
The above endpoint is used to retrieve the detail view of any given restaurant in the database.
The response below will be given if the request was successful:

```json
{
    "id": 1,
    "name": "",
    "image": null,
    "description": "",
    "ratings": "0.0",
    "address": "",
    "dishes": [
        {
            "id": 2,
            "name": "Fried Rice",
            "description": "This is my favorite dish abeg.",
            "price": "300.00",
            "restaurant": 1,
            "ratings": "4.0",
            "favourite": [
                2
            ],
            "restaurant_details": {
                "name": "",
                "ratings": 0.0
            },
            "get_category": {
                "id": 2,
                "name": "english meals",
                "image": "/media/category/Screen_Shot_2024-01-24_at_3.14.41_PM.png"
            },
            "images": [
                {
                    "id": 1,
                    "file": "/media/dishes/wiz_C06uxkq.png",
                    "label": "image 1"
                },
                {
                    "id": 2,
                    "file": "/media/dishes/wiz_RG5bfCI.png",
                    "label": "Image 2"
                }
            ],
            "category": 1
        },
        {
            "id": 1,
            "name": "Jollof Rice",
            "description": "This is the best food you have ever tasted",
            "price": "400.00",
            "restaurant": 1,
            "ratings": "5.0",
            "favourite": [],
            "restaurant_details": {
                "name": "",
                "ratings": 0.0
            },
            "get_category": {
                "id": 1,
                "name": "english meals",
                "image": "/media/category/Screen_Shot_2024-01-24_at_3.14.41_PM.png"
            },
            "images": [
                {
                    "id": 1,
                    "file": "/media/dishes/wiz_C06uxkq.png",
                    "label": "image 1"
                },
                {
                    "id": 2,
                    "file": "/media/dishes/wiz_RG5bfCI.png",
                    "label": "Image 2"
                }
            ],
            "category": 1
        }
    ]
}

```

## Ingredients
</summary>
  
### /api/ingredients/ GET, POST

The ingredients endpoint retrieves all the ingredients in the database.
The client should expect a response like when making a GET request:

```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "image_url": "https://f.com/tomatoes.png",
            "name": "tomatoes"
        },
        {
            "id": 2,
            "image_url": "https://f.com/garden_egg.png",
            "name": "garden egg"
        }
    ]
}

```

The `image_url` field is optional.

### Error Response
```json
{
    "name": [
        "Ingredient with this name already exists."
    ]
}

```



### /api/ingredients/(id)/ GET, PUT, DELETE
The above endpoint retrieves, update or delete a single instance of ingredient in the database.

## Dishes

### /api/dishes/ GET, POST

The dishes endpoint retrieves all the dishes or food items in the database.

The client should expect a response like when making a GET request:

```json
  {
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 3,
            "name": "Swallow fufu",
            "description": "This is the description",
            "price": "3000.00",
            "restaurant": 1,
            "ratings": "0.0",
            "favourite": [],
            "restaurant_details": {
                "name": "",
                "ratings": 0.0
            },
            "get_category": {
                "id": 3,
                "name": "english meals",
                "image": "https://res.cloudinary.com/dqevhwn0e/image/upload/v1/media/category/Screen_Shot_2024-01-24_at_3.14.41_PM.png"
            },
            "images": [
                {
                    "id": 3,
                    "file": "https://res.cloudinary.com/dqevhwn0e/image/upload/v1/media/category/Screen_Shot_2024-01-24_at_3.14.41_PM.png",
                    "label": ""
                }
            ],
            "image_urls": [
                {
                    "id": 4,
                    "url": "https://f.com/fgh.png"
                },
                {
                    "id": 5,
                    "url": "https://f.com/fgh.png"
                },
                {
                    "id": 6,
                    "url": "https://f.com/fgh.png"
                }
            ],
            "category": 1
        },
        {
            "id": 2,
            "name": "Fried Rice",
            "description": "This is my favorite dish abeg.",
            "price": "300.00",
            "restaurant": 1,
            "ratings": "4.0",
            "favourite": [
                2
            ],
            "restaurant_details": {
                "name": "",
                "ratings": 0.0
            },
            "get_category": {
                "id": 2,
                "name": "english meals",
                "image": "https://res.cloudinary.com/dqevhwn0e/image/upload/v1/media/category/Screen_Shot_2024-01-24_at_3.14.41_PM.png"
            },
            "images": [
                {
                    "id": 1,
                    "file": "https://res.cloudinary.com/dqevhwn0e/image/upload/v1/media/category/Screen_Shot_2024-01-24_at_3.14.41_PM.png",
                    "label": "image 1"
                },
                {
                    "id": 2,
                    "file": "https://res.cloudinary.com/dqevhwn0e/image/upload/v1/media/category/Screen_Shot_2024-01-24_at_3.14.41_PM.png",
                    "label": "Image 2"
                }
            ],
            "image_urls": [
                {
                    "id": 4,
                    "url": "https://f.com/fgh.png"
                },
                {
                    "id": 5,
                    "url": "https://f.com/fgh.png"
                },
                {
                    "id": 6,
                    "url": "https://f.com/fgh.png"
                }
            ],
            "category": 1
        },
        {
            "id": 1,
            "name": "Jollof Rice",
            "description": "This is the best food you have ever tasted",
            "price": "400.00",
            "restaurant": 1,
            "ratings": "5.0",
            "favourite": [],
            "restaurant_details": {
                "name": "",
                "ratings": 0.0
            },
            "get_category": {
                "id": 1,
                "name": "english meals",
                "image": "https://res.cloudinary.com/dqevhwn0e/image/upload/v1/media/category/Screen_Shot_2024-01-24_at_3.14.41_PM.png"
            },
            "images": [
                {
                    "id": 1,
                    "file": "https://res.cloudinary.com/dqevhwn0e/image/upload/v1/media/category/Screen_Shot_2024-01-24_at_3.14.41_PM.png",
                    "label": "image 1"
                },
                {
                    "id": 2,
                    "file": "https://res.cloudinary.com/dqevhwn0e/image/upload/v1/media/category/Screen_Shot_2024-01-24_at_3.14.41_PM.png",
                    "label": "Image 2"
                }
            ],
            "image_urls": [
                {
                    "id": 4,
                    "url": "https://f.com/fgh.png"
                },
                {
                    "id": 5,
                    "url": "https://f.com/fgh.png"
                },
                {
                    "id": 6,
                    "url": "https://f.com/fgh.png"
                }
            ]
            "category": 1
        }
    ]
}

```


For a POST request, you can decide to use a formData to send your request with the following body parameters `name`, `images`, `description`, `price`, `restaurant`, `category` and payload:

```json
{
  "name":"Rice",
  "description":"This is the best food you have ever tasted",
  "price":4000,
  "restaurant":1,
  "category":2,
  "delivery_options":"paid",
  "time_duration":20,
  "images": "[ListOfImages base64]",
  "ingredients":[1,2,3,4],
  "all_images": [
    "https://f.com/fgh.png",
    "https://f.com/fgh.png",
    "https://f.com/fgh.png"
  ]
}

```
The `images` field is best handled using formData. But you can use it in other ways based on your use case.

You have an option to send an array of images in the `all_images` field.


The `ingredients` field is a list or array of ids. Each id must be attributed to an ingredient instance, meaning you must first fetch the ingredients, retrieve their ids and make a request.

### /api/dishes/(id)/ GET

The `id` parameter is used to get a specific dish. If a non-existent id is not provided, a 404 NOT FOUND response would be received by the client. In order to avoid this the right id must be given.


The expected response gotten will be as follows:


```json

{
    "id": 3,
    "name": "Swallow fufu",
    "description": "This is the description",
    "price": "3000.00",
    "restaurant": 1,
    "ratings": "0.0",
    "favourite": [],
    "_ingredients": [
        "onions",
        "carrot",
        "green peas"
    ],
    "restaurant_details": {
        "name": "",
        "ratings": 0.0
    },
    "get_category": {
        "id": 3,
        "name": "english meals",
        "image": "https://res.cloudinary.com/dqevhwn0e/image/upload/v1/media/category/Screen_Shot_2024-01-24_at_3.14.41_PM.png"
    },
    "image_urls": [
        {
            "id": 4,
            "url": "https://f.com/fgh.png"
        },
        {
            "id": 5,
            "url": "https://f.com/fgh.png"
        },
        {
            "id": 6,
            "url": "https://f.com/fgh.png"
        }
    ],



    "images": [
        {
            "id": 3,
            "file": "https://res.cloudinary.com/dqevhwn0e/image/upload/v1/media/category/Screen_Shot_2024-01-24_at_3.14.41_PM.png",
            "label": ""
        }
    ],
    "category": 1
}

```
### /api/dishes/(id)/ GET, PUT, DELETE
Get request retrieves a single item by `id`.
The delete and the put requests are used for updating or permanently deleting the dish item.

The PUT request has a payload similar to that of the POST request, altghough you must ensure that
that every request ends in a slash (/).
  


# Categories
  
## /api/categories/ GET, POST
For Categories, the above endpoint can be used to likewise perform POST and GET operations.
The endpoint retrieves all the category data in the database. It also creates new categories with unique names. This depends on the method used in the request, whether a GET or POST request.

The Payload the client should expect to receive from a GET request is as follows:

```json
{
    "count": 1,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "english meals",
            "image": "https://res.cloudinary.com/dqevhwn0e/image/upload/v1/media/category/Screen_Shot_2024-01-24_at_3.14.41_PM.png"
        }
    ]
}

```

Here, every category returns a paginated response of `id`, `name` and `image` in the payload.

Post request, on the other hand, does a different thing. It creates a new `category` with the following payload:

```json
  {
    "name": "traditional dishes",
    "image": "<FileData base64>"
  }

```
After being created, the response will contain the payload created.



## /api/categories/(id)/ GET, PUT, DELETE
The GET request will retrieve a single item based on the id provided as parameter.

The delete and the put requests are used for updating or permanently deleting categories.
The delete request does not need any payload, only the `id` parameters is received by the backend service and act upon. 

The PUT request, on the other hand requires a payload, same as the POST request.


# Pagination
</summary>
  
The pagination is used with Query Parameters like:

`https://example.com/api/categories/?page_size=10&page=1`

Those are the default values for `page` and `page_size`. There is usually 10 items in one page. If your page is 2, I guess you'll receive the next 10 items, depending on your page size. If your `page_size` is 20, it means you want 20 items per page...


And the `⁠count` attribute is used to tell the number of items there are per page. So with it you can set a limit to your frontend, make it not fetch anymore data once you've arrived at the `⁠count⁠`.

# PAYMENT INTEGRATION WITH STRIPE
  
In order for payments to be processed a payment intent must be created using strip.
The client should send an object containing the amount the total amount to be paid 
to the server with the following url endpoint:

## /api/payment/intent/ POST
```json
{
  "amount": 2000,
  "currency_code": "usd"
}

```
The above amount value `2000` in the payload represent `20 usd` which is equivalently `20 * 100` or `{total} * 100`. 
After the payment intent has been created, the client will get back a success response with the following response body :

```json
  {
    "payment_intent_secret": "pi_3OhHi24eGaAoGO3h0u6gK1j_secret_sNrZa3Vl0XQj9dDoCRTWERZSo"
  }

```

### Potential error responses:
These errors occur when a currencies with relatively low exchange rate like Naira is used with stripe.

```json
{
    "message": "Something went wrong: Request req_8xS8MfJKBnov7c: Amount must convert to at least 50 cents. 0.20 ₦ converts to approximately €0.00."
}

{
    "message": "Something went wrong: Request req_IpeDAKfFWG8KQw: Amount must be no more than 999,999.99 ₦"
}

{
    "message": "Something went wrong: Unexpected error communicating with Stripe.  If this problem persists,\nlet us know at support@stripe.com.\n\n(Network error: ConnectionError: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response')))"
}

```

- The first error response would occur only when the amount in naira is relatively lesser than 50 American cents.
- The second error response, on the other hand, would occur if the value in naira is greater than ₦999,999.

- The fourth is as a result of network error.


# Create orders
  
## /api/orders/ POST
When a customer creates an order, the client should send the following payload to the backend service:

```json
  {
    "total_price": 6800,
    "payment_status": true,
    "is_delivered": false,

    "items": [
        {
            "dish_id": 1,
            "restaurant_id": 1,
            "amount": 400,
            "quantity": 2
        },
        {
            "dish_id": 3,
            "restaurant_id": 1,
            "amount": 3000,
            "quantity": 2

        }
    ]

}

```
`payment_status` is a boolean value.
It should be set to `true` if payments were successfull.

`is_delivered` status can be modified later, but its default value is `false`. 

The `total_price` must correllate with the total price of all the `items` in the `items` array.
This is to say the `total_price` must be `(item[0].amount * item[0].quantity) + (item[2].amount * item[2].quantity)`. If there is no correlation, an error response would be raised.


For each item in the array of items in the payload, the `dish_id` field is the id of the dish you are sending from the cart data. The `restaurant_id` is the unique id of the restaurant. Please note that this is not the same as the `kitchen_id`. The `kitchen_id` is only used for user authentiction. 

## Response body
```json

{
    "id": 66,
    "user": 2,
    "total_price": 6800,
    "created_at": "2024-02-08T12:53:28.862377Z",
    "is_delivered": false,
    "payment_status": true,
    "items": [
        {
            "id": 71,
            "quantity": 2,
            "amount": 400,
            "status": "pending",
            "dish": {
                "id": 1,
                "name": "Jollof Rice",
                "time_duration": 0,
                "description": "This is the best food you have ever tasted",
                "price": 400,
                "restaurant": 1,
                "ratings": "5.0",
                "restaurant_details": {
                    "name": "",
                    "ratings": 0.0
                },
                "get_category": {
                    "id": 1,
                    "name": "english meals",
                    "image": "/media/category/Screen_Shot_2024-01-24_at_3.14.41_PM.png"
                },
                "images": [
                    {
                        "id": 1,
                        "file": "/media/dishes/wiz_C06uxkq.png",
                        "label": "image 1"
                    },
                    {
                        "id": 2,
                        "file": "/media/dishes/wiz_RG5bfCI.png",
                        "label": "Image 2"
                    }
                ]
            },
            "driver": null
        },
        {
            "id": 72,
            "quantity": 2,
            "amount": 3000,
            "status": "pending",
            "dish": {
                "id": 3,
                "name": "Swallow Eba",
                "time_duration": 0,
                "description": "This is the description",
                "price": 3000,
                "restaurant": 1,
                "ratings": "0.0",
                "restaurant_details": {
                    "name": "",
                    "ratings": 0.0
                },
                "get_category": {
                    "id": 3,
                    "name": "english meals",
                    "image": "/media/category/Screen_Shot_2024-01-24_at_3.14.41_PM.png"
                },
                "images": [
                    {
                        "id": 3,
                        "file": "/media/dishes/ananthu-ganesh-qHvgQUE43a8-unsplash.jpg",
                        "label": ""
                    }
                ]
            },
            "driver": null
        }
    ]
}


```

# Get Recent order items
  
## /api/orderitems/ GET
## /api/orderitems/(id)/ GET

The response from the order items endpoint is dependent on the authenticated user based on the auth token provided in the http header. 

In order to fetch the user's orders, whether they be driver, restaurant or customer, the client should send a GET request to the above endpont.
How this works is that the user will see all his orders and can also get the detail of orders if they request based on the `id`. 

## Response Body

```json
[
    {
        "id": 66,
        "quantity": 2,
        "amount": 300,
        "status": "completed",
        "dish": {
            "id": 2,
            "name": "Fried Rice",
            "time_duration": 30,
            "description": "This is my favorite dish abeg.",
            "price": 300,
            "restaurant": 1,
            "ratings": "4.0",
            "restaurant_details": {
                "name": "",
                "ratings": 0.0
            },
            "get_category": {
                "id": 2,
                "name": "english meals",
                "image": "/media/category/Screen_Shot_2024-01-24_at_3.14.41_PM.png"
            },
            "images": [
                {
                    "id": 1,
                    "file": "/media/dishes/wiz_C06uxkq.png",
                    "label": "image 1"
                },
                {
                    "id": 2,
                    "file": "/media/dishes/wiz_RG5bfCI.png",
                    "label": "Image 2"
                }
            ]
        },
        "driver": {
            "id": 1,
            "driver_id": "Jose",
            "vehicle_image": null,
            "restaurant": 1,
            "vehicle_color": "red",
            "vehicle_description": "The vehicle is red",
            "vehicle_number": "398GHS293",
            "available": true,
            "current_location_latitude": null,
            "current_location_longitude": null
        }
    }
]

```

### Using Query Parameters to determine the nature of response
  
In order to get the orderitems that should be listed as `history` or `ongoing`, query parameters are used in the request.
For instance, if you intend on getting historical data of the order items, you should send your request to the orderitems endpoint and a query parameter should be sent as well as follows:

### /api/orderitems/?option=history GET
Or
### /api/orderitems/?option=ongoing GET
Note that `option` is the key and `ongoing` or `history` are the values of the query.
The query parameters will determine the result gotten from the response body.
The `ongoing` option will return `pending` orders. 
The `history` option, on the other hand, will return all the orders that are that are either `completed` or `cancelled`.

This is the same for all users.

### Orders can also be updated via a PUT request.
## /api/orderitems/(id)/ PUT

In order to change order items fields like `driver` assigned. You need to provide the payload containing either the `driver` id or `status`.

```json

  {
    "status": "completed"
  }

```

The `status` must be one of the following options: -- `completed`, `pending` or `cancelled`. The client must send one of the following as the current status: `completed`, `pending` or `cancelled`.
When an order is saved, the status of the each item in the items array is `pending`. The client can update it using the above endpoint.


### Assigning Drivers to orderitems via a PUT request.
  
## /api/orderitems/drivers/assign/?option=add_driver PUT
## Or
## /api/orderitems/drivers/assign/?option=remove_driver PUT
 In order to successfully assign a driver to an orderitem, the `id` of the item and driver must be sent to the backend in the following payload:

```json
{
  "orderitem_id": 1,
  "driver_id": 1
}

```
The `option` parameter is required. It tells the backend service what it is you are trying to do.
The `option` parameter should be one of two values: `add_driver` or `remove_driver`.
To `add_driver` means you are trying to assign driver to a particular orderitem instance.
To `remove_driver` means the opposite.

The two parameters in the payload, `orderitem_id` and `driver_id` respectively, are the unique `id` of both the driver and the orderitem in question. 

The `driver_id` field should be the id of the driver you wish to assign.
The `orderitem_id` field, on the other hand, should be the id of the orderitem you wish to modify.

To add driver, you should send the payload to `/api/orderitems/drivers/assign/?option=add_driver` with the above payload.
To remove driver, you should send the payload to `/api/orderitems/drivers/assign/?option=remove_driver`


### Expected Success Response:
```json
{"message": "Driver: jake@gmail.com assigned successfully to ordered item"}

```

### Expected Error Response:
```json
{"message": "driver_id field is required."}
{"message": "option query parameter is required."}
{"message": "User must be a restaurant"}
{"message": "Order item does not exist"}
{"message": "Driver with id: {driver_id} does not exist your restaurant"}
{"message": "Select a valid option --- add_driver or remove_driver"}

```

# Rating dishes
  
## Rate a particular dish
## /api/dishes/(id)/ratings/ POST

The parameters to rate a dish is the `id` of the dish. 

### Request payload
```json

  {
  "rating_number": 2,
  "rating_text": "This is my text update forever"
  }

```
While the `rating_number` payload field is required, the `rating_text` payload field is not a required field.
<br>
The `rating_number` payload field is expected to be a number or an integer.
If the client does not send an integer, the following error will be
raised:

```json

{
  "message": "rating_number must be an integer"
}

```
If the `rating_number` is not given, the following error response will be given:
```json
{
  "message": "rating_number is required"
}
```
If, similarly, a dish with the underlying `id` does not exist, an error will also be raised:

```json
{
  "message": "dish with id not found"
}
```

## Get the rating data for a particular dish
  
## /api/dishes/(id)/ratings/ GET
In order to retrieve all the rating data for a particular dish, the client should make a get request to the above endpoint. The rating data consists of the `number` of rating, `text` or recommendation of user, `user_data` which is the author's details and `dish` information.



### Response:
```json
  [
  {
    "number": 4,
    "text": "This is my text update forever",
    "user_data": {
      "display_image": "/static/images/user-icon-no-image.png",
      "email": "admin@gmail.com",
      "role": "chef"
    },
    "dish": {
      "id": 1,
      "name": "rice",
      "images": [
        {
          "id": 1,
          "file": "/media/dishes/removal.ai_9f48d15f-89ad-4488-9ccf-e85a5155cdb5-new-me_TXD2Q8_zmk80jx.png",
          "label": ""
        }
      ]
    }
  }
]

```
The above response is an array of objects. Each object consists of each user's review.
Note that it is only the review that is approved by the admin will show.

# Rating restaurants
  
## Rate a particular restaurant
## /api/ingredients/ POST GET






# Rating restaurants
## Rate a particular restaurant
## /api/restaurants/(id)/ratings/ POST

The parameters to rate a restaurant is the `id` of the restaurant. 

### Request payload
```json

  {
  "rating_number": 2,
  "rating_text": "This is my text update forever"
  }

```
While the `rating_number` payload field is required, the `rating_text` payload field is not a required field.
<br>
The `rating_number` payload field is expected to be a number or an integer.
If the client does not send an integer, the following error will be
raised:

```json

{
  "message": "rating_number must be an integer"
}

```
If the `rating_number` is not given, the following error response will be given:
```json
{
  "message": "rating_number is required"
}
```
If, similarly, a restaurant with the underlying `id` does not exist, an error will also be raised:

```json
{
  "message": "restaurant with id not found"
}
```

## Get the rating data for a particular restaurant
  
## /api/restaurants/(id)/ratings/ GET
In order to retrieve all the rating data for a particular restaurant, the client should make a get request to the above endpoint. The rating data consists of the `number` of rating, `text` or recommendation of user, `user_data` which is the author's details and `restaurant` information.

### Response:
```json
  [
  {
    "number": 4,
    "text": "This is my text update forever",
    "user_data": {
      "display_image": "/static/images/user-icon-no-image.png",
      "email": "admin@gmail.com",
      "role": "chef"
    },
    "restaurant": {
      "id": 1,
      "name": "Reyvers Kitchen",
      "description": "This is a silly description",
      "image": "/media/restaurant/removal.ai_9f48d15f-89ad-4488-9ccf-e85a5155cdb5-new-me_TXD2Q8_VYoncWM.png",
      "address": "This is Reyvers Kitchen Address"
    }
  }
]

```
The above response is an array of objects. Each object consists of each user's review.




# Rating drivers
  
<!-- Rating Driver -->

## Rate a particular driver
## /api/drivers/(id)/ratings/ POST

The required parameter to rate a driver is the `id` of the driver. 

### Request payload
```json

  {
  "rating_number": 2,
  "rating_text": "This is my rating text"
  }

```
While the `rating_number` payload field is required, the `rating_text` payload field is not a required field.

The `rating_number` payload field is expected to be a number or an integer ranging from `1-5`.
If the client does not send an integer, the following error will be
raised:

```json

{
  "message": "rating_number must be an integer"
}

```
If the `rating_number` is not given, the following error response will be given:
```json
{
  "message": "rating_number is required"
}
```
If, similarly, a driver with the underlying `id` does not exist, an error will also be raised:

```json
{
  "message": "driver with id not found"
}
```


## Get the rating data for a particular driver
  
## /api/drivers/(id)/ratings/ GET
In order to retrieve all the rating data for a particular driver, the client should make a get request to the above endpoint. The rating data consists of the `number` of rating, `text` or recommendation of user, `user_data` which is the author's details and `driver` information.

### Response:
```json
  [
    {
        "number": 4,
        "text": "This is my text update forever with love for driver",
        "user_data": {
            "display_image": "",
            "email": "jacobcode@gmail.com",
            "username": "51M07fbk",
            "role": "logistics"
        },
        "driver": {
            "user": 3,
            "name": "Daniel Osifo", 
            "vehicle_image_url": null,
            "vehicle_color": "red",
            "vehicle_description": "Lovely car",
            "vehicle_number": "ZOISJ342",
            "available": false,
            "profile_details": {
                "name": "Daniel Osifo", 
                "image_url": "https://somesite.com/image.png",
                "date_of_birth": "2020-02-02",
                "phone_number": "+234892993839",
                "bio": "This is a fantastic bio"
            }
        }
    },
    {
        "number": 4,
        "text": "This is my text update forever with love for driver from someone else",
        "user_data": {
            "display_image": "",
            "email": "admin@gmail.com",
            "username": "aMuuNZLh",
            "role": "chef"
        },
        "driver": {
            "user": 3,
            "driver_id": "51M07fbk",
            "vehicle_image_url": null,
            "vehicle_color": "red",
            "vehicle_description": "Lovely car",
            "vehicle_number": "ZOISJ342",
            "available": false,
            "profile_details": {
                "name": "Daniel Osifo", 
                "image_url": "https://somesite.com/image.png",
                "date_of_birth": "2020-02-02",
                "phone_number": "+234892993839",
                "bio": "This is a fantastic bio"
            }
        }
    }
  ]
```
The above response is an array of objects. Each object consists of each user's review.


# Get the Analytics data for a particular Driver or Restaurant
  
## Restaurant
## /auth/restaurants/analytics/ GET

In order to get the analytics data for restaurant, the user making the request must be a restaurant as indicated in the Authentication Header Token. If the user is not a restaurant or chef, an error would be raised. This is because the auth header is used to identify the user.

If the restaurant passes the test of authentication, a response is given as thus:

```json
{
    "message": "Here's your analytics",
    "analytics": {
        "completed_orders_count": 0,
        "pending_orders_count": 2,
        "cancelled_orders_count": 0,
        "total_orders": 2,
        "reviews": {
            "restaurant_ratings": 4.0,
            "reviews_count": 1
        },
        "num_available_drivers": 1,
        "total_revenue": 5000.0
    }
}

```



## Driver
## /auth/drivers/analytics/ GET

In order to get the analytics data for driver, the user making the request must be a driver as indicated in the Authentication Header Token. If the user is not a driver or chef, an error would be raised. This is because the auth header is used to identify the user.

If the driver passes the test of authentication, a response is given as thus:

```json
{
    "message": "Here's your analytics",
    "analytics": {
        "completed_orders_count": 0,
        "pending_orders_count": 1,
        "cancelled_orders_count": 0,
        "total_orders": 1,
        "reviews": {
            "driver_ratings": 4.0,
            "reviews_count": 2
        }
    }
}

```






