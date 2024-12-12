import asyncio
import sys
import logging
from typing import Optional

import websockets

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


async def receive_messages(
    ws: websockets.WebSocketClientProtocol, stop_event: asyncio.Event
) -> None:
    """
    Continuously receives and displays messages from the server.
    If the connection is closed or an error occurs, set stop_event.
    """
    try:
        async for message in ws:
            # Print the received message on a new line, then show prompt
            sys.stdout.write(f"\n{message}\n >")
            sys.stdout.flush()
    except websockets.ConnectionClosed:
        logging.info("Connection closed by the server.")
    except Exception as e:
        logging.warning(f"Connection error: {e}")
    finally:
        stop_event.set()


async def main():
    """
    Main entry point for the PyChat WebSocket Client.
    Prompts user for server URL and username, connects to the WebSocket endpoint,
    and exchanges messages.
    """

    print("Welcome to PyChat WebSocket Client!")
    print(
        "You will be prompted for the server WebSocket URL (e.g. wss://dunamismax.com/chat) and a desired username.\n"
    )

    server_url = (
        input("Enter the server WebSocket URL [wss://dunamismax.com/chat]: ").strip()
        or "wss://dunamismax.com/chat"
    )
    desired_username = input("Enter your desired username: ").strip() or "User"

    # Connect to the WebSocket server
    try:
        async with websockets.connect(server_url) as ws:
            # The server first asks for the username
            # Receive the server's initial prompt
            prompt = await ws.recv()
            print(prompt)  # "Enter your desired username:"

            # Send the desired username
            await ws.send(desired_username)

            # Assigned username
            assigned_line = await ws.recv()
            if not assigned_line.startswith("Your username is:"):
                logging.error(
                    "Unexpected response from server when assigning username."
                )
                return
            assigned_username = assigned_line.replace("Your username is:", "").strip()

            # Receive the room list prompt
            room_list_data = await ws.recv()
            sys.stdout.write(room_list_data + "\n")
            sys.stdout.flush()

            # Prompt user to choose a room by number
            chosen_room_num = input("").strip()
            await ws.send(chosen_room_num)

            # The server may respond with invalid choice message or proceed
            # This message may or may not come, so we do a quick check
            try:
                # We use asyncio.wait_for in case there's no extra message
                invalid_msg = await asyncio.wait_for(ws.recv(), timeout=0.5)
                if invalid_msg.startswith("Invalid choice"):
                    print(invalid_msg)
                else:
                    # Not an invalid message, it's probably the next prompt
                    # Put it back into flow by printing it
                    print(invalid_msg)
            except asyncio.TimeoutError:
                # No invalid message was sent, continue
                pass

            # Instructions after joining the room
            print("\n" + "=" * 50)
            print(f"Welcome, {assigned_username}!")
            print("You are now connected to the chat room.")
            print("Type your message and press Enter to send.")
            print("Type /quit to leave the chat.")
            print("=" * 50 + "\n")

            stop_event = asyncio.Event()

            # Start the receiver task
            receiver_task = asyncio.create_task(receive_messages(ws, stop_event))

            # Prompt the user
            sys.stdout.write("> ")
            sys.stdout.flush()

            # Main send loop
            loop = asyncio.get_event_loop()
            while not stop_event.is_set():
                # Reading user input asynchronously
                # We'll run input reading in a thread to not block the event loop
                try:
                    msg = await loop.run_in_executor(None, sys.stdin.readline)
                except (KeyboardInterrupt, EOFError):
                    # Treat as /quit
                    msg = "/quit\n"
                msg = msg.strip()

                if stop_event.is_set():
                    break

                if msg.lower() == "/quit":
                    # Inform the server we are quitting
                    try:
                        await ws.send(msg)
                    except Exception:
                        pass
                    break

                # Send the message to the server
                if msg:
                    try:
                        await ws.send(msg)
                    except Exception as e:
                        logging.warning(f"Failed to send message to server: {e}")
                        stop_event.set()
                        break

                # Reprint prompt after sending
                if not stop_event.is_set():
                    sys.stdout.write("> ")
                    sys.stdout.flush()

            stop_event.set()
            receiver_task.cancel()
            print("\n[SYSTEM] Disconnected. Bye!")

    except Exception as e:
        logging.error(f"Failed to connect or error during communication: {e}")


if __name__ == "__main__":
    asyncio.run(main())
