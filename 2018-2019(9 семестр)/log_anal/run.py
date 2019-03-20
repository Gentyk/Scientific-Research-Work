from analyse.models import Log

names = [name[0] for name in Log.objects.distinct('username').values_list('username')]
for name in names:
    log = Log.objects.filter(username=name)
    n = log.count()
    # error = log.filter(domain_type='page error').count() + log.filter(domain_type='not determined').count()
    # other = log.filter(domain_type='other').count()
    error = log.filter(domain_category='not determined').count()
    print(name + " " + str(error/n))