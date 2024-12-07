# client.py

import socket
import threading
import sys
import time  # Ensure time is imported

MAX_MESSAGE_SIZE = 1024  # 1KB


def send_quit_message(client_socket):
    """
    Sends the 'quit' message to the server.
    """
    try:
        client_socket.sendall("quit".encode("utf-8"))
    except Exception as e:
        print(f"[ERROR] Failed to send 'quit' message: {e}")


def send_messages(client_socket, shutdown_event):
    """
    Reads user input and sends messages to the server.
    """
    try:
        while not shutdown_event.is_set():
            try:
                message = input("> ")
            except EOFError:
                # Handle EOF (e.g., Ctrl+D/Ctrl+Z)
                print("\n[INFO] EOF received. Disconnecting from server.")
                send_quit_message(client_socket)
                shutdown_event.set()
                break

            if message.lower() == "quit":
                send_quit_message(client_socket)
                shutdown_event.set()
                break
            elif message.lower() == "/help":
                print(
                    "\nAvailable Commands:\n - quit: Disconnect from the chat\n - /help: Show this help message\n"
                )
            else:
                # Sanitize message
                sanitized_message = "".join(ch for ch in message if ch.isprintable())

                # Limit message size
                encoded_message = sanitized_message.encode("utf-8")
                if len(encoded_message) > MAX_MESSAGE_SIZE:
                    print(
                        "[WARNING] Message too long. Please limit your message to 1KB."
                    )
                    continue

                try:
                    client_socket.sendall(encoded_message)
                except (BrokenPipeError, ConnectionResetError):
                    print("\n[ERROR] Connection lost. Unable to send message.")
                    shutdown_event.set()
                    break
                except Exception as e:
                    print(f"\n[ERROR] An error occurred while sending messages: {e}")
                    shutdown_event.set()
                    break
    except KeyboardInterrupt:
        print("\n[INFO] Keyboard interrupt received. Disconnecting from server.")
        send_quit_message(client_socket)
        shutdown_event.set()
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred while sending messages: {e}")
        shutdown_event.set()
    finally:
        print("[INFO] Sending thread exiting.")


def receive_messages(client_socket, shutdown_event):
    """
    Listens for messages from the server and prints them.
    """
    try:
        while not shutdown_event.is_set():
            try:
                message = client_socket.recv(MAX_MESSAGE_SIZE)
                if message:
                    decoded_message = message.decode("utf-8").strip()
                    if decoded_message.startswith("[SERVER]"):
                        # Display server messages distinctly
                        print(
                            f"\r\033[93m{decoded_message}\033[0m\n> ",
                            end="",
                            flush=True,
                        )
                    else:
                        # Print regular messages
                        print(f"\r{decoded_message}\n> ", end="", flush=True)
                else:
                    # Server closed the connection gracefully
                    print("\n[INFO] Connection closed by server.")
                    shutdown_event.set()
                    break
            except (ConnectionResetError, ConnectionAbortedError):
                # Handle abrupt disconnection from the server
                print("\n[ERROR] Connection with the server was lost.")
                shutdown_event.set()
                break
            except UnicodeDecodeError:
                # Handle decoding errors
                print("\n[ERROR] Received a message that could not be decoded.")
                continue
            except Exception as e:
                print(f"\n[ERROR] An error occurred while receiving messages: {e}")
                shutdown_event.set()
                break
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred while receiving messages: {e}")
        shutdown_event.set()
    finally:
        print("[INFO] Receiving thread exiting.")


def main():
    """
    Main function to run the client.
    """
    # Ask the user for the server IP address, port, and nickname
    host = input("Enter the server IP address [localhost]: ") or "localhost"
    port_input = input("Enter the server port [42069]: ") or "42069"
    nickname = input("Enter your nickname [Anonymous]: ") or "Anonymous"

    try:
        port = int(port_input)
    except ValueError:
        print("[ERROR] Port must be an integer.")
        sys.exit()

    # Initialize the shutdown event
    shutdown_event = threading.Event()

    # Create a TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # Connect the socket to the server
        try:
            client_socket.connect((host, port))
            print(f"[CONNECTED] Connected to server at {host}:{port}")
        except (ConnectionRefusedError, socket.timeout):
            print(f"[ERROR] Unable to connect to server at {host}:{port}")
            client_socket.close()
            sys.exit()
        except socket.gaierror:
            print(f"[ERROR] Invalid server IP address: {host}")
            client_socket.close()
            sys.exit()
        except Exception as e:
            print(f"[ERROR] An unexpected error occurred while connecting: {e}")
            client_socket.close()
            sys.exit()

        # Send the nickname to the server
        try:
            client_socket.sendall(nickname.encode("utf-8"))
        except Exception as e:
            print(f"[ERROR] Failed to send nickname: {e}")
            client_socket.close()
            sys.exit()

        # Start threads for receiving and sending messages
        receive_thread = threading.Thread(
            target=receive_messages, args=(client_socket, shutdown_event)
        )
        receive_thread.daemon = True  # Allows thread to exit when main thread exits
        receive_thread.start()

        send_thread = threading.Thread(
            target=send_messages, args=(client_socket, shutdown_event)
        )
        send_thread.daemon = True
        send_thread.start()

        # Wait for the threads to finish or a KeyboardInterrupt
        try:
            while receive_thread.is_alive() and send_thread.is_alive():
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n[INFO] Keyboard interrupt received. Exiting...")
            shutdown_event.set()
        finally:
            # Ensure threads have finished
            receive_thread.join()
            send_thread.join()
            # Close the socket
            client_socket.close()
            print("[INFO] Client shutdown complete.")
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        client_socket.close()
        sys.exit()


if __name__ == "__main__":
    main()
