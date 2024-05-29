import logging as log
import os
file = "/tmp/texp/tmp.log"
if not os.path.exists(os.path.split(file)[0]):
    os.makedirs(os.path.split(file)[0], exist_ok=True,)
log.basicConfig(filename=file, filemode="w", level=log.DEBUG)
