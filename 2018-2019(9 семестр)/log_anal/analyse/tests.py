import requests

from django.test import TestCase, Client

from base.analys import Main
from ML.create_vectors import CreateVectors
from ML.create_vectors_in_two_files import CreateVectorsApart


class Test1(TestCase):
    client = Client()

    def test1(self):
        pass