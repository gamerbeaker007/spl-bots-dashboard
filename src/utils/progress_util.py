import logging

from src.configuration import progress


def set_daily_title(title):
    progress.progress_daily_title = title


def update_daily_msg(msg, error=False, log=True):
    if log:
        if error:
            logging.error(msg)
        else:
            logging.info(msg)
    progress.progress_daily_txt = msg
