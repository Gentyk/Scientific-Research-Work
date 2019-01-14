import vk
import time
import numpy as np

# те id, которые ты не хочешь чтобы чекались (не забудь сюда вписать свой - если ты себе что-то посылала)
execute = []

# начинаем сессию
session = vk.Session(access_token='<your token>')
vkapi = vk.API(session)
APIVersion =  5,92

# смотрим сколько у нас вообще есть диалогов с пользователями
a = vkapi('messages.getConversations', v=APIVersion)
n = a['count']
if n > 150:
    mass = [150*(i + 1) for i in range(n // 150)]
    mass.append(n % 150)
else:
    mass = [n]
# и среди этих диалогов выбираем только те, которые непубличные (один-на-один); из этих диалогов выписываем id пользователей
# и убираем исключания
users_id = []
offset = 0
for num in mass:
    time.sleep(0.4)
    a = vkapi('messages.getConversations', offset=offset, count=num, v=APIVersion)
    for nigger in a['items']:
        if nigger['conversation']['peer']['type'] == 'user' and not nigger['conversation']['peer']['id'] in execute:
            users_id.append(nigger['conversation']['peer']['id'])
    offset = num

# смотрим сколько диалогов с другими пользователями получилось
users_id = list(set(users_id))
print(len(users_id))

# чекаем диалог с каждым пользователем по отдельности
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


# смотрим сколько в итоге нормальных диалогов получилось и формируем отчеты
print(len(result))
path = 'otch.npy'
np.save(path, result)
path = 'otch.txt'
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




