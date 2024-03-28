from typing import Annotated
from fastapi import Depends, FastAPI, Form, HTTPException, Header
from auth import auth
from models import RoleBasedUser
from sqlalchemy import Select
from sqlalchemy.exc import IntegrityError
from database_connection import session
from pydantic import BaseModel, EmailStr

app = FastAPI(title="RBAC")

class UserAddModel(BaseModel):
    username:str
    password:str
    email:EmailStr|None=None



@app.get('/')
def home():
    return "Hello"


@app.post('/login/')
def login(username: str= Form(),password:str= Form()):
    print(username, password)
    user = session.execute(Select(RoleBasedUser).where(RoleBasedUser.username==username)).one_or_none()
    if user:
        access_token,refresh_token = auth.generate_JWT(username, user[0].role)
        valid_password = auth.verify_password(password,user[0].password,)
        if valid_password:
            return {
                "Sucess":"Login Sucesfull",
                "Tokens":{
                    "access_token": access_token,
                    "refresh_token": refresh_token
                }
            }
        else:
            raise HTTPException(
                status_code=401,
                detail={
                    'error':'UNAUTHORIZED',
                    'error_message':'Can\'t verify password'

                }
            )
    else:
            raise HTTPException(
                status_code=401,
                detail={
                    'error':'UNAUTHORIZED',
                    'error_message':'Can\'t verify username'
                    
                }
            )
    
def token_in_header(Authorization:str = Header()):
    token_splitted = Authorization.split(" ",1)
    if token_splitted[0].lower() =='bearer':
        return auth.decodAccessJWT(token_splitted[1])
               
    else:
        raise HTTPException(
            status_code=401,
            detail= "Invalid token Scheme"
        )
    
def is_allowed(payload =Depends(token_in_header)):
    if payload['role'] == 'admin':
        return 'Hello'
    raise HTTPException(
        status_code=401,
        detail={
            'error': "UNAUTHORIZED",
            'message': "You don't have access to view this endpoint"
        }
    )


@app.get('/test')
def test(return_value=Depends(is_allowed)):
    return return_value

@app.post('/user', status_code=201)
def add_user(useraddmodel:UserAddModel):
    useraddmodel.password = auth.hash_password(useraddmodel.password)
    user_to_add = RoleBasedUser(**useraddmodel.__dict__)
    session.add(user_to_add)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=400,
            detail={
                'error': "Bad Request",
                'message':'User with same username already exsist'
            }
        )
    return "User Added sucesfully"