from fastapi import APIRouter,HTTPException,Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from services.auth import get_current_user,hash_password
from schema.user import UserUpdate
from model.users import USER
from model.mailbox import MAILBOX
from schema.response import APIResponse
from model.mailbox_message import MAILBOXMESSAGE
from schema.mailbox import CREATEMAILBOX,UPDATEMAILBOX
router=APIRouter()


## USER POINTS
###########################
@router.get("/user/me")
def current_user(db:Session=Depends(get_db),user=Depends(get_current_user)):
    return user


@router.patch("/user/me")
def change_credentials(update_credentials:UserUpdate,db:Session=Depends(get_db),user=Depends(get_current_user)):
    update_data=update_credentials.model_dump(exclude_unset=True)

    if "password" in update_data:
        update_data["password"]=hash_password(update_data["password"])

    for key,value in update_data.items():
        setattr(user,key,value)

    db.commit()
    db.refresh(user)

    return APIResponse(
        success=True,
        message="user credentials updated successfully"
    )

@router.delete("/user/me")
def delete_user(db:Session=Depends(get_db),user=Depends(get_current_user)):
    dlt_user=db.get(USER,user.id)


    if not dlt_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(dlt_user)
    db.commit()

    return APIResponse(
        success=True,
        message="profile deleted successfully",
        
    )

######################


## MAILBOXES(INBOX,SENT,DRAFTS,TRASH,SPAM,CUSTOM)
############################################################################
@router.get("/mailboxes")
def get_mailboxes(db:Session=Depends(get_db),user=Depends(get_current_user)):

    user_mailboxes=db.query(MAILBOX).filter(MAILBOX.user_id==user.id).all()

    return user_mailboxes

@router.post("/mailboxes")
def create_mailbox(mailbox_data:CREATEMAILBOX,db:Session=Depends(get_db),user=Depends(get_current_user)):

    mailbox=MAILBOX(user_id=mailbox_data.user_id,
                    name=mailbox_data.name)


    db.add(mailbox)
    db.commit()
    db.refresh(mailbox)

    return APIResponse(
        success=True,
        message="user credentials updated successfully"
    )

@router.get("/mailboxes/{mailbox_id}")
def get_one_mailbox(mailbox_id:int,db:Session=Depends(get_db),user=Depends(get_current_user)):
    mailbox=db.query(MAILBOX).filter(MAILBOX.id==mailbox_id,
                                        MAILBOX.user_id==user.id).first()

    if not mailbox:
        raise HTTPException(status_code=401,detail="mailbox not found")

    return mailbox

@router.patch("/mailboxes/{mailbox_id}/rename")
def rename_mailbox(mailbox_id:int,mailbox_data:UPDATEMAILBOX,db:Session=Depends(get_db),user=Depends(get_current_user)):
    mailbox=db.query(MAILBOX).filter(MAILBOX.id==mailbox_id,MAILBOX.user_id==user.id).first()

    if not mailbox:
        raise HTTPException(status_code=401,detail="mailbox not found")

    update_mailbox=mailbox_data.model_dump(exclude_unset=True)
    if "name" not in update_mailbox:
        raise HTTPException(status_code=444,detail="write name first")

    for key ,value in update_mailbox.items():

        setattr(mailbox,key,value)

    db.commit()
    db.refresh(mailbox)
    return APIResponse(
        success=True,
        message=f"{mailbox.name} rename successfully"
        
    )

@router.delete("/mailboxes/{mailbox_id}")
def delete_mailbox(mailbox_id:int,db:Session=Depends(get_db),user=Depends(get_current_user)):
    mailbox=db.query(MAILBOX).filter(MAILBOX.id==mailbox_id,MAILBOX.user_id==user.id).first()

    if not mailbox:
        raise HTTPException(status_code=401,detail="mailbox not found")

    db.delete(mailbox)
    db.commit()

    return APIResponse(
        success=True,
        message="profile deleted successfully",
        
    )





