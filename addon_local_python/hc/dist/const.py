# ROOT_DIR = '/data/data/com.termux/files/home/.homeassistant/'
# data_file = '/data/data/com.termux/files/home/ha_tool/data'
# CODE_FILE = '/sdcard/Download/code.txt'

# ROOT_DIR = '/Volumes/Data/Dropbox/09_home_assistant/25_Template_Deployement/.homeassistant'

# ROOT_DIR = '/Users/chinh/.homeassistant/'
# data_file = '/Volumes/Data/Dropbox/09_home_assistant/18_ha_tool/data'
# CODE_FILE = '/Volumes/Data/Dropbox/09_home_assistant/18_ha_tool/data/code.txt'

# ROOT_DIR = '/usr/share/hassio/homeassistant/'
# ROOT_DIR = '/home/iwin/.homeassistant/'
# data_file = '/media/iwin/DATA/intern/18_ha_tool/data'
# CODE_FILE = '/media/iwin/DATA/intern/18_ha_tool/data/code.txt'
# ROOT_DIR = 'C:/Users/bacht/AppData/Roaming/.homeassistant/'
# data_file = 'D:/intern/18_ha_tool/data'
# CODE_FILE = 'D:/intern/18_ha_tool/data/code.txt'

# Chạy trên 5005
# ROOT_DIR = '/usr/share/hassio/homeassistant/'
# data_file = '/usr/share/hassio/hatool/data'
# CODE_FILE = '/usr/local/etc/code.txt'

# Addons configuration
ROOT_DIR = '/config/'
data_file = '/share/hatool/data'
CODE_FILE = '/usr/local/etc/code.txt'

URL_STATE = 'http://127.0.0.1:8123/api/states'
URL_SERVICE = 'http://127.0.0.1:8123/api/services'
LOCAL_HOST = 'http://127.0.0.1'

local_ip = '127.0.0.1'

# TRIGGER_LIST = {
#     "event":{
#         "event type":[],
#         "event data": {}
#     },
#     "Geolocation":{
#         "source": [],
#         "zone": [],
#         "event": ["enter", "leave"]
#     },
#     "Home Assistant":{
#         "event": ["start", "shutdown"]
#     },
#     "mqtt":{
#         "topic": [],
#         "payload": []
#     },
#     "numeric state": {
#         "entity": "",
#         "above": [],
#         "below": [],
#         "value template": [],
#         "for": []
#     },
#     "state":{
#         "entity": "",
#         "from": [],
#         "to": [],
#         "for": []
#     },
#     "sun": {
#         "event": ["sunrise", "sunset"],
#         "offset": ["optional"]
#     },
#     "template":{
#         "value template": []
#     },
#     "time": {
#         "at": []
#     },
#     "time pattern": {
#         "hours":[],
#         "minutes": [],
#         "seconds": []
#     },
#     "webhook":{
#         "webhook_id": []
#     },
#     "zone": {
#         "entity with location": [],
#         "zone": [],
#         "event": ["enter", "leave"]
#     }
# }

# CONDITION_LIST = {

#         "numeric state": {
#             "entity": "",
#             "above": [],
#             "below": [],
#             "value template": []
#         },
#         "state":{
#             "entity": "",
#             "state": []
#         },
#         "sun":{
#             "before":["sunrise", "sunset"],
#             "before offset": [],
#             "after": ["sunrise", "sunset"],
#             "after offset": []
#         },
#         "template":{
#             "value template": []
#         },
#         "time":{
#             "after": [],
#             "before": []
#         },
#         "zone":{
#             "zone": ["zone.home"],
#             "entity with location": []
#         }
# }


# ACTION_LIST = {
#     "condition": {
#         "condition type": ["State", "Sun", "Template", "Time", "Zone"]
#     },
#     "delay":{
#         "delay": []
#     },
#     "fire event": {
#         "event": [],
#         "service data": []
#     },
#     "call service": {
#         "service": "",
#         "service data": []
#     }
# }
