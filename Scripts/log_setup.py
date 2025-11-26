import logging  #importing the built in python logging 

def setupLogClient():
    '''
    Setting up the logger for the client server
    '''
    # Logging for client
    def setupLogClient():
        logging.basicConfig(
            filename="client.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
# Logging for server
    def setupLogServer():
        logging.basicConfig(
            filename="server.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )