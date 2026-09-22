
import model
from model.email import EMAIL
from model.recipient import EMAIL_RECIPIENT

def save_email(db,sender,recipients,subject,body):

    try:
        email=EMAIL(sender=sender,subject=subject,body=body)

        db.add(email)
        db.flush()
        recip=[]
        for recipant in recipients:
            recip.append(EMAIL_RECIPIENT(email_id=email.id,recipient=recipant))

        db.add_all(recip)
        db.commit()

        print(f"email has been added to DB with id {email.id}")
    except Exception as e:
        db.rollback()
        print(f"Database error : {e}")


    finally:
        db.close()
