from fastapi import APIRouter,HTTPException,Depends
from sqlalchemy.orm import Session
from database.connection import get_db
from services.auth import get_current_user,hash_password
from schema.user import UserUpdate,USEROUT
from model.users import USER
from model.mailbox import MAILBOX
from schema.response import APIResponse
from model.mailbox_message import MAILBOXMESSAGE
from schema.mailbox_message import CREATEMAILBOX,UPDATEMAILBOX,MAILBOXOUT
from typing import List
from schema.mailbox_message import CREATEMAILBOX_MESSAGE,UPDATEMESSAGE,MESSAGEOUT






router=APIRouter()


## USER POINTS
###########################
@router.get("/user/me",response_model=USEROUT)
def current_user(user=Depends(get_current_user)):
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
    


    db.delete(user)
    db.commit()

    return APIResponse(
        success=True,
        message="profile deleted successfully",
        
    )

######################


## MAILBOXES(INBOX,SENT,DRAFTS,TRASH,SPAM,CUSTOM)
############################################################################
@router.get("/mailboxes",response_model=List[MAILBOXOUT])
def get_mailboxes(db:Session=Depends(get_db),user=Depends(get_current_user)):

    user_mailboxes=db.query(MAILBOX).filter(MAILBOX.user_id==user.id).all()

    return user_mailboxes

@router.post("/mailboxes")
def create_mailbox(mailbox_data:CREATEMAILBOX,db:Session=Depends(get_db),user=Depends(get_current_user)):

    mailbox=MAILBOX(user.id=mailbox_data.user_id,
                    name=mailbox_data.name)

    PROTECTED = {"inbox", "sent", "drafts", "trash", "spam"}

    if mailbox.name.lower() in PROTECTED:
        raise HTTPException(status_code=400, detail="System mailbox cannot be recreated")
    

    db.add(mailbox)
    db.commit()
    db.refresh(mailbox)

    return APIResponse(
        success=True,
        message="mailbox created successfully"
    )

@router.get("/mailboxes/{mailbox_id}",response_model=MAILBOXOUT)
def get_one_mailbox(mailbox_id:int,db:Session=Depends(get_db),user=Depends(get_current_user)):
    mailbox=db.query(MAILBOX).filter(MAILBOX.id==mailbox_id,
                                        MAILBOX.user_id==user.id).first()

    if not mailbox:
        raise HTTPException(status_code=404,detail="mailbox not found")

    return mailbox

@router.patch("/mailboxes/{mailbox_id}/rename", response_model=MAILBOXOUT)
def rename_mailbox(mailbox_id:int,mailbox_data:UPDATEMAILBOX,db:Session=Depends(get_db),user=Depends(get_current_user)):
    mailbox=db.query(MAILBOX).filter(MAILBOX.id==mailbox_id,MAILBOX.user_id==user.id).first()


    PROTECTED = {"inbox", "sent", "drafts", "trash", "spam"}

    if mailbox.name.lower() in PROTECTED:
        raise HTTPException(status_code=400, detail="System mailbox cannot be renamed")
    
    if not mailbox:
        raise HTTPException(status_code=404,detail="mailbox not found")

    update_mailbox=mailbox_data.model_dump(exclude_unset=True)
    if "name" not in update_mailbox:
        raise HTTPException(status_code=422,detail="write name first")

    for key ,value in update_mailbox.items():

        setattr(mailbox,key,value)

    db.commit()
    db.refresh(mailbox)
    return mailbox  

    return APIResponse(
        success=True,
        message=f"{mailbox.name} rename successfully"
        
    )

@router.delete("/mailboxes/{mailbox_id}")
def delete_mailbox(mailbox_id:int,db:Session=Depends(get_db),user=Depends(get_current_user)):
    mailbox=db.query(MAILBOX).filter(MAILBOX.id==mailbox_id,MAILBOX.user_id==user.id).first()

    PROTECTED = {"inbox", "sent", "drafts", "trash", "spam"}

    if mailbox.name.lower() in PROTECTED:
        raise HTTPException(status_code=400, detail="System mailbox cannot be deleted")
    
    if not mailbox:
        raise HTTPException(status_code=404,detail="mailbox not found")

    db.delete(mailbox)
    db.commit()

    return APIResponse(
        success=True,
        message="mailbox deleted successfully"
        
    )


#########################

## MAILBOX _ MESSAGES 
###################################################

@router.get("/mailbox/{mailbox_id}/messages",response_model=List(MESSAGEOUT))
def get_messages(mailbox_id:int,db:Session=Depends(get_db),user=Depends(get_current_user)):
    mailbox=db.query(MAILBOX).filter(MAILBOX.id==mailbox_id).first()
    if not mailbox:
        raise HTTPException(status_code=404,detail="mailbox not found")

    if mailbox.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )
    messages=db.query(MAILBOXMESSAGE).filter(MAILBOXMESSAGE.mailbox_id==mailbox_id).all()

    return messages

@router.get("/mailbox/{mailbox_id}/{message_id}",response_model=MESSAGEOUT)
def get_messages(mailbox_id:int,message_id:int,db:Session=Depends(get_db),user=Depends(get_current_user)):
    mailbox=db.query(MAILBOX).filter(MAILBOX.id==mailbox_id).first()
    if not mailbox:
        raise HTTPException(status_code=404,detail="mailbox not found")

    if mailbox.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )
    message=db.query(MAILBOXMESSAGE).filter(MAILBOXMESSAGE.mailbox_id==mailbox_id,MAILBOXMESSAGE.id==message_id).first()

    if not message:
        raise HTTPException(status_code=404,detail="message not found")

    return message

@router.delete("/mailbox/{mailbox_id}/{message_id}")
def delete_message(mailbox_id:int,message_id:int,db:Session=Depends(get_db),user=Depends(get_current_user)):
    mailbox=db.query(MAILBOX).filter(MAILBOX.id==mailbox_id).first()
    if not mailbox:
        raise HTTPException(status_code=404,detail="mailbox not found")

    if mailbox.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )
    message=db.query(MAILBOXMESSAGE).filter(MAILBOXMESSAGE.mailbox_id==mailbox_id,MAILBOXMESSAGE.id==message_id).first()

    if not message:
        raise HTTPException(status_code=404,detail="message not found")

    db.delete(message)
    db.commit()

    return APIResponse(
        success=True,
        message=f"{message_id} has been deleted"
    )

    
@router.post("/mailbox/{mailbox_id_old}/{message_id}/{mailbox_id_new}")
def move_message(mailbox_id_old:int,mailbox_id_new:int,message_id:int,db:Session=Depends(get_db),user=Depends(get_current_user)):

    mailbox_old=db.query(MAILBOX).filter(MAILBOX.id==mailbox_id_old).first()
    if not mailbox_old:
        raise HTTPException(status_code=404,detail="mailbox not found")
    
    mailbox_new=db.query(MAILBOX).filter(MAILBOX.id==mailbox_id_new).first()
    if not mailbox_new:
        raise HTTPException(status_code=404,detail="mailbox not found")

    if mailbox_old.user_id != user.id or mailbox_new.user_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    message=db.query(MAILBOXMESSAGE).filter(MAILBOXMESSAGE.mailbox_id==mailbox_id_old,MAILBOXMESSAGE.id==message_id).first()
    if not message:
        raise HTTPException(status_code=404,detail="message not found")

    message.mailbox_id=mailbox_id_new

    db.commit()

    return APIResponse(
        success=True,
        message=f"{message_id} moves from {mailbox_old} to {mailbox_new}"
    )

    
    






