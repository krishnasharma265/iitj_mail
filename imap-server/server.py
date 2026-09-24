import socket


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

            elif command =="LOGOUT":
                client.sendall(b"* BYE IITJ IMAP server logging out\r\n")

                client.sendall(f"{tag} OK LOGOUT completed\r\n".encode())

                break
            else:
                client.sendall(f"{tag} BAD command not implemented\r\n".encode())

        client.close()


if __name__=="__main__":
    start_server()