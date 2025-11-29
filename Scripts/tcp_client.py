import socket
import threading
import sys
import os
import signal

# Logging and declaring the different colors
import logging

from log_setup import setupLogClient
# ANSI color codes 
RESET = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
BOLD = "\033[1m"


setupLogClient()
logging.info("Client Logging initialized")


client_socket = None
connected = False
nickname = "Guest"

def display_help():
    # List available commands
    
	# multi-line formatted string defining the help messages
    help_message = f"""
{BOLD}{CYAN}--- Chat Client Help Commands ---{RESET}

{BLUE}/connect <server-name> [port#]{RESET}  - connect to the specified server.

{BLUE}/nick <nickname>{RESET}               - Pick a unique nickname.

{BLUE}/list{RESET}                        - List all connected users.

{BLUE}/join <channel>{RESET}                - Join a specific channel.

{BLUE}/leave [<channel>]{RESET}            - Leave the current or specific channel.

{BLUE}/quit{RESET} 					       - Leave chat and Disconnect from the server.

{BLUE}/help{RESET} 						   - Display this help message.

"""
    print(help_message)

def connect_to_server(server_name, port):
    
	# connect to a server using the provided server name and port
    
	global client_socket, connected
      
	if connected:
		print(f"{YELLOW}---Already connected to a server.---{RESET}")
		return
	
	try:
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket.connect((server_name, port))
		connected = True

		threading.Thread(target=receive_messages, daemon = True).start()
		print(f"{YELLOW}--- Connected to server {server_name}:{port} ---{RESET}")
	except Exception as e:
		print(f"{RED}--- Connection failed: {e} ---{RESET}")
		connected = False
		client_socket = None	


def disconnect_from_server():

	global client_socket, connected

	if connected:
		try:

			if client_socket:
				client_socket.sendall("/quit".encode('utf-8))'))
			client_socket.close()
		
		except:
			pass
		finally:
			connected = False
			client_socket = None
			print(f"{RED}--- Disconnected from server.---{RESET}")
		os._exit(0)
	

def receive_messages():
	global connected

	while connected:
		try:
			data = client_socket.recv(1024)
			if not data:
				print("{RED}\n--- Server closed the connection. ---{RESET}")
				disconnect_from_server()
				break

			print(f"\r{data.decode('utf-8')}\n", end='')
			sys.stdout(f"{nickname}>")
			sys.stdout.flush()
		
		except ConnectionResetError:
			print("{MAGENTA}\n--- Connection lost. ---{RESET}")
			connected = False
			break
		except Exception as e:
			if connected:
				print(f"{MAGENTA}\n--- Error receiving message: {e} ---{RESET}")
			connected = False
			break


def send_message(message):
	global client_socket, connected

	if connected and client_socket:
		try:
			client_socket.sendall(message.encode('utf-8'))
		except Exception as e:
			print(f"{RED}--- Error sending message: {e} ---{RESET}")
			connected = False
			client_socket.close()
	else:
		print(f"{BLUE}--- Not connected to any server. ---{RESET}")



def user_interface_loop():
	# This function will handle user input and command functionality

	global nickname, connected, client_socket # Access global variables

	def signal_handler(sign, frame):
		# This is how we handle Ctrl+C
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

			if not message:
				continue

			if message.startswith('/'):
				split = message.split()
				command = split[0].lower()
				args = split[1:]

				if command == '/connect':
					host = args[0]
					port = int(args[1]) if len(args) > 1 else 65432 # maximum port number
					connect_to_server(host, port)
				
				elif command == '/quit':
					disconnect_from_server()

				elif command == '/help':
					display_help()
				
				elif connected:
					if command == '/nick':
						if len(args) != 1:
							print(f"{YELLOW}Usage: /nick <nickname>{RESET}")
						else:
							nickname = args[0]
							client_socket.sendall(f"/nick {nickname}".encode())
					
					elif command == '/list':
						client_socket.sendall("/list".encode())
					
					elif command == '/join':
						if len(args) != 1:
							print(f"{YELLOW}Usage: /join <channel>{RESET}")
						else:
							client_socket.sendall(f"/join {args[0]}".encode())
					
					elif command == '/leave':
						channel = args[0] if args else ""
						client_socket.sendall(f"/leave {channel}".encode())
					
					else:
						print(f"{RED}Unknown command. Type /help for a list of commands.{RESET}")

				else:
					print(f"{RED}Not connected to any server. Use /connect to connect.{RESET}")
				
			elif connected:
				send_message(message)

			else:
				print(f"{RED}Not connected to any server. Use /connect to connect.{RESET}")
		except EOFError:
			disconnect_from_server()
		
		except Exception as e:
			disconnect_from_server()

if __name__ == "__main__":
	user_interface_loop()