import vk_api
import requests


session = requests.Session()
login, password = '89157764354', '#Valentin123'
vk_session = vk_api.VkApi(login, password)
try:
    vk_session.auth(token_only=True)
except vk_api.AuthError as error_msg:
    print(error_msg)
vk = vk_session.get_api()
import datetime
vk.messages.send(
    user_id=313308205,
    message='hellow',
    random_id=121
)
