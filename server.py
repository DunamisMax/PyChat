import socket
import threading
import logging
import time
from typing import Dict, List, Tuple, Optional
import asyncio
from contextlib import asynccontextmanager

from pydantic import BaseModel
from fastapi import FastAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Global in-memory state
clients: Dict[str, socket.socket] = {}
usernames = set()

# Locks to ensure thread-safe operations on shared data
clients_lock = threading.Lock()
usernames_lock = threading.Lock()


class Message(BaseModel):
    sender: str
    content: str


# TCP Chat Server Configuration
HOST = "0.0.0.0"
PORT = 42069


def assign_username(requested_username: str) -> str:
    """
    Assign a unique username. If the requested username is taken or empty,
    append a numeric counter until a unique username is found.
    """
    if not requested_username.strip():
        requested_username = "User"
    base = requested_username
    counter = 1
    with usernames_lock:
        while requested_username in usernames:
            requested_username = f"{base}{counter}"
            counter += 1
        usernames.add(requested_username)
    return requested_username


def broadcast(msg: Message, exclude: Optional[str] = None) -> None:
    """
    Broadcast a message to all connected clients except 'exclude'.
    If a client fails to receive, that client is disconnected.
    """
    msg_str = f"[{msg.sender}]: {msg.content}\n"
    to_disconnect = []
    with clients_lock:
        for user, conn in clients.items():
            if user != exclude:
                try:
                    conn.sendall(msg_str.encode())
                except Exception as e:
                    logging.warning(
                        f"Failed to send to {user}: {e}. Marking for disconnection."
                    )
                    to_disconnect.append(user)

    # Disconnect any clients that failed to receive
    for user in to_disconnect:
        disconnect_user(user)


def disconnect_user(username: str) -> None:
    """
    Disconnect a user from the chat:
    - Removes them from the clients and usernames sets.
    - Closes their socket connection.
    - Broadcasts a leave message to others.
    """
    conn = None
    with clients_lock:
        conn = clients.pop(username, None)
    with usernames_lock:
        usernames.discard(username)

    if conn:
        try:
            conn.close()
        except Exception:
            logging.debug(f"Error closing connection for {username}, ignoring.")

    broadcast(Message(sender="SERVER", content=f"{username} has left the chat."))


def handle_client(conn: socket.socket, addr: Tuple[str, int]) -> None:
    """
    Handle an individual client connection:
    1. Receive the desired username from the client.
    2. Assign a unique username and notify the client.
    3. Add the client to the global clients list.
    4. Broadcast a join message.
    5. Loop: Read messages from this client and broadcast them.
    """
    username = "Unknown"
    try:
        # Step 1: Get requested username from the client
        data = conn.recv(1024)
        if not data:
            logging.info(f"Connection closed before username was received from {addr}.")
            conn.close()
            return

        requested_username = data.decode().strip()
        username = assign_username(requested_username)

        # Step 2: Notify client of assigned username
        conn.sendall(f"Your username is: {username}\n".encode())

        # Step 3: Add client to global dictionary
        with clients_lock:
            clients[username] = conn

        # Step 4: Broadcast join message
        broadcast(
            Message(sender="SERVER", content=f"{username} has joined the chat."),
            exclude=username,
        )

        logging.info(f"{username} connected from {addr}")

        # Step 5: Message loop
        while True:
            data = conn.recv(1024)
            if not data:
                logging.info(f"{username} disconnected.")
                break
            msg_text = data.decode().strip()

            if msg_text.lower() == "/quit":
                logging.info(f"{username} requested to quit.")
                break

            if msg_text:  # Only broadcast if there's content
                broadcast(Message(sender=username, content=msg_text), exclude=username)
    except ConnectionResetError:
        logging.info(f"Connection reset by client {username} at {addr}.")
    except Exception as e:
        logging.error(f"Error handling client {username} at {addr}: {e}")
    finally:
        disconnect_user(username)


def start_tcp_server() -> None:
    """
    Start the TCP server that accepts new client connections.
    Spins up a new thread (daemon) for each client.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    logging.info(f"Chat server listening on {HOST}:{PORT}...")

    while True:
        conn, addr = s.accept()
        logging.info(f"Incoming connection from {addr}")
        client_thread = threading.Thread(
            target=handle_client, args=(conn, addr), daemon=True
        )
        client_thread.start()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the TCP server in a separate thread
    threading.Thread(target=start_tcp_server, daemon=True).start()

    # Give the server a moment to start
    await asyncio.sleep(0.5)

    logging.info("FastAPI application startup complete.")
    yield
    # No special teardown logic is required here.


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root() -> dict:
    """
    A simple endpoint to confirm server health and list online users.
    """
    with usernames_lock:
        current_users: List[str] = list(usernames)
    return {"status": "ok", "users_online": current_users}


if __name__ == "__main__":
    import uvicorn

    # Start the FastAPI application with Uvicorn.
    # The TCP server is already started by the lifespan function.
    uvicorn.run("server:app", host="0.0.0.0", port=8000, log_level="info")
