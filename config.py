import os

class Config(object):
     #updates channel
     UPDATES_CHANNEL = os.environ.get("UPDATES_CHANNEL",)
