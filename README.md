# CSC4220/6220: Computer Networks - Team Project

## Notworking Team Members

- Kelly Jacinto Ozuna - suzyobaii  
- Jonathan Ermias - jonathanermias  
- Tina Tran - TT-ran  
- Mumo Musyoka - mumomuthike  

## Demo Video

https://youtu.be/qDWwT4kRLZg?si=ljAdpxAW37Mp5JOo

## File/Folder Manifest

project organization:
notworking-irc/
── Scripts/ #main src code
    - pycache/ #python cache files
    - ChatProtocol.py #object-based protocol for commands, events, messages  
    - logger.py #logging setup for client and server
    - tcp_client.py #chat client 
    - tcp_server.py #chat server 
── README.md #this file


## Building and Running the Server/Clients

### Prerequisites
- Python 3.10+ installed on your machine  
- A terminal or command-line interface  
- All project files are in the `Scripts/` folder inside the project directory 

        1. Open terminal and make sure you are in the 'Scripts` folder so cd /path/to/notworking-irc/Scripts. You can check by typing: 
        % ls
        You should see the project files like tcp_server.py and tcp_client.py
    
        2. Start the server by running in the terminal: 
            % python3 tcp_server.py -p 65432 -d 1
    
        You should see the message:
        TCP server listening on 127.0.0.1 : 65432
       
        3. Open another terminal window (or a split terminal) to run the client. You can run multiple clients in different windows to test multiple users:
            %python3 tcp_client.py
    
        4. After starting, the client will display the help menu with all available commands. You should see:
            Guest>
    
        Note: use /help in the client for a full list of commands at any time.
    
        5. Connect the client to the server:
            Guest> /connect 127.0.0.1 65432
       
        You should see confirmation that the client connected successfully, along with a default nickname message.
    
        6. Change your nickname if desired, for exmaple:  
            /nick kelly 
       
        7. Open more terminal windows to create up to 4 clients, and assign each a unique nickname.
    
        8. To see all channels and the number of users in each, type:
            /list
       
        9. To join a channel, type:
            /join <channel_name>
       
        10. To chat, just type any message in the client window and users in the same channel will see your messages with their nicknames.
    
        11. To leave a channel:  
            /leave <channel_name>
        
        12. To switch to a different channel: 
            /join <new_channel_name>
        
        13. To disconnect the client:    
            /quit
        
        14. To shut down the server manually, press `Ctrl+C`. If idle for 3 minutes, the server will automatically shut down.



## Testing

    1. First we made sure the client could connect to the server and receive a default nickname. Also implemented ANSI color enhancements in the terminal and made sure the colors were visible in the terminal.

    2. Then we ensured that all commands in the help menu (/connect, /nick, /list, /join, /leave, /quit) worked correctly without errors one by one.

    3. We opened multiple client windows (up to 4) to simulate different users. Checked that messages broadcasted correctly within channels. 

    4. Then we debugged /join and /leave to ensure proper channel switching.

    5. Tested shutting down the server with Ctrl-C and verified automatic shutdown after 3 minutes of inactivity.

    6. Tested new ANSI colors changes by sending messages to confirm visibility in the terminal.

    7. Logging was the last feature we fixed, we faced several issues along the way but eventually ensured that server events and user activities were properly recorded.

    ~testing was primarily done locally, using multiple terminal sessions 

## Observations and Reflection
Our development process was highly collaborative and flexible. We mainly communicated via Discord, using both voice calls and text chat to share tasks, ask questions, and provide updates. Each team member was very responsive, helpful, and cooperative, ensuring that progress moved smoothly. No tasks were permanently assigned; everyone helped wherever needed.

-Kelly: initial client-server connection setup and ANSI color starter

-Jonathan: client interface and user interaction, testing

-Tina: server-client object protocol, channel/user classes, testing

-Mumo: logging, terminal enhancements, demo

It was easy to ask for help and receive guidance, and we were able to reassign tasks if needed based on comfort and expertise. Each member contributed to debugging, testing, and refining features, and we often updated each other on our progress. This strong communication and willingness to assist one another made the team highly dependable and allowed us to overcome challenges efficiently.

