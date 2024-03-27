from typing import Annotated
from fastapi import Depends, FastAPI, Form, HTTPException, Header
from auth import auth
from models import RoleBasedUser
from sqlalchemy import Select
from database_connection import session

app = FastAPI(title="RBAC")

@app.get('/')
def home():
    return "Hello"


@app.post('/login/')
def login(username: Annotated[str, Form()],password: Annotated[str, Form()]):
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
    
def token_in_header(authorization:str = Header()):
    token_splitted = authorization.split(" ",1)
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