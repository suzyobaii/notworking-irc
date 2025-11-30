import socket
import threading
from ChatProtocol import Command, Event, Message, serialize, deserialize
from argparse import ArgumentParser

import logging
from logger import setupLogServer



"""
A user represents a client in the server. Each user in the server 
needs to have a unique name. When a client joins the server they are
automatically generated a nickname via the user_id counter and they
are put in a channel by themselves. 
"""
class User:
	user_id = 1 # Class wide variable
	

	def __init__(self, conn, addr):
		self.conn = conn
		self.addr = addr
		self.nickname = f"Guest_{User.user_id}"

		# Automatically create a new channel with only the user
		self.curr_channel = Channel(self)
		self.channels = {self.curr_channel}

		User.user_id += 1 # When a new user is added, increment the id
		logging.info(f"A new connection from {addr} that was assigned the nickname {user.nickname}")

	def join_channel(self, channel):
		if channel in self.channels:
			if channel == self.curr_channel:
				return f"You are already in [{channel.name}]."
			else:
				self.curr_channel = channel
				logging.info(f"{self.nickname} switched to the specific channel [{channel.name}]")
				return f"You are now in [{channel.name}]."

		self.channels.add(channel)
		self.curr_channel = channel
		channel.add_user(self)
		logging.info(f"{self.nickname} joined the channel [{channel.name}]")
		return f"You have joined [{channel.name}]."

	def leave_channel(self, channel):
		self.channels.remove(channel)
		self.curr_channel = None
		channel.remove_user(self)
		logging.info(f"{self.nickname} left the channel [{channel.name}]")

	def leave_all_channels(self): # triggers when a client quits the server
		logging.info(f"{self.nickname} is leaving all channels (disconnecting)")
		if self.channels:
			for channel in self.channels:
				channel.remove_user(self)

	def display_channels(self):
		if self.channels:
			display = "\nYou are a member of the channel(s):"
			for channel in self.channels:
				display += f" [{channel.name}] |"

			if self.curr_channel:
				display += f"\nYou are currently in [{self.curr_channel.name}]."
			else:
				display += f"\nYou are currently not in a channel."
		else:
			display = "\nYou are not in any channels."

		return display


"""
A channel is a named group of one or more clients. All clients receive
messages addressed to the channel. A channel is created when a client
joins. A client can reference the channel using the channel name. 
"""
class Channel:
	channel_id = 1 # class wide variable

	def __init__(self, user, name=None):
		self.users = {user}
		if name:
			self.name = name
		else:
			self.name = f"Channel_{Channel.channel_id}"
			Channel.channel_id += 1
			logging.info(f"Channel created: {self.name} with initial user {user.nickname}")

	# Messages sent to the channel are broadcast to all users (except sender)
	def broadcast(self, user, message):
		message.sender = user.nickname
		logging.info(f"A message broadcast by {user.nickname} in [{self.name}]")

		for member in self.users:
			if member != user:
				if member.curr_channel != self: # include what channel the message comes from
					message.channel = self.name

				member.conn.sendall(serialize(message).encode('utf-8'))

	# Add a user to the channel when they use the /join command
	def add_user(self, user):
		self.users.add(user)
		logging.info(f"{user.nickname} was added to channel [{self.name}]")

	# Remove a user when they use the /leave command
	def remove_user(self, user):
		self.users.remove(user)
		logging.info(f"{user.nickname} was removed from channel [{self.name}]")

	def display_user_count(self):
		return f"\n[{self.name}] has {len(self.users)} user(s)."


