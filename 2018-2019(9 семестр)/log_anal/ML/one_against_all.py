import numpy as np

from analyse.models import Log
from ML import create_vectors_in_two_files

class VectorsOneAgainst(create_vectors_in_two_files.CreateVectorsApart):
    def __init__(self, name):
        super(VectorsOneAgainst, self).__init__(name)
        self.url_matrix = {}

    def get_maps(self, type_obj, name):
        objects = [i[0] for i in Log.objects.filter(username=name).values_list(type_obj)]
        url_matrix = {}
        type_obj = 'url'
        names = [url for url in objects if url in self.urls]
        for url in names:
            outfile = "..\\users\\"+name+"\\"+type_obj+" "+name+str(self.urls.index(url) + 1)
            url_matrix['url'] = np.load(outfile)

        domain_matrix = {}
        type_obj = 'domain'
        names = [domain for domain in objects if domain in self.domains]
        for domain in names:
            outfile = "..\\users\\" + name + "\\" + type_obj + " " + name + str(self.domains.index(domain) + 1)
            domain_matrix['domain'] = np.load(outfile)