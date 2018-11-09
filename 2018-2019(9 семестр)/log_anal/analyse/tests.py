from django.test import TestCase

from analys import Analyst
from analyse.models import Log

NAME = 'valli'


class Test1(TestCase):

    def test1(self):
        u_log = Log.objects.filter(username=NAME)
        a = Analyst(u_log, NAME)
        result = a.start_treatment()
        result.update(a.activity_analyse())
        for k in result:
            s = k+": "+str(result[k])
            print(s)


