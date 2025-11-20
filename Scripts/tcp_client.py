import socket
import threading
import sys
import os
import signal

client_socket = None
connected = False
nickname = "Guest"

def display_help():
    # List available commands
    
	# multi-line formatted string defining the help messages
    help_message = f"""
--- Chat Client Help Commands ---

/connect <server-name> [port#] - connect to the specified server.

/nick <nickname>               - Pick a unique nickname.

/list                          - List all connected users.

/join <channel>                - Join a specific channel.

/leave [<channel>]             - Leave the current or specific channel.

/quite					       - Leave chat and Disconnect from the server.

/help						   - Display this help message.

"""
    print(help_message)

def connect_to_server(server_name, port):
    
	# connect to a server using the provided server name and port
    
	global client_socket, connected
      
	if connected:
		print("Already connected to a server.")
		return
	
	else:
		try:
			client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			client_socket.connect((server_name, port))
			connected = True

			threading.Thread(target=receive_messages, daemon = True).start()
		except:










def user_interface_loop():
	# This function will handle user input and command functionality

	global nickname, connected, client_socket # Access global variables

	def signal_handler(sign, frame):
		# This is how we handle Ctrl+C
		print(f"\n --- Keyboard Intrrpt. Exiting. . . ---")
		disconnect_from_server()

	signal.signal(signal.SIGINT, signal_handler)
	
	display_help()

	while True:
		try:
			
			prompt = f"{nickname>}"
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
				
				elif command == '/nick':