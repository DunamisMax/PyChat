# PyChat

A simple terminal-based chat application that supports multiple themed chat rooms. This project enables multiple users to connect to a central TCP server, select a room by number, and exchange messages in real-time. A FastAPI endpoint provides a view into the currently online users.

**Key Features:**

- **Multiple Chat Rooms:** Users can choose from a set of predefined rooms to join and chat in.
- **Real-Time Communication:** Messages sent by one user in a room are broadcasted to all other users in that room.
- **HTTP Endpoint for Monitoring:** A FastAPI endpoint lists all online users, allowing quick checks of the server’s status.

**Usage:**

1. Start the server:

   ```bash
   python server.py
   ```

   The server starts the TCP chat on `0.0.0.0:42069` and the FastAPI interface on `http://0.0.0.0:8000`.

2. Connect with a client:

   ```bash
   python client.py
   ```

   Enter the server’s IP, your desired username, and select a room by number.

**Commands:**

- **/quit**: Leave the chat room and disconnect.

This project was created with the assistance of GPT in o1-pro mode.
