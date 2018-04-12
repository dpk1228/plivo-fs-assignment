from freeswitchESL import ESL
import sys
import logging
import json

logger = logging.getLogger(__name__)


_HOST = 'localhost'
_ESL_PORT = '8021'
_PWD = 'ClueCon'

# originate argument
_ORIG_ARG = "user/{} &park()" 

# remote mp3 file to play 
_PLAY_FILE = "shout://s3.amazonaws.com/plivocloud/Trumpet.mp3"


def get_connection():
    """
    function to create and return ESL connection object
    """
    con = ESL.ESLconnection(_HOST, _ESL_PORT, _PWD)

    if not con.connected():
        logger.warning("Check You Connection !!!")
        return False

    return con

def originate_call(dest):
    """
    Function to originate call and play remote mp3 file
    : param dest: destination number to call

    response : 'ok' or 'error'
    """
    # get the connection object
    con = get_connection()
    if not con:
        # in no connection is created return with error
        return "error" 
    # api to originate call
    call = con.api("originate", _ORIG_ARG.format(dest))
    call_status = call.serialize("json")
    status = json.loads(call_status)
    status = status.get('_body').strip().split(' ')
    logger.info(status)
    if status[0] != '+OK':
    	return "error"
    else:
        # if call was originated then grab the uuid
        uuid = status[1]
        logger.info("UUID : {}".format(uuid))
        # play remote file through shout
        play_res = con.execute('playback', _PLAY_FILE, str(uuid))
    con.disconnect()
    return "ok"

