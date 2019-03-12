"""
Здесь находятся дополнительные функции, которые могут быть использованы
"""
import os
import time

from analyse.models import Teams
from ML.create_vectors_in_two_files import CreateVectorsApart
from ML.ML import classification


def create_dirname(path):
    # проверяем наличие папки для результатов и возвращаем путь
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def train_and_test(clicks, day_parts, list_permission, teams, algorithms=None, add_info_by_namedir="", action=[]):
    """
    В зависимости от режима запускает или формирование выборок, или запускает МО.
    """
    start_time = time.time()
    for team in teams:
        for day_part in day_parts:
            for n_click in clicks:
                thousand = Teams.objects.filter(team=team).values_list('thousand')[0][0]
                path = create_dirname(str(".\\dataset2\\") + str(team) + " perm " + str(list_permission) + " " + \
                                      str(day_part) + "t " + str(n_click) + "cl " + str(thousand) + add_info_by_namedir)
                names = [name[0] for name in Teams.objects.filter(team=team).values_list('username')]
                if "train" in action:
                    data = (thousand, int(thousand/0.7))
                    CreateVectorsApart(path, data, names, n_click, day_part, list_permission, team)
                if "ML" in action:
                    info = {'team': team, 'clicks': n_click, 'patterns': list_permission}
                    classification(path, names, algorithms, info)
    msg = "Завершено. Время выполнения: %s seconds ---" % (time.time() - start_time)
    print(msg)
    #messagebox.showerror("Выполнено", msg)

