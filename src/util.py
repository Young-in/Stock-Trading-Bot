import pandas as pd
import numpy as np
import os
import datetime
import pytz
import re


def isIterable(value):
    """
    Check if value is iterable
    if value is iterable, it returns True. 
    """
    try:
        iter(value)
        return True
    except:
        return False

def isFileExist(file_name):
    """
    Check if file( or directory) exists
    if file exists, it returns True.
    """
    return os.path.exists(file_name)

def getLocalTime(area = "Asia/Seoul"):
    """
    Return local time whose format is "Year-Month-Day Hour:Minute:Second"
    Default area is seoul.
    UTC clock(?) is based on UK, so we need to localize clock.
    """
    KST = pytz.timezone(area)
    now = datetime.datetime.now(tz=KST)
    return now
