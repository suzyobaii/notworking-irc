import socket
import threading
import sys
import os
import signal

# Logging and color
import logging
import colorama
from log_setup import setupLogClient
from colorama import Fore, Style, init
init(autoreset=True)

setupLogClient()
logging.info("Client Logging initialized")


client_socket = None
connected = False
nickname = "Guest"

def display_help():
    # List available commands
    
	# multi-line formatted string defining the help messages
    help_message = f"""
{Fore.CYAN + Style.BRIGHT}--- Chat Client Help Commands ---

{Fore.BLUE}/connect <server-name> [port#]{Fore.RESET}  - connect to the specified server.

{Fore.BLUE}/nick <nickname>{Fore.RESET}               - Pick a unique nickname.

{Fore.BLUE}/list{Fore.RESET}                        - List all connected users.

{Fore.BLUE}/join <channel>{Fore.RESET}                - Join a specific channel.

{Fore.BLUE}/leave [<channel>]{Fore.RESET}            - Leave the current or specific channel.

{Fore.BLUE}/quit{Fore.RESET} 					       - Leave chat and Disconnect from the server.

{Fore.BLUE}/help{Fore.RESET} 						   - Display this help message.

"""
    print(help_message)

def connect_to_server(server_name, port):
    
	# connect to a server using the provided server name and port
    
	global client_socket, connected
      
	if connected:
		print(Fore.YELLOW + "---Already connected to a server.---")
		return
	
	try:
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket.connect((server_name, port))
		connected = True

		threading.Thread(target=receive_messages, daemon = True).start()
		print(Fore.YELLOW + f"--- Connected to server {server_name}:{port} ---")
	except Exception as e:
		print(Fore.RED + f"--- Connection failed: {e} ---")
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
			print(Fore.YELLOW + "--- Disconnected from server.---")
		os._exit(0)
	

def receive_messages():
	global connected

	while connected:
		try:
			data = client_socket.recv(1024)
			if not data:
				print(Fore.RED + "\n--- Server closed the connection. ---")
				disconnect_from_server()
				break

			print(f"\r{data.decode('utf-8')}\n", end='')
			sys.stdout(f"{nickname}>")
			sys.stdout.flush()
		
		except ConnectionResetError:
			print(Fore.MAGENTA + "\n--- Connection lost. ---")
			connected = False
			break
		except Exception as e:
			if connected:
				print(Fore.MAGENTA + f"\n--- Error receiving message: {e} ---")
			connected = False
			break


def send_message(message):
	global client_socket, connected

	if connected and client_socket:
		try:
			client_socket.sendall(message.encode('utf-8'))
		except Exception as e:
			print(Fore.RED + f"--- Error sending message: {e} ---")
			connected = False
			client_socket.close()
	else:
		print(Fore.MAGENTA + "--- Not connected to any server. ---")



def user_interface_loop():
	# This function will handle user input and command functionality

	global nickname, connected, client_socket # Access global variables

	def signal_handler(sign, frame):
		# This is how we handle Ctrl+C
		print(Fore.RED + f"\n --- Keyboard Intrrpt. Exiting. . . ---")
		disconnect_from_server()

	signal.signal(signal.SIGINT, signal_handler)
	
	display_help()

	while True:
		try:
			
			prompt = f"{nickname}>"
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
							print(Fore.YELLOW + "Usage: /nick <nickname>")
						else:
							nickname = args[0]
							client_socket.sendall(f"/nick {nickname}".encode())
					
					elif command == '/list':
						client_socket.sendall("/list".encode())
					
					elif command == '/join':
						if len(args) != 1:
							print(Fore.GREEN + "Usage: /join <channel>")
						else:
							client_socket.sendall(f"/join {args[0]}".encode())
					
					elif command == '/leave':
						channel = args[0] if args else ""
						client_socket.sendall(f"/leave {channel}".encode())
					
					else:
						print(Fore.RED + "Unknown command. Type /help for a list of commands.")

				else:
					print(Fore.RED + "Not connected to any server. Use /connect to connect.")
				
			elif connected:
				send_message(message)

			else:
				print(Fore.RED + "Not connected to any server. Use /connect to connect.")
		except EOFError:
			disconnect_from_server()
		
		except Exception as e:
			disconnect_from_server()

if __name__ == "__main__":
	user_interface_loop()