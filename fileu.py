import logging
from datetime import datetime
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
    if isinstance(logger,logging.Logger):
        log = logger
    elif isinstance(logger,str):
        log = logging.getLogger(logger)
    elif isinstance(logger,type(None)):
        log = logging.getLogger('Update_User')
    else:
        log = logging.getLogger('Unknown Logger')
    if level<=10:
        log.debug(str(datetime.now().strftime("%H:%M:%S"))+' '+str(message))
    elif level==20:
        log.info(str(datetime.now().strftime("%H:%M:%S"))+' '+str(message))
    elif level==30:
        log.warning(str(datetime.now().strftime("%H:%M:%S"))+' '+str(message))
    elif level==40:
        log.error(str(datetime.now().strftime("%H:%M:%S"))+' '+str(message))
    elif level>=50:
        log.critical(str(datetime.now().strftime("%H:%M:%S"))+' '+str(message))