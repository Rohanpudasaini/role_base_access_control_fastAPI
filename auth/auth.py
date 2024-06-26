import datetime
import time
import bcrypt
from fastapi import HTTPException
from jose import jwt, JWTError
from passlib.context import CryptContext
from decouple import config


pwd_context = CryptContext(schemes=['bcrypt'],deprecated='auto')

ACCESS_SECRET = config('secret_access')
REFRESH_SECRET = config('secret_refresh')
# EXPIRE = config('expire_time')
ALGORITHM = config('algorithm')
ACCESS_EXPIRE_TIME = int(config('access_expire_time'))
REFRESH_EXPIRE_TIME = int(config('refresh_expire_time'))

def generate_JWT(username:str,role:str):
    payload = {
        'user_id':username, 
        'role': role,
        # 'expiry': (datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=ACCESS_EXPIRE_TIME)).date(),
        'expiry': time.time() + 1200
        }
    encoded_access = jwt.encode(payload,ACCESS_SECRET,algorithm=ALGORITHM)
    payload = {
        'user_id':username, 
        'role': role,
        # 'expiry': datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=REFRESH_EXPIRE_TIME)
        'expiry': time.time() + 604800
        }
    encoded_refresh = jwt.encode(payload,REFRESH_SECRET,ALGORITHM)
    return encoded_access, encoded_refresh

def decodAccessJWT(token:str):
    try:
        decode_token = jwt.decode(token,ACCESS_SECRET,ALGORITHM)
        # return decode_token if decode_token['expiry'] >= time.time() else None
        if decode_token['expiry'] >= time.time():
            return decode_token
        else:
            raise HTTPException(
                status_code=401,
                detail="Expired Token"
            )   
            
    except JWTError:
        raise HTTPException(
                    status_code=401,
                    detail="Token Verification failed"
                )    
        
def decodRefreshJWT(token:str):
    try:
        decode_token = jwt.decode(token,REFRESH_SECRET,ALGORITHM)
        # return decode_token if decode_token['expiry'] >= time.time() else None
        if decode_token['expiry'] >= time.time():
            return decode_token
        else:
            raise HTTPException(
                status_code=401,
                detail="Expired Token"
            )   
            
    except JWTError:
        raise HTTPException(
                    status_code=401,
                    detail="Token Verification failed"
                )    

# def hash_password(password:str):
#     return pwd_context.hash(password)

# def verify_password(plain_password, hash_password):
#     return pwd_context.verify(plain_password, hash_password)
    
# Hash a password using bcrypt
def hash_password(password):
    pwd_bytes = password.encode('UTF-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password

# Check if the provided password matches the stored password (hashed)
def verify_password(plain_password:str, hashed_password):
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_byte_enc , hashed_password)