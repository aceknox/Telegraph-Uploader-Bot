import os

class Config(object):
     #updates channel
     UPDATES_CHANNEL = os.environ.get("UPDATES_CHANNEL","-1001509464345")
     LOG_CHANNEL = os.environ.get("LOG_CHANNEL","-1001834539520")
