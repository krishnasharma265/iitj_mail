from fastapi import APIRouter,Depends,HTTPException,Request
from sqlalchemy.orm import Session
from schema.user import CreateUser,LoginUser
from database.connection import get_db
from models.user import USER
from datetime import date
from services.auth import hash_password,verify_password
from schema.response import APIResponse
from schema.token_response import Token_Response


router=APIRouter(prefix="/auth",tags=["Auth"])

@router.post("/signup")
def signup(request:Request,user:CreateUser,db:Session=Depends(get_db)):
    existing=db.query(USER).filter(USER.email==user.email).first()

    if existing:
        raise HTTPException(status_code=400,detail="User already exists")

    new_user=USER(
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return APIResponse(
        success=True,
        message="user created"
    )

@router.post("/login")
def login(request:Request,user:LoginUser,db:Session=Depends(get_db)):
    exist_user=db.query(USER).filter(USER.email==user.email).first()

    if not exist_user :
        raise HTTPException(status_code=401,detail="INVALID CREDENTIAL")

    elif not verify_password(user.password,exist_user.password):
        raise HTTPException(status_code=401,detail="INVALID CREDENTIAL")    

    token=create_token({"sub":exist_user.email})

    return Token_Response(
        access_token=token.get("access_token"),
        refresh_token=token.get("refresh_token")
        token_type=token.get("token_type")
    )
