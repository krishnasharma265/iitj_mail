import sys,os
sys.path.append(os.path.join(os.path.dirname(__file__),".."))## if common is outside app then it contain two "..",".."

import socket
from common.database.database import SessionLocal
from common.model.users import USER
from common.model.mailbox import MAILBOX
from common.model.mailbox_message import MAILBOXMESSAGE
from common.model.email import EMAIL
import common.model




HOST="0.0.0.0"
PORT=143

def recieve_line(client):
    data=b""

    while not data.endswith(b"\r\n"):
        chunk=client.recv(1)

        if not chunk:
            return None
        data+=chunk
    return data.decode().strip()

def start_server():
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

    server.bind((HOST,PORT))
    server.listen(5)

    print(f"IMAP server is running on {HOST}:{PORT}")

    while True:
        client,address=server.accept()
        print(f"connection from {address}")

        client.sendall(b"* ok IITJ IMAP server ready\r\n")

        authenticated=False
        current_user=None
        selected_mailbox=None

        db=SessionLocal()

        while True:
            message=recieve_line(client)

            if message is None:
                break

            print("Client:",message)

            parts= message.split()

            if not parts:
                continue

            tag=parts[0]

            command=parts[1].upper() if len(parts)>1 else ""

            if command =="NOOP":
                client.sendall(f"{tag} ok NOOP completed\r\n".encode())

            elif command=="LOGIN":
                if len(parts)!=4:

                    client.sendall(f"{tag} Bad Login requires username and password \r\n".encode())
                    continue

                username=parts[2]
                password=parts[3]

                user=db.query(USER).filter(USER.email==username).first()

                if user is None:
                    client.sendall(
                        f"{tag} NO Authentication failed\r\n".encode()
                    )

                    continue

                ##temp pass checking
                if password!=user.password_hash:
                    client.sendall(
                        f"{tag} NO Authentication failed\r\n".encode()
                    )

                    continue

                authenticated=True
                current_user=user

                client.sendall(
                    f"{tag} OK LOGIN completed\r\n".encode()
                )

                print(f"User authenticated: {user.email}")

            elif command=="SELECT":
                if authenticated==False or current_user==None:
                    client.sendall(
                        f"{tag} NO Authenticate first\r\n".encode()
                    )

                    continue


                if len(parts) != 3 or parts[2].upper() != "INBOX":

                    client.sendall(
                        f"{tag} BAD Only SELECT INBOX is supported\r\n".encode()
                    )

                    continue

                mailbox=db.query(MAILBOX).filter(MAILBOX.user_id==current_user.id).first()

                if mailbox is None:
                    continue
                
                selected_mailbox=mailbox
                mailbox_message=db.query(MAILBOXMESSAGE).filter(MAILBOXMESSAGE.mailbox_id==selected_mailbox.id).all()

                total=len(mailbox_message)
                unseen=len([message for message in mailbox_message 
                             if message.is_read==False])

                client.sendall(f"total email : {total}\nunseen : {unseen}")
                client.sendall(
                    f"{tag} OK [READ-WRITE] SELECT completed\r\n".encode()
                )
                
            elif command=="FETCH":
                if authenticated==False or current_user==None:
                    client.sendall(
                        f"{tag} NO Authenticate first\r\n".encode()
                    )

                    continue

                if selected_mailbox is None:
                    client.sendall(f"{tag} No select mailbox first\r\n".encode())
                    continue

                if len(parts)<3:
                    client.sendall(f"{tag} Bad FETCH requires message number \r\n".encode())
                    continue

                try:
                    message_no=int(parts[2])

                except ValueError:
                    client.sendall(f"{tag} BAD Invalid message no\r\n".encode())

                    continue

                


                mailbox_messages=db.query(MAILBOXMESSAGE).filter(MAILBOXMESSAGE.mailbox_id==selected_mailbox.id).all()

                if message_no<1 or message_no>len(mailbox_messages):
                    client.sendall(b"no such message no exist\r\n")
                    continue
                
                mailbox_message=mailbox_messages[message_no-1]
                fetch_email=db.query(EMAIL).filter(EMAIL.id==mailbox_message.email_id).first()

                if fetch_email is None:
                    client.sendall(
                        f"{tag} NO Email not found\r\n".encode()
                    )

                    continue
                
                mailbox_message.is_read=True
                db.commit()

                response=(
                    f"* message no {message_no}  FETCH"
                    f"sender : {fetch_email.sender}"
                    f"subject : {fetch_email.subject}"
                    f"body : {fetch_email.body}\r\n"
                )

                client.sendall(response.encode())

                client.sendall(f"{tag} OK FETCHED \r\n".encode())


            elif command=="SEARCH":
                if authenticated==False or current_user==None:
                    client.sendall(
                        f"{tag} NO Authenticate first\r\n".encode()
                    )

                    continue

                if selected_mailbox is None:
                    client.sendall(f"{tag} No select mailbox first\r\n".encode())
                    continue

                if len(parts)<3:
                    client.sendall(f"{tag} Bad search requires object \r\n".encode())
                    continue
                
                mailbox_messages=db.query(MAILBOXMESSAGE).filter(MAILBOXMESSAGE.mailbox_id==selected_mailbox.id).all()
                
                                    

                if parts[2].upper()=="ALL":
                    
                    client.sendall(f"total messages {mailbox_messages}\r\n".encode())

                elif parts[2].upper()=="UNSEEN":
                    unseen=[message for message in mailbox_messages 
                                    if message.is_read==False]
                    client.sendall(f"total UNSEEEN messages {unseen}\r\n".encode())

                elif parts[2].upper()=="SEEN":
                    seen=[message for message in mailbox_messages 
                                    if message.is_read==True]
                    client.sendall(f"total SEEEN messages {seen}\r\n".encode())

                # elif parts[2]=="FROM":
                #     if len(parts)<4:
                #         client.sendall(f"{tag} Bad search requires email id\r\n".encode())
                #         continue
                    
                #     from_user=db.query(USER).filter(USER.email==(parts[4].lower())).first()

                #     if from_user is None:
                #         client.sendall(f"{tag} Bad search requires valid email id\r\n".encode())
                #         continue
                        
                #     emails=db.query(EMAIL).filter(EMAIL.user_id==from_user.id).all()
                    
                #     from_emails=[email.id for email in emails]

                else:

                    client.sendall(
                        f"{tag} BAD SEARCH criteria not supported\r\n".encode()
                    )

                    continue


            elif command=="DELETE":
                if authenticated==False or current_user==None:
                    client.sendall(
                        f"{tag} NO Authenticate first\r\n".encode()
                    )

                    continue

                if selected_mailbox is None:
                    client.sendall(f"{tag} No select mailbox first\r\n".encode())
                    continue
                
                
                if len(parts)<3 :
                    client.sendall(f"{tag} No give mail id first\r\n".encode())
                    continue

                try:
                    del_id=int(parts[2])
                except ValueError:
                    client.sendall(f"{tag} BAD Invalid message")
                    continue

                mailbox_message=db.query(MAILBOXMESSAGE).filter(MAILBOXMESSAGE.mailbox_id==selected_mailbox.id
                                                            ,MAILBOXMESSAGE.email_id==del_id).first()
                
                if mailbox_message is None:
                    client.sendall(f"{tag} No give a Valid mail id for delete\r\n".encode())
                    continue
                
                db.delete(mailbox_message)
                db.commit()
                        
            elif command == "STORE":

                if not authenticated or current_user is None:

                    client.sendall(
                        f"{tag} NO Authenticate first\r\n".encode()
                    )

                    continue

                if selected_mailbox is None:

                    client.sendall(
                        f"{tag} NO Select mailbox first\r\n".encode()
                    )

                    continue

                if len(parts) < 4:

                    client.sendall(
                        f"{tag} BAD STORE requires message number and flags\r\n".encode()
                    )

                    continue

                try:

                    message_no = int(parts[2])

                except ValueError:

                    client.sendall(
                        f"{tag} BAD Invalid message number\r\n".encode()
                    )

                    continue

                mailbox_messages = db.query(MAILBOXMESSAGE).filter(
                    MAILBOXMESSAGE.mailbox_id == selected_mailbox.id
                ).all()

                if message_no < 1 or message_no > len(mailbox_messages):

                    client.sendall(
                        f"{tag} NO Message does not exist\r\n".encode()
                    )

                    continue

                mailbox_message = mailbox_messages[message_no - 1]

                flag_operation = parts[3].upper()

                flag = parts[4].upper() if len(parts) > 4 else ""
                if flag not in ["(\\SEEN)", "(\\DELETED)"]:

                    client.sendall(
                        f"{tag} BAD Unsupported flag\r\n".encode()
                    )

                    continue

                if flag =="(\\SEEN)":
                    if flag_operation.startswith("+FLAGS"):

                        mailbox_message.is_read = True

                    elif flag_operation.startswith("-FLAGS"):

                        mailbox_message.is_read = False

                    else:

                        client.sendall(
                            f"{tag} BAD Unsupported STORE operation\r\n".encode()
                        )

                        continue

                elif flag=="(\\DELETED)":
                    if flag_operation.startswith("+FLAGS"):

                        mailbox_message.is_deleted = True

                    elif flag_operation.startswith("-FLAGS"):

                        mailbox_message.is_deleted = False
                    
                    else:

                        client.sendall(
                            f"{tag} BAD Unsupported STORE operation\r\n".encode()
                        )

                        continue

                # else:

                #     client.sendall(
                #         f"{tag} BAD Only \\\\Seen is currently supported\r\n".encode()
                #     )

                #     continue

                db.commit()

                flags=[]

                if mailbox_message.is_read==True:
                    flags.append("\\SEEN")

                if mailbox_message.is_deleted:
                    flags.append("\\DELETED")

                flag_string=" ".join(flags)

                client.sendall(
                    f"* {message_no} FETCH (FLAGS ({flag_string}))\r\n".encode()
                )

                client.sendall(
                    f"{tag} OK STORE completed\r\n".encode()
                )



            elif command == "EXPUNGE":

                if not authenticated or current_user is None:
                    client.sendall(
                        f"{tag} NO Authenticate first\r\n".encode()
                    )
                    continue

                if selected_mailbox is None:
                    client.sendall(
                        f"{tag} NO Select mailbox first\r\n".encode()
                    )
                    continue

                mailbox_messages = db.query(MAILBOXMESSAGE).filter(
                    MAILBOXMESSAGE.mailbox_id == selected_mailbox.id
                ).all()

                deleted_messages = []

                for sequence_number, mailbox_message in enumerate(
                    mailbox_messages,
                    start=1
                ):

                    if mailbox_message.is_deleted:

                        deleted_messages.append(
                            (sequence_number, mailbox_message)
                        )

                # Delete from database
                for sequence_number, mailbox_message in deleted_messages:

                    db.delete(mailbox_message)

                db.commit()

                # Inform client
                for sequence_number, mailbox_message in deleted_messages:

                    client.sendall(
                        f"* {sequence_number} EXPUNGE\r\n".encode()
                    )

                client.sendall(
                    f"{tag} OK EXPUNGE completed\r\n".encode()
                )


            elif command == "CLOSE":

                if not authenticated or current_user is None:

                    client.sendall(
                        f"{tag} NO Authenticate first\r\n".encode()
                    )

                    continue

                if selected_mailbox is None:

                    client.sendall(
                        f"{tag} NO Mailbox not selected\r\n".encode()
                    )

                    continue

                # Find messages marked as deleted
                deleted_messages = db.query(MAILBOXMESSAGE).filter(
                    MAILBOXMESSAGE.mailbox_id == selected_mailbox.id,
                    MAILBOXMESSAGE.is_deleted == True
                ).all()

                # Permanently delete them
                for mailbox_message in deleted_messages:

                    db.delete(mailbox_message)

                db.commit()

                # Deselect mailbox
                selected_mailbox = None

                client.sendall(
                    f"{tag} OK CLOSE completed\r\n".encode()
                )


            elif command =="LOGOUT":
                client.sendall(b"* BYE IITJ IMAP server logging out\r\n")

                client.sendall(f"{tag} OK LOGOUT completed\r\n".encode())

                break
            else:
                client.sendall(f"{tag} BAD command not implemented\r\n".encode())

        client.close()


if __name__=="__main__":
    start_server()