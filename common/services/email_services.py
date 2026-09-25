
import common.model
from common.model.email import EMAIL
from common.model.recipient import EMAIL_RECIPIENT
from common.model.users import USER
from common.model.mailbox import MAILBOX
from common.model.mailbox_message import MAILBOXMESSAGE



def save_email(db,sender,recipients,subject,body):

    try:
        email=EMAIL(sender=sender,subject=subject,body=body)

        db.add(email)
        db.flush()
        # recip=[]
        for recipant in recipients:
            email_recipant=EMAIL_RECIPIENT(email_id=email.id,
                    recipient=recipant)
            db.add(email_recipant)

            user=db.query(USER).filter(USER.email==recipant).first()

            if user is None:
                print(f"User not found : {recipant}")
                continue

            mailbox=db.query(MAILBOX).filter(MAILBOX.user_id==user.id,
                                                MAILBOX.name=="INBOX").first()

            if mailbox is None:
                print(f"INBOX not found for  {recipant}")
                continue

            mailbox_message=MAILBOXMESSAGE(mailbox_id=mailbox.id,
                                            email_id=email.id,
                                            is_read=False)

            db.add(mailbox_message)

        # db.add_all(recip)
        db.commit()

        print(f"email has been added to DB with id {email.id}")
    except Exception as e:
        db.rollback()
        print(f"Database error : {e}")


    finally:
        db.close()
