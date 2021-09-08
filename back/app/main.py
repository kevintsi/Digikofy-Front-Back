from typing import List
import uvicorn
from fastapi import FastAPI, status, Response
from .modules.response_models import UserAuthentication, Coffee, UserRefreshToken
from .modules.services import UserService, CoffeeService
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="DigikofyAPI")

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", status_code=status.HTTP_200_OK, tags=["Home"])
def home():
    """
        Index page
    Args:
        response (Response): [index]
    """
    return {"message" : "Everything works fine"} 


###### USER ROUTE ########

@app.post("/register", status_code=status.HTTP_201_CREATED, tags=["User"])
async def register(data: UserAuthentication, response: Response):
    """
        Route to register the user in the database

        Args:
            data (UserAuthentication): [Information needed to register the user]
            response (Response): [Response returned (status code)]
    """
    code = UserService().create_user(data)
    if code == 201:
        print('Sucessfully created new user')
    elif code == 409:
        print("An user with this email address already exists")
        response.status_code = status.HTTP_409_CONFLICT
    else:
        print("Something went wrong")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


@app.post("/login", status_code=status.HTTP_200_OK, tags=["User"])
async def login(data: UserAuthentication, response: Response):
    """
        Route to log in the user

        Args:
            data (UserAuthentication): [Information needed to log in]
            response (Response): [Response returned (status code)]

        Returns:
            [Object]: [Object containing id token, refresh_token]
    """
    res = UserService().log_in_user(data)
    if res is not None:
        return res
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED

@app.post("/refreshToken", status_code=status.HTTP_200_OK, tags=["User"])
async def refresh_token(data : UserRefreshToken, response : Response):
    """
        Route to get a new id token with the refresh token given

        Args:
            data (UserRefreshToken): [Information needed to get a new id token]
            response (Response): [Response returned (status code)]

        Returns:
            [Object]: [Object containing id token, refresh_token]
    """
    res,code = UserService().get_new_token(data)
    if res is not None:
        return res
    elif code == 403:
        response.status_code = status.HTTP_403_FORBIDDEN

@app.post("/revoke", status_code=status.HTTP_200_OK, tags=["User"])
async def revoke_refresh_token(data : UserRefreshToken):
    """
        Route to log out and revoke the refresh token

        Args:
            data (UserRefreshToken): [Information needed to revoke refresh token]
    """
    UserService().revoke_refresh_token(data)

######## COFFEE'S ROUTE ##########


@app.get("/coffees", status_code=status.HTTP_200_OK, response_model=List[Coffee], tags=["Coffee"])
async def get_coffee(response: Response):
    """
        Route that returns all coffees

        Args:
            response (Response): [Response returned (status code)]
        Returns:
            [List[Coffee]]: [List of coffees]
    """
    (code, data) = CoffeeService().get_coffee()
    print(code)
    if code == 200:
        return data
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


@app.get("/coffee/{id}", status_code=status.HTTP_200_OK, response_model=Coffee, tags=["Coffee"])
async def get_coffee_by_id(id: str, response: Response):
    """
        Route that return the coffee with the given id

        Args:
            id (str): [Id coffee]
            response (Response): [Response returned (status code)]
        Returns:
            [Coffee]: [Coffee with the given id]
    """
    (code, data) = CoffeeService().get_coffee_by_id(id)
    print(code, data)
    if code == 200:
        return data
    elif code == 404:
        response.status_code = status.HTTP_404_NOT_FOUND
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
