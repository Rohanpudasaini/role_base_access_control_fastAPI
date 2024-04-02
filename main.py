from typing import Annotated
from fastapi import Depends, FastAPI, Form, HTTPException, Header
from auth import auth
from models import User, Role
from sqlalchemy import Select
from database_connection import session

app = FastAPI(title="RBAC")


def token_in_header(Authorization:str = Header()):
    token_splitted = Authorization.split(" ",1)
    if token_splitted[0].lower() =='bearer':
        return auth.decodAccessJWT(token_splitted[1])

    else:
        raise HTTPException(
            status_code=401,
            detail= "Invalid token Scheme"
        )
    
    

@app.get('/', dependencies=[Depends(token_in_header)])
def home():
    return "Hello"


@app.post('/login/')
def login(username: str = Form() ,password: str= Form()):
    user = session.execute(Select(User.username, User.role_id, User.password).where(User.username==username)).first()
    if user:
        access_token,refresh_token = auth.generate_JWT(user[0], user[1])
        valid_password = auth.verify_password(password,user[2])
        if valid_password:
            return {
                "Sucess":"Login Sucesfull",
                "Tokens":{
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    'role_id': user[1]
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
    

# def is_allowed(payload =Depends(token_in_header)):
#     if payload['role'] == 'admin':
#         return 'Hello'
#     raise HTTPException(
#         status_code=401,
#         detail={
#             'error': "UNAUTHORIZED",
#             'message': "You don't have access to view this endpoint"
#         }
#     )
def get_role_permissions(role_id):
    return session.scalars(Select(Role.permission).where(Role.id==role_id)).first()


class PermissionChecker:
    def __init__(self, permissions_required: list):
        self.permissions_required = permissions_required

    def __call__(self, user:dict = Depends(token_in_header)):
        print(user)
        for permission_required in self.permissions_required:
            if permission_required not in get_role_permissions(user['role']):
                raise HTTPException(
                    status_code=403,
                    detail="Not enough permissions to access this resource")
        return user



@app.get('/test_user', dependencies=[Depends(PermissionChecker(['user:all']))])
def test():
    return "Welcome User"

@app.get('/test_admin', dependencies=[Depends(PermissionChecker(['admin:all']))])
def test():
    return "Welcome Admin"