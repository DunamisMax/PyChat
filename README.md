# PyChat

PyChat is a simple, terminal-based chat application built with Python and FastAPI. It uses WebSockets for real-time messaging and supports multiple chat rooms, user authentication (via assigned nicknames), and a clean, minimal interface. PyChat is easy to deploy behind an Nginx reverse proxy, allowing you to host a web-accessible chat alongside other services such as WebDAV or a static website.

## Features

- **Real-Time Messaging:** Chat with others in real-time using WebSockets.
- **Multiple Rooms:** Choose from a predefined set of rooms to join and interact with different groups of users.
- **User Nicknames:** Pick a desired username. If it’s taken, PyChat will assign a unique variant.
- **Easy Integration:** Runs behind a FastAPI server, making it easy to integrate with other web services.
- **WebDAV and Static Site Coexistence:** Can be served alongside WebDAV or a normal website, all on the same domain using Nginx.

## Getting Started

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/PyChat.git
   cd PyChat

Install Dependencies:

pip install -r requirements.txt
Run the Server:

uvicorn server:app --host 0.0.0.0 --port 8000
Your chat server will be available at wss://yourdomain.com/chat (when properly reverse-proxied with Nginx and TLS).

Run the Client: Use the WebSocket-based client.py:

python client.py
When prompted, enter your WebSocket URL (e.g., wss://yourdomain.com/chat) and choose a username and room.

Contributing
Feel free to open issues, submit pull requests, or request features. Contributions are always welcome and appreciated.

License
This project is licensed under the MIT License.

This project was created with the assistance of GPT in o1-pro mode.
