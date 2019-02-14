
from os import listdir
from os.path import isfile, join

from analyse.models import Log, Bigrams, Trigrams
from base.filling_the_database import Filling

#if __name__ == '__main__':
Log.objects.all().delete()
Bigrams.objects.all().delete()
Trigrams.objects.all().delete()
names = [f.split('.')[0] for f in listdir('logs') if isfile(join('logs', f))]
for name in names:
    print("Start filling %s data"%name)
    p = Filling(name)
    print("Successful filling %s data" % name)