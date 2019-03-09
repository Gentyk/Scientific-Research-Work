from datetime import datetime

from django.db.models import F

NUMBER_FREQUENT_URL = 20
NUMBER_FREQUENT_DOMAINS = 20
WIDTH = 32*5
HEIGHT = 18*5


class Analyst(object):
    def __init__(self, log, bi_log, tri_log, username, finish_time):
        self.log = log
        self.bi = bi_log
        self.tri = tri_log
        self.username = username
        self.finish_time = finish_time
        self.seance = log.values("seance").distinct().count()
        self.n_clicks = self.log.filter(start_computer=False).count()
        self.result = {}

    # последовательный анализ лога по пуктам
    def activity_analyse(self):
        # частые объекты
        all_urls = [url[0] for url in self.log.values_list('url').distinct()]
        self.result['частые url'] = self._get_frequent_objects_list(all_urls, 'url', NUMBER_FREQUENT_URL)
        all_domains = [domain[0] for domain in self.log.values_list('domain').distinct()]
        self.result['частые домены'] = self._get_frequent_objects_list(all_domains, 'domain', NUMBER_FREQUENT_DOMAINS)

        # n-граммы
        self.result['url биграммы'] = self._bigramm('url1', 'url2')
        self.result['domain биграммы'] = self._bigramm('domain1', 'domain2')
        self.result['type биграммы'] = self._bigramm('type1', 'type2')
        self.result['category биграммы'] = self._bigramm('category1', 'category2')
        self.result['url триграммы'] = self._trigramm('url1', 'url2', 'url3')
        self.result['domain триграммы'] = self._trigramm('domain1', 'domain2', 'domain3')
        self.result['type триграммы'] = self._trigramm('type1', 'type2', 'type3')
        self.result['category триграммы'] = self._trigramm('category1', 'category2', 'category3')

    # Пункт 0: самые общие данные о логе
    def start_treatment(self):
        # самая общая информация о логе, которая могла вас интересовать
        self.result['всего записей'] = self.n_clicks
        start = self.log.earliest('time').time
        end = self.log.latest('time').time
        time = end - start
        self.result['длительность снятия данных'] = str(time)
        self.result['начало записи лога'] = str(start)
        self.result['конец записи лога'] = str(end)
        self.result['количество сеансов'] = self.seance

    # возвращает массив частых объектов
    def _get_frequent_objects_list(self, obj_list, obj_type, numbers):
        mass = []
        objects = {}
        for object in obj_list:
            d = {obj_type: object}
            n = self.log.filter(**d).count()
            if not n in mass:
                mass.append(n)
            if n in objects:
                objects[n].append(object)
            else:
                objects[n] = [object]
        mass.sort(reverse=True)
        mass = mass[:numbers]
        r1 = []
        for n in mass:
            for object in objects[n]:
                r1.append(object)
                if len(r1) >= 20:
                    r1 = r1[:20]
                    break
            if len(r1) >= 20:
                r1 = r1[:20]
                break
        return r1

    def _bigramm(self, column1, column2):
        bi_gramms = {}
        a = self.bi.only(column1, column2).exclude(**{column1: F(column2)}).distinct(column1, column2).values_list(column1, column2)
        mass = []
        for data in a:
            n = self.bi.only(column1, column2).filter(**{column1: data[0]}).filter(**{column2: data[1]}).count()
            if n in bi_gramms:
                bi_gramms[n].append((data[0], data[1]))
            else:
                bi_gramms[n] = [(data[0], data[1])]
            if n not in mass:
                mass.append(n)
        mass.sort(reverse=True)
        mass = mass[:15]
        result_bi_gramms = []
        for n in mass:
            for objs in bi_gramms[n]:
                result_bi_gramms.append(tuple([objs[0], objs[1]]))
                if len(result_bi_gramms) >= 15:
                    break
            if len(result_bi_gramms) >= 15:
                break
        return result_bi_gramms,

    def _trigramm(self, col1, col2, col3):
        th_gramms = {}
        a = self.tri.only(col1, col2, col3).distinct(col1, col2, col3).values_list(col1, col2, col3)
        mass = []
        for data in a:
            n =  self.tri.only(col1, col2, col3).filter(**{col1: data[0]}).filter(**{col2: data[1]}).filter(**{col3: data[2]}).count()
            if n in th_gramms:
                th_gramms[n].append((data[0], data[1], data[2]))
            else:
                th_gramms[n] = [(data[0], data[1], data[2])]
            if n not in mass:
                mass.append(n)
        mass.sort(reverse=True)
        mass = mass[:10]
        result_gramms = []
        for n in mass:
            for data in th_gramms[n]:
                result_gramms.append(tuple([data[0], data[1], data[2]]))
                if len(result_gramms) >= 10:
                    break
            if len(result_gramms) >= 10:
                break
        return result_gramms


def check_logfile(name):
    with open('.\\logs\\' + name + '.txt') as file:
        data = [line for line in file]

    old_time = None
    for line_d in data:
        try:
            line = line_d.split('\t')
            time = datetime.strptime(line[0], '%d.%m.%Y')
            if old_time and time < old_time:
                msg = "error:" + str(old_time) + " - " + str(time)
                return msg
            else:
                old_time = time
        except ValueError:
            pass
    return "+"