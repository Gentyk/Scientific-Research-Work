from django.test import TestCase

from analys import Analyst
from analyse.models import Log

NAME = 'valli'


class Test1(TestCase):

    def test1(self):
        u_log = Log.objects.filter(username=NAME)
        a = Analyst(u_log, NAME)
        a.activity_analyse()
        with open('./users/otch.txt', 'w') as f:

            for k in a.result:
                s = k+": "+str(a.result[k])+"\n"
                f.writelines(s)
            #print(s)


