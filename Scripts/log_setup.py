import logging  #importing the built in python logging 

def setupLogClient():
    '''
    Setting up the logger for the client server
    '''
    logging.basicConfig(
        filename:"client.log", 
        level=logging.INFO, 
        format"%(asctime)s - %(levelname)s - %(message)s"
    )
