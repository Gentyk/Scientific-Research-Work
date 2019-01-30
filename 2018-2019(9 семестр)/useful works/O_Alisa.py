"""
Код занимается импортом переписок из контакта
"""
import vk
import time
import numpy as np

# собираем id-шники, которые не хотим выкачивать в массивы
# у меня уже были собранные некоторые данные - я их добавил в исключение для нового пользователя
r_dict = np.load('otch.npy').item()
execute = list(r_dict.values())
r_dict2 = np.load('otch2.npy').item()
execute2 = list(r_dict2.values())
execute += execute2
execute += [313308205] # ну, и вручную тоже можно добавлять

# подключаемся к сессии
session = vk.Session(access_token='ваш токен')
vkapi = vk.API(session)


APIVersion =  5,92
#dialogs = vkapi('messages.getDialogs', user_id=137403092, v=APIVersion)
# смотрим сколько у нас вообще есть диалогов с пользователями
a = vkapi('messages.getConversations', v=APIVersion)
n = a['count']
if n > 150:
    data = [(150 * i, 150) for i in range(n // 150)]
    data.append(((n // 150) * 150, n % 150))
else:
    data = [(0, n)]
# и среди этих диалогов выбираем только те, которые непубличные (один-на-один); из этих диалогов выписываем id пользователей
# и убираем исключания
users_id = []
for offset, count in data:
    time.sleep(0.4)
    a = vkapi('messages.getConversations', offset=offset, count=count, v=APIVersion)
    for nigger in a['items']:
        if nigger['conversation']['peer']['type'] == 'user' and not nigger['conversation']['peer']['id'] in execute:
            users_id.append(nigger['conversation']['peer']['id'])

users_id = list(set(users_id))
print(len(users_id))

result = {}
for user in users_id:
    time.sleep(0.4)
    friend_dialog = vkapi('messages.getDialogs', user_id=user, v=APIVersion)

    dialog_len_max = friend_dialog['count']
    if dialog_len_max < 40:
        continue
    dialog_len = (dialog_len_max if dialog_len_max < 200 else 200)
    time.sleep(0.4)
    messages = vkapi('messages.getHistory',
                            user_id=user,
                            count=dialog_len,
                            v=APIVersion
                           )
    text_messages = []
    for message in messages['items']:
        if message['from_id'] == user and message['body'] != "":
            text_messages.append(message['body'])
        if len(text_messages) >= 25:
            break

    if len(text_messages) < 25 and dialog_len_max > dialog_len:
        while dialog_len_max > dialog_len:
            offset = dialog_len+1
            dialog_len = (dialog_len + 200 if dialog_len + 200 <= dialog_len_max else dialog_len_max)
            time.sleep(0.4)
            messages = vkapi('messages.getHistory',
                             offset=offset,
                             user_id=user,
                             count=dialog_len,
                             v=APIVersion
                             )
            for message in messages['items']:
                if message['from_id'] == user and message['body'] != "":
                    text_messages.append(message['body'])
                if len(text_messages) >= 25:
                    break
            if len(text_messages) >= 25:
                break
    if len(text_messages) >= 25:
        result[user] = text_messages.copy()

print(len(result))
path = 'otch3.npy'
np.save(path, result)
path = 'otch3.txt'
with open(path, 'w') as f:
    f.writelines(str(len(result))+"\n")
    for k, v in result.items():
        s = "\n||||||||||||||||||||||||||||||||||||||||!!!!!!!!!!!!||||||||||||||||||||||||||||\n" +str(k) + ":" + str(len(v)) + "\n"
        f.writelines(s)
        j = 0
        for i in v:
            s = "\n\nСообщение " + str(j) + ":\n" + str(i)
            j += 1
            try:
                f.writelines(s)
            except:
                f.writelines("сообщение со смайликами")