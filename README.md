# Python Chat Application

A simple multi-client chat application built with Python's `socket` and `threading` modules. This project consists of a server and client that allow multiple users to communicate in real-time over a network.

## Table of Contents

- [Python Chat Application](#python-chat-application)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Running the Server](#running-the-server)
    - [Running the Client](#running-the-client)
  - [Commands](#commands)
  - [Configuration](#configuration)
    - [Server Configuration](#server-configuration)
    - [Client Configuration](#client-configuration)
  - [Logging](#logging)
  - [Security Measures](#security-measures)
  - [Known Issues](#known-issues)
  - [Contributing](#contributing)
  - [License](#license)

## Features

- **Multi-client Support**: Multiple clients can connect to the server simultaneously and engage in a group chat.
- **Nickname Management**: Users can choose a nickname upon connecting.
- **Message Broadcasting**: Messages are broadcast to all connected clients.
- **Rate Limiting**: Prevents spamming by limiting the number of messages a client can send within a time window.
- **Message Size Limit**: Enforces a maximum message size to prevent resource exhaustion.
- **Connection Limit**: Limits the number of concurrent client connections to the server.
- **Input Sanitization**: Removes non-printable characters from messages to ensure safe broadcasting.
- **Graceful Disconnection**: Clients can gracefully disconnect from the server.
- **Command Support**: Clients can use commands like `/help` and `quit`.
- **Logging**: Server activity, including messages and connection events, is logged to a file.

## Prerequisites

- **Python 3.6+**: Ensure you have Python 3.6 or higher installed on your system.
- **Operating System**: The application is cross-platform and should run on Windows, macOS, and Linux.

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/DunamisMax/PyChat
   ```

2. **Navigate to the Project Directory**

   ```bash
   cd PyChat
   ```

## Usage

### Running the Server

1. **Navigate to the Project Directory**

   ```bash
   cd path/to/server.py
   ```

2. **Run the Server Script**

   ```bash
   python server.py
   ```

   **Optional Server Arguments:**

   - `--host`: The server IP address to bind to. Default is `0.0.0.0` (all interfaces).
   - `--port`: The server port to listen on. Default is `42069`.

   **Example with Arguments:**

   ```bash
   python server.py --host 0.0.0.0 --port 42069
   ```

3. **Server Output**

   - The server will start and display:

     ```
     [STARTING] Server is starting...
     [LISTENING] Server is listening on 0.0.0.0:42069
     ```

### Running the Client

1. **Navigate to the Project Directory**

   ```bash
   cd path/to/client.py
   ```

2. **Run the Client Script**

   ```bash
   python client.py
   ```

3. **Follow the Prompts**

   - **Enter the Server IP Address**

     ```
     Enter the server IP address [localhost]:
     ```

     - Press Enter to use the default `localhost` or type the server's IP address.

   - **Enter the Server Port**

     ```
     Enter the server port [42069]:
     ```

     - Press Enter to use the default `42069` or enter the server's port.

   - **Enter Your Nickname**

     ```
     Enter your nickname [Anonymous]:
     ```

     - Press Enter to use the default `Anonymous` or provide a nickname.

4. **Chatting**

   - After connecting, you can start sending messages.
   - Type `quit` to disconnect from the server.
   - Type `/help` to see available commands.

## Commands

- **`quit`**: Disconnect from the chat server.
- **`/help`**: Display available commands.

## Configuration

### Server Configuration

- **Host and Port**

  - Default host is `0.0.0.0` (listens on all interfaces).
  - Default port is `42069`.
  - Change these via command-line arguments.

- **Rate Limiting**

  - **Rate Limit**: Maximum messages allowed per client within the time window (default is 5 messages).
  - **Rate Limit Period**: Time window in seconds for rate limiting (default is 10 seconds).
  - Modify `RATE_LIMIT` and `RATE_LIMIT_PERIOD` variables in `server.py`.

- **Message Size Limit**

  - **Maximum Message Size**: Default is `1024` bytes (1KB).
  - Modify `MAX_MESSAGE_SIZE` variable in both `server.py` and `client.py` to change the limit.

- **Maximum Concurrent Connections**

  - **Default**: `100` clients.
  - Modify `MAX_CONNECTIONS` variable in `server.py`.

### Client Configuration

- **Default Host and Port**

  - The client prompts for the server IP and port but provides defaults:
    - Host: `localhost`
    - Port: `42069`

## Logging

- **Server Logging**

  - All server activities are logged to `chat_server.log`.
  - Includes timestamps, connection events, messages, and errors.
  - Logs are helpful for monitoring and troubleshooting.

## Security Measures

- **Rate Limiting**

  - Prevents clients from spamming messages.

- **Message Size Restrictions**

  - Protects the server from resource exhaustion due to large messages.

- **Connection Limits**

  - Prevents too many simultaneous connections that could overwhelm the server.

- **Input Sanitization**

  - Removes non-printable characters to prevent potential injection attacks.

## Known Issues

- **No Encryption**

  - Communication between the client and server is unencrypted (plain text).
  - For secure communication, consider implementing SSL/TLS encryption.

- **No Authentication**

  - The server allows any client to connect without credentials.
  - Implement authentication mechanisms if needed.

## Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1. **Fork the Repository**

   - Click the "Fork" button at the top right of the repository page.

2. **Create a Feature Branch**

   ```bash
   git checkout -b feature/YourFeature
   ```

3. **Commit Your Changes**

   ```bash
   git commit -am 'Add your feature'
   ```

4. **Push to Your Fork**

   ```bash
   git push origin feature/YourFeature
   ```

5. **Submit a Pull Request**

   - Open a pull request to merge your changes into the main repository.

## License

This project is licensed under the [MIT License](LICENSE).
