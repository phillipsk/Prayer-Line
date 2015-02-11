# Prayer Coordinator/Speaker pin number [enabled after pressing 7 form the initial main menu]
pin_number = '8824'

# Plivo API settings
PLIVO_AUTH_ID = 'MAMTDMMJZKMJQ0YJRMMW'
PLIVO_TOKEN = 'N2RkNDgzM2I3M2JmZjk0YWU5Yzc2OTEyMDJiYTA4'

# *Plivo* from number
from_number = '+16176583908'
to_number = '16178070291'


try:
    from local_settings import *
except ImportError:
    pass
