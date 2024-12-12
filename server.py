import asyncio
import logging
from typing import Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Available chat rooms (hard-coded)
available_rooms = ["General", "Python", "Linux & Open Source", "Off-Topic", "Help"]

# rooms: Dict[str, Dict[str, WebSocket]]
# rooms[room_name] = {username: websocket}
rooms: Dict[str, Dict[str, WebSocket]] = {room: {} for room in available_rooms}

# Global state
usernames = set()
user_rooms: Dict[str, str] = {}  # Maps username to the room they joined

# Locks to ensure thread-safe operations on shared data
usernames_lock = asyncio.Lock()
rooms_lock = asyncio.Lock()


class Message(BaseModel):
    sender: str
    content: str


async def assign_username(requested_username: str) -> str:
    """
    Assign a unique username. If the requested username is taken or empty,
    append a numeric counter until a unique username is found.
    """
    if not requested_username.strip():
        requested_username = "User"
    base = requested_username
    counter = 1
    async with usernames_lock:
        while requested_username in usernames:
            requested_username = f"{base}{counter}"
            counter += 1
        usernames.add(requested_username)
    return requested_username


async def broadcast(msg: Message, exclude: Optional[str] = None) -> None:
    """
    Broadcast a message to all connected clients in the same room as msg.sender,
    except 'exclude'.
    """
    sender_room = user_rooms.get(msg.sender)
    if not sender_room:
        return

    msg_str = f"[{msg.sender}]: {msg.content}"
    to_disconnect = []
    async with rooms_lock:
        room_clients = rooms.get(sender_room, {})
        for user, ws in room_clients.items():
            if user != exclude:
                try:
                    await ws.send_text(msg_str)
                except Exception as e:
                    logging.warning(
                        f"Failed to send to {user}: {e}. Marking for disconnection."
                    )
                    to_disconnect.append(user)

    for user in to_disconnect:
        await disconnect_user(user)


async def disconnect_user(username: str) -> None:
    """
    Disconnect a user from the chat:
    - Removes them from their room and from usernames.
    - Closes their WebSocket connection.
    - Broadcasts a leave message to others in the same room.
    """
    user_room = user_rooms.pop(username, None)
    ws = None
    async with rooms_lock:
        if user_room and user_room in rooms:
            ws = rooms[user_room].pop(username, None)

    async with usernames_lock:
        usernames.discard(username)

    if ws:
        try:
            await ws.close()
        except Exception:
            logging.debug(f"Error closing connection for {username}, ignoring.")

    if user_room:
        await broadcast(
            Message(sender="SERVER", content=f"{username} has left the chat.")
        )


async def send_room_list(ws: WebSocket) -> None:
    """
    Sends the list of available rooms to the client.
    """
    room_list = "Available rooms:\n"
    for i, r in enumerate(available_rooms, start=1):
        room_list += f"{i}. {r}\n"
    room_list += "Enter the number of the room you want to join:"
    await ws.send_text(room_list)


app = FastAPI()


@app.get("/")
async def read_root() -> dict:
    """
    A simple endpoint to confirm server health and list online users.
    """
    async with usernames_lock:
        current_users: List[str] = list(usernames)
    return {"status": "ok", "users_online": current_users}


@app.websocket("/chat")
async def websocket_endpoint(ws: WebSocket):
    # Accept the WebSocket connection
    await ws.accept()

    username = "Unknown"
    try:
        # Step 1: Ask for desired username
        await ws.send_text("Enter your desired username:")
        requested_username = await ws.receive_text()
        username = await assign_username(requested_username)
        await ws.send_text(f"Your username is: {username}")

        # Step 2: Send room list
        await send_room_list(ws)

        # Step 3: Receive chosen room
        chosen_str = await ws.receive_text()
        try:
            chosen_index = int(chosen_str.strip()) - 1
            if chosen_index < 0 or chosen_index >= len(available_rooms):
                chosen_room = "General"
                await ws.send_text("Invalid choice, defaulting to 'General'.")
            else:
                chosen_room = available_rooms[chosen_index]
        except ValueError:
            chosen_room = "General"
            await ws.send_text("Invalid choice, defaulting to 'General'.")

        # Step 4: Add the client to the chosen room
        async with rooms_lock:
            rooms[chosen_room][username] = ws
        user_rooms[username] = chosen_room

        # Step 5: Broadcast join message
        await broadcast(
            Message(sender="SERVER", content=f"{username} has joined {chosen_room}."),
            exclude=username,
        )

        logging.info(f"{username} connected and joined room: {chosen_room}")

        # Step 6: Message loop
        while True:
            try:
                data = await ws.receive_text()
            except WebSocketDisconnect:
                logging.info(f"{username} disconnected.")
                break

            msg_text = data.strip()
            if msg_text.lower() == "/quit":
                logging.info(f"{username} requested to quit.")
                break

            if msg_text:
                await broadcast(
                    Message(sender=username, content=msg_text), exclude=username
                )
    except WebSocketDisconnect:
        logging.info(f"Connection lost with {username}.")
    except Exception as e:
        logging.error(f"Error handling client {username}: {e}")
    finally:
        await disconnect_user(username)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, log_level="info")
