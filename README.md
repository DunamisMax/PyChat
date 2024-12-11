# PyChat

A simple, terminal-based chat application featuring a TCP chat server and a FastAPI endpoint for monitoring connected users. This project allows multiple users to connect to a central server and exchange messages in real-time, and also provides a convenient HTTP endpoint for listing currently active participants.

**Author:** [dunamismax](https://github.com/dunamismax)  
**Socials:** [BlueSky](https://bsky.app/profile/dunamismax.bsky.social), [Reddit](https://www.reddit.com/user/dunamismax)

This project was created with the assistance of GPT in o1-pro mode.

## Features

- **Real-Time Chat:** Multiple clients can connect and exchange messages.
- **TCP-Based:** Utilizes a raw TCP socket server for chat, ensuring fast, direct communication.
- **User Management:** Automatic assignment of unique usernames, even if collisions occur.
- **HTTP Endpoint:** A FastAPI endpoint to list online users, ensuring easy integration with other services or dashboards.
- **Graceful Shutdowns:** Users can quit with `/quit` and the server will cleanly remove them.

## Quick Start

### Prerequisites

- **Python 3.9+** recommended
- **Virtual Environment (venv)** for clean dependency management
- **pip** for installing dependencies

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/dunamismax/pychat.git
   cd pychat
   ```

2. **Set up a virtual environment and install dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

### Running the Server

Start the server with:
```bash
python server.py
```
- The TCP chat server will run on `0.0.0.0:42069`.
- The FastAPI application will be available at `http://0.0.0.0:8000`.

### Connecting with a Client

Run the client script in another terminal or machine:
```bash
python client.py
```
- Enter the server IP when prompted (e.g., `127.0.0.1` if running locally).
- Choose a username (the server may adjust it if it’s already taken).
- Type messages and press Enter to send.
- Type `/quit` to leave the chat.

### Listing Online Users

Use a simple `curl` request or a browser to list currently online users:
```bash
curl http://0.0.0.0:8000/
```
This returns JSON with a list of active users.

## Code Structure

- **server.py:**  
  Sets up both the TCP chat server and the FastAPI application. Manages user connections, broadcasts messages, and exposes an HTTP endpoint for listing users.
  
- **client.py:**  
  A command-line client for interacting with the chat server. Handles sending messages, receiving broadcasts, and gracefully disconnecting.

## Troubleshooting

- **Address Already in Use:**  
  Ensure no other processes are running on the same ports or choose different ports in `server.py`.
  
- **Connection Issues:**  
  Verify that the server is running and reachable at the specified IP and port.
  
- **Unexpected Errors:**  
  Check the console logs for detailed error messages. Both server and client scripts use logging to provide insights into what went wrong.

## License

This project is provided as-is under an unlicensed, free-to-use model. Check the repository for any specific licensing details.

---

Created and maintained by [dunamismax](https://github.com/dunamismax), with the assistance of GPT in o1-pro mode.
