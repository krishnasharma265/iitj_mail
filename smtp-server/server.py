import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import socket
from common.database.connection import db_init,get_db
# from sqlalchemy.orm import Session
# from fastapi import Depends
from common.database.database import SessionLocal
from common.services.email_services import save_email
import common.model






HOST="0.0.0.0"
PORT=2525

def recieve_line(client):
    data=b""

    while not data.endswith(b"\r\n"):
        chunk=client.recv(1)

        if not chunk:
            return None
        
        data+= chunk

    return data.decode().strip()

def parse_mail_data(mail_data):
    "convert raw data into subject and body"


    mail_data=mail_data.replace("\r\n.\r\n","")
    mail_data=mail_data.replace("\r\n","\n")

    lines=mail_data.split("\n")

    subject=""

    body_lines=[]

    in_body=False

    for line in lines:
        if not in_body:
            if line.lower().startswith("subject:"):
                subject=line[len("subject:"):].strip()

            elif line =="":
                in_body=True

        else:
            body_lines.append(line)


    body="\n".join(body_lines)

    return subject,body


def extract_email(command,keyword):
    command_upper=command.upper()

    if not command_upper.startswith(keyword):
        return None

    value=command[len(keyword):].strip()

    if not value.startswith("<") or not value.endswith(">"):
        return None

    email=value[1:-1].strip()

    if "@" not in email:
        return None
    
    return email



def start_server():
    # local database connection setup
    db=SessionLocal()


    server= socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    server.setsockopt(socket.SOL_SOCKET , socket.SO_REUSEADDR, 1)

    server.bind((HOST,PORT))
    server.listen(5)

    print(f"SMTP server running on {HOST}:{PORT}")

    while True:
        client, address= server.accept()
        print(f"connection from {address}")

        client.sendall(b"220 mySMTP server Ready\r\n")

        greeted=False
        sender=None
        recipients=[]

        while True:
            message=recieve_line(client)
            

            if message is None:
                break

            
            print("Client:",message)

            if message.upper().startswith("EHLO"):

                greeted=True

                client.sendall(
                    b"250-mySMTP\r\n"
                    b"250 ok\r\n"
                )

            elif message.upper().startswith("HELO"):

                greeted=True

                client.sendall(
                    b"250 Hello\r\n"
                )

                ##mail from 
            elif message.upper().startswith("MAIL FROM"):

                if not greeted:
                    client.sendall(
                        b"503 send EHLO/HELO first ok \r\n"

                    )
                    continue
                    
                email=extract_email(message,"MAIL FROM:")

                if email is None:
                    client.sendall(
                        b"501 Invalid MAIL FROM\r\n"
                    )
                    continue
                sender=email

                client.sendall(
                        b"250 sender ok \r\n"

                    )

            ## RCPT TO
            elif message.upper().startswith("RCPT TO"):

                if sender is None:
                    client.sendall(
                        b"503 need mail from frist\r\n"
                    )
                    continue


                email=extract_email(message,"RCPT TO:")

                if email is None:
                    client.sendall(
                        b"501 Invalid RCPT TO\r\n"
                    )
                    continue
                recipients.append(email)
                client.sendall(
                        b"250 recipant ok\r\n"
                    )

            ## DATA
            elif message.upper()=="DATA":

                if sender is None:
                    client.sendall(
                        b"503 Need MAIL FROM first\r\n"
                    )
                    continue
                if recipients is None:
                    client.sendall(
                        b"503 Need RCPT TO first\r\n"
                    )
                    continue

                client.sendall(
                    b"354 start mail input ; end with <CRLF>.<CRLF>\r\n"
                )
            
                mail_data=b""

                while True:
                    chunk = client.recv(1024)

                    if not chunk:
                        break

                    mail_data +=chunk

                    if b"\r\n.\r\n" in mail_data:
                        break
                

                ## convert bytes to string
                mail_text=mail_data.decode(errors="replace")

                subject,body=parse_mail_data(mail_text)

                print("MAIL recieved ")
                print("Sender",sender)
                print("Recipient",recipients)
                print("subject:  ",subject)
                print("body:  ",body)

                save_email(db,sender,recipients,subject,body)
                # print(mail_data.decode(errors="replace"))

                client.sendall(
                    b"250 Message accepted\r\n"
                )

                ## reset transaction
                sender=None
                recipients=[]

            elif message.upper() == "QUIT":
                client.sendall(
                    b"221 Bye\r\n"
                )
                break

            else:
                client.sendall(
                    b"502 command not implemented\r\n"
                )
        client.close()


if __name__ == "__main__":
    for attempt in range(10):
        try:
            db_init()
            break
        except OperationalError:
            print(f"DB not ready, retrying ({attempt+1}/10)...")
            time.sleep(3)
    else:
        raise RuntimeError("Could not connect to database after retries")
    
    start_server()



