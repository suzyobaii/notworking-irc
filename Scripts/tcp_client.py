import socket
import threading
import sys
import os
import signal
from ChatProtocol import Command, Event, Message, serialize, deserialize

import logging
from logger import setupLogClient

# ANSI COlor Cides

RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"

client_socket = None
connected = False
nickname = "Guest"

def display_help():
    logging.info("Displayed help menu")
    # List available commands
    
	# multi-line formatted string defining the help messages
    help_message = f"""
{BOLD}{GREEN}--- Chat Client Help Commands --- {RESET} 

{BLUE}/connect <server-name> [port#] - connect to the specified server.{RESET}

{BLUE}/nick <nickname>               - Pick a unique nickname.{RESET}

{BLUE}/list                          - List all connected users.{RESET}

{BLUE}/join <channel>                - Join a specific channel.{RESET}

{BLUE}/leave [<channel>]             - Leave the current or specific channel.{RESET}

{BLUE}/quit                          - Leave chat and Disconnect from the server.{RESET}

{BLUE}/help                          - Display this help message.{RESET}

"""
    print(help_message)

def connect_to_server(server_name, port):
    
	# connect to a server using the provided server name and port
    
	global client_socket, connected
	logging.info(f"Attempted connection to {server_name}:{port}")
      
	if connected:
		logging.warning("Attempted to connect while already connected")
		print(f"{YELLOW}---Already connected to a server.---{RESET}")
		return
	
	try:
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket.connect((server_name, port))
		connected = True

		logging.info(f"Successfully connected to the {server_name}:{port}")

		threading.Thread(target=receive_messages, daemon = True).start()
		print(f"{YELLOW}--- Connected to server {server_name}:{port} ---{RESET}")
	except Exception as e:
		logging.error(f"Connection failed: {e}")
		print(f"{RED}--- Connection failed: {e} ---{RESET}")
		connected = False
		client_socket = None	


def disconnect_from_server():

	global client_socket, connected
	logging.info("Client requested disconnect")

	if connected:
		try:

			if client_socket:
				client_socket.sendall(serialize(Command(cmd="/quit")).encode('utf-8'))
			client_socket.close()
		
		except:
			logging.error(f"Error while disconnecting: {e}")
			pass
		finally:
			connected = False
			client_socket = None
			print(f"{RED}--- Disconnected from server.---{RESET}")
		os._exit(0)
	

def receive_messages():
	global connected, nickname
	logging.info("Started message receiver thread")

	while connected:
		try:
			data = client_socket.recv(1024)
			if not data:
				logging.warning(" The srver closed the connection")
				print(f"\n{RED}--- Server closed the connection. ---{RESET}")
				disconnect_from_server()
				break

			response = deserialize(data.decode('utf-8'))
			logging.info(f"received the message: {response}")

			if isinstance(response, Event):
				print(f"\r{response.notif}\n", end='')

				if response.type == "nick":
					nickname = response.optional
					logging.info(f"The nickname was updated to {nickname}")

			elif isinstance(response, Message):
				if response.channel: # Label message as a notification
					print(f"\r{GREEN}FROM [{response.channel}] {RESET}{CYAN}{response.sender}>{RESET}{response.content}\n", end='')
				else:
					print(f"\r{CYAN}{response.sender}>{RESET}{response.content}\n", end='')

			else:
				logging.error("received an unknown response")
				raise ValueError(f"{MAGENTA}Unknown response sent.{RESET}")

			sys.stdout.write(f"{CYAN}{nickname}>{RESET}")
			sys.stdout.flush()
		
		except ConnectionResetError:
			logging.error(f"receive this error: {e}")
			logging.error("Connection lost (ConnectionResetError)")
			print(f"{MAGENTA}\n--- Connection lost. ---{RESET}")
			connected = False
			break
		except Exception as e:
			if connected:
				print(f"{MAGENTA}\n--- Error receiving message: {e} ---{RESET}")
			connected = False
			break


def send_message(message):
	global client_socket, connected
	logging.info(f"{nickname} typed: {message}")
	if connected and client_socket:
		try:
			logging.info("Sent message to server")
			msg = Message(content=message)
			client_socket.sendall(serialize(msg).encode('utf-8'))
		except Exception as e:
			logging.error(f"Error sending message: {e}")
			print(f"{RED}--- Error sending message: {e} ---{RESET}")
			connected = False
			client_socket.close()
	else:
		logging.warning("There was an attempt to send message while disconnected")
		print(f"{BLUE}--- Not connected to any server. ---{RESET}")



def user_interface_loop():
	setupLogClient()
	logging.info("Client Logging initialized")


	# This function will handle user input and command functionality

	global nickname, connected, client_socket # Access global variables

	def signal_handler(sign, frame):
		# This is how we handle Ctrl+C
		logging.warning("The keyboard interrupt received")
		print(f"{RED}\n --- Keyboard Intrrpt. Exiting. . . ---{RESET}")
		disconnect_from_server()

	signal.signal(signal.SIGINT, signal_handler)
	
	display_help()

	while True:
		try:
			
			prompt = f"{MAGENTA}{nickname}>{RESET}"
			sys.stdout.write(prompt)
			sys.stdout.flush()

			message = sys.stdin.readline().strip()
			logging.info(f"User input received: {message}")

			if not message:
				continue

			if message.startswith('/'): # if the message is a command
				split = message.split()
				cmd = split[0].lower()
				args = split[1:]
				logging.info(f"User entered command: {cmd} Args: {args}")

				if cmd == '/connect':
					host = args[0]
					port = int(args[1]) if len(args) > 1 else 65432 # maximum port number
					connect_to_server(host, port)
				
				elif cmd == '/quit':
					disconnect_from_server()

				elif cmd == '/help':
					display_help()
				
				elif connected:
					command = Command(cmd=cmd, args=args)
					logging.info(f"Sent command to server: {command}")

					if cmd == '/nick':
						if len(args) != 1:
							print(f"{YELLOW}Usage: /nick <nickname>{RESET}")
						else:
							#nickname = args[0]
							client_socket.sendall(serialize(command).encode('utf-8'))
					
					elif cmd == '/list':
						client_socket.sendall(serialize(command).encode('utf-8'))
					
					elif cmd == '/join':
						if len(args) != 1:
							print(f"{YELLOW}Usage: /join <channel>{RESET}")
						else:
							client_socket.sendall(serialize(command).encode('utf-8'))
					
					elif cmd == '/leave':
						client_socket.sendall(serialize(command).encode('utf-8'))
					
					else:
						print(f"{RED}Unknown command. Type /help for a list of commands.{RESET}")
						logging.warning("A command was entered while disconnected")

				else:
					print(f"{RED}Not connected to any server. Use /connect to connect.{RESET}")
					logging.warning("The user tried to send chat message while disconnected")
				
			elif connected:
				send_message(message)

			else:
				print(f"{RED}Not connected to any server. Use /connect to connect.{RESET}")
		except EOFError:
			disconnect_from_server()
			logging.warning("EOF... disconnecting")
		
		except Exception as e:
			logging.error(f"Other error: {e}")
			disconnect_from_server()

if __name__ == "__main__":
	user_interface_loop()