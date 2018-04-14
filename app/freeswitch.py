from freeswitchESL import ESL
import sys
import logging
import json
import threading

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
    response = dict()
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
        response['message'] = 'error'
        response['error'] = status[1]

    else:
        uuid = status[1]

        # if call was originated then grab the uuid
        logger.info("UUID : {}".format(uuid))
        response['message'] = 'ok'
        t1 = threading.Thread(target=eventListener, args=(con,uuid,))
        t1.start()
    return response

def eventListener(con, uuid) :
        """
        Event listener on connection con with call job uuid
        """
        # play remote file through shout
        con.execute('playback', _PLAY_FILE, str(uuid))
        i=0
        con.events('plain', 'all')

        # need to listen the event and act accordingly
        while(True):
            ev = con.recvEvent();
            if ev:
                events = ev.getHeader("Event-Name")

                # if playback completed then hangup the call  
                if events == 'PLAYBACK_STOP' and ev.getHeader("Unique-ID") == str(uuid) :
                    print(ev.serialize())
                    print("Hanging up the call")
                    con.execute('hangup','', str(uuid))
                    break
                

        con.disconnect()
