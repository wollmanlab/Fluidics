import logging
from datetime import datetime
import time
import os

now = datetime.now()
day = now.day
month = now.strftime("%B")
year = now.year
time_stamp = str(year)+str(month)+str(day)

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
                    filename=os.path.join(os.path.dirname(os.path.abspath(__file__)),'Logs',time_stamp+'.log'),filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',level=20)

def update_user(message,level=20,logger=None):
    """
    update_user Send string messages to logger with various levels OF IMPORTANCE

    :param message: _description_
    :type message: str
    :param level: _description_, defaults to 20
    :type level: int, optional
    :param logger: Logger to send logs can be a name of logger, defaults to 'FileU'
    :type logger: str, logging.Logger, optional
    """
    if not isinstance(message,str):
        try:
            message = f"\n{message.to_string()}"
        except:
            message = str(message)
    # message = str(datetime.now().strftime("%H:%M:%S"))+' '+message
    print(str(datetime.now().strftime("%H:%M:%S"))+' '+message)
    if isinstance(logger,logging.Logger):
        log = logger
    elif isinstance(logger,str):
        log = logging.getLogger(logger)
    elif isinstance(logger,type(None)):
        log = logging.getLogger('Update_User')
    else:
        log = logging.getLogger('Unknown Logger')
    if level<=10:
        log.debug(message)
    elif level==20:
        log.info(message)
    elif level==30:
        log.warning(message)
    elif level==40:
        log.error(message)
    elif level>=50:
        log.critical(message)

def precise_sleep(sleep_time):
    start = time.perf_counter()
    while time.perf_counter()-start<sleep_time:
        pass