"""
A Server is a place where clients can connect to. It takes in a 
port number and a debug level (0 or 1) as arguments. Channels are 
created in servers. The server logs user interactions and manages
channels and clients. The server should automatically shutdown when
there is no activity for 3 minutes. A maximum of 4 clients can be
on the server at the same time. 
"""
class ChatServer:
	def __init__(self, port, debug_level=0):
		self.host = '127.0.0.1'
		self.port = port
		self.debug_level = debug_level
		self.socket = None
		self.channels = {}
		self.clients = set()
		self.unique_nicknames = set()
	
	def log(self, message, level=1):
		# level 0 = crit error, level 1 = all venets
		if level <= self.debug_level:
			print(message)

	# Server will start running at the port number
	def startup(self):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

		self.socket.bind((self.host, self.port))
		self.socket.listen(4) # Maximum of 4 threads (clients)

		self.log(f"TCP server listening on {self.host} : {self.port}", level=0)
		logging.info(f"Server started on {self.host}:{self.port}")
		self.accept_clients()


	def accept_clients(self):
		self.socket.settimeout(180) # 3 minute timeout for idle server
		try:
			while True:
				try:
					conn, addr = self.socket.accept()
				except socket.timeout:
					# If timeout occurs and no clients conennected, timeout
					if len(self.clients) == 0:
						self.log("Server idle for 3 minutes... Shutting Down.", level=0)
						logging.warning("Server idle for 3 minutes, shutting down")
						break
					else:
						continue
				# continuation of Tina's Code	
				user = User(conn, addr)
				self.clients.add(user)
				self.unique_nicknames.add(user.nickname)

				self.channels[user.curr_channel.name] = user.curr_channel

				self.log("A new user has joined the server!", level=1)
				logging.info(f"User {user.nickname} joined server")

				t = threading.Thread(target=self.handle_client, args=(user,), daemon=True)
				t.start()
		except KeyboardInterrupt:
			self.log("\nShutting down connection...")
			logging.warning("KeyboardInterrupt , shutting down server")

		finally:
			self.shutdown()



	"""
	Protocol objects are transmitted between server and client. 
	This requires serializing and deserializing the object. A client
	sends only command or message objects while the server sends
	only event or message objects.
	"""
	def handle_client(self, user):
		# Assign user a unique nickname when they join the server
		user.conn.sendall(serialize(Event(type="nick", 
									  notif="You have been assigned a new nickname by default. Use /nick to change it.", 
									  optional=user.nickname)).encode('utf-8'))
		logging.info(f"Sent a nickname assignment to {user.nickname}")

		while True:
			try:
				data = user.conn.recv(1024)
				if not data:
					logging.warning(f"User {user.nickname} disconnected")
					break

				response = deserialize(data)

				if isinstance(response, Command):
					self.log(response.cmd, level=1) # For testing purposes
					logging.info(f"{user.nickname} sent the command: {response.cmd}")

					if response.cmd == "/quit":
						user.leave_all_channels()
						self.clients.remove(user)
						logging.info(f"{user.nickname} quit the server")

						break

					if response.cmd == "/nick":
						if response.args[0] in self.unique_nicknames:
							logging.warning(f"the nickname {newnick} already taken")
							event = Event(type="error", notif="Nickname already taken. Try another nickname.")
						else:
							if user.nickname in self.unique_nicknames:
								self.unique_nicknames.remove(user.nickname)

							user.nickname = response.args[0]
							self.unique_nicknames.add(user.nickname)
							notif = f"Nickname updated to {user.nickname}"
							logging.info(f"the nickname changed to {newnick}")
							event = Event(type="nick", notif=notif, optional=user.nickname)

					elif response.cmd == "/list":
						logging.info(f"the {user.nickname} requested the list of channels on the server")
						notif = "List of channels on the server:"
						for channel in self.channels.values():
							notif += channel.display_user_count()

						notif += user.display_channels()

						event = Event(type="list", notif=notif)

					elif response.cmd == "/join":
						channel = response.args[0]
						logging.info(f"{user.nickname} requested to joing the channel: {channel_name}")
						if channel in self.channels:
							notif = user.join_channel(self.channels[channel])
							event = Event(type="join", notif=notif)
						else:
							event = Event(type="error", notif="No such channel exists. Use /list to see all channels.")

					elif response.cmd == "/leave":
						# Case for leaving a named channel
						logging.info(f"the {user.nickname} requested to leave the channel")
						if len(response.args):
							if response.args[0] in self.channels: # Check if the channel exists
								channel = self.channels[response.args[0]]
								if channel in user.channels: # Check if the user is in the channel
									user.leave_channel(channel)
									event = Event(type="leave", notif=f"You have left [{channel.name}].")
								else:
									event = Event(type="error", notif="You are not in this channel. Use /list to see all channels.")
							else:
								event = Event(type="error", notif="No such channel exists. Use /list to see all channels.")

						# Case for leaving the channel the user is currently in
						else:
							channel = user.curr_channel
							logging.info(f"{user.nickname} sent the  message: {response.content}")
							if channel:
								user.leave_channel(channel)
								event = Event(type="leave", notif=f"You have left [{channel.name}].")
							else:
								event = Event(type="error", notif="You are currently not in a channel.")

					user.conn.sendall(serialize(event).encode('utf-8'))
							
				elif isinstance(response, Message):
					self.log("Sending a message.", level=1) # For testing purposes
					if user.curr_channel:
						user.curr_channel.broadcast(user, response)
					else:
						event = Event(type="error", notif="You are currently not in a channel. Use /join <channel> to join a channel.")
						user.conn.sendall(serialize(event).encode('utf-8'))

				else:
					raise ValueError("Unknown object type sent.")

			except KeyboardInterrupt:
				logging.warning("the server was interrupted while handling client and shutdown")
				self.log("\nServer shutting down...", level=1)


	def shutdown(self):
		self.log("\nServer is shutting down...", level=0)
		logging.info("Server shutting down...")

		for user in list(self.clients):
			
			try:
				user.conn.close()
				logging.info(f"closing the  connection for {user.nickname}")
			
			except Exception as e:
				
				self.log(f"Error closing connection for {user.addr}: {e}", level=0)
				logging.error(f"There ws an error closing connection for {user.addr}: {e}")
		
		self.clients.clear()

		if self.socket:
			try:
				self.socket.close()
			
			except Exception as e:
				self.log(f"Error closing server socket: {e}", level=0)
				logging.error(f"There was an error closing server socket: {e}")



def main():
	setupLogServer()
	logging.info("Server Logging initialized")
	"""
	The server takes in arguments for the port and debug-level.
	Type in terminal python3 ChatServer.py -p <port#> -d <debug-level>
	to pass arguments to the server. 
	"""
	parser = ArgumentParser(description='Create a Chat Server.')
	parser.add_argument('-p', '--port', type=int, default=65432, help='Port Number: (default=65432)')
	parser.add_argument('-d', '--debug', type=int, default=0, choices=[0, 1],
                        help='Debug-level: 0=errors only (default), 1=all events')
	args = parser.parse_args()

	server = ChatServer(port=args.port, debug_level=args.debug)
	server.startup()


if __name__=="__main__":
	main()