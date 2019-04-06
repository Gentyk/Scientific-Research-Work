from django.conf.urls import url

from analyse.views import *

urlpatterns = [
    url('info/$', InfoView.as_view()),  # горячие клавиши для перехода на другие страницы
    url('users/$', UsersView.as_view(), name="users"),
    url('base/$', BaseView.as_view(), name="database"),
    url('analyse/$', AnalyseView.as_view(), name="analyse"),
    url('analyse2/$', AnalyseView2.as_view(), name="analyse2"),
    url('vectors/$', VectorsView.as_view(), name="vectors"),
    url('patterns/$', PatternsView.as_view(), name="patterns"),
    url('ML/$', MLView.as_view(), name="ML"),
    url('MLCombine/$', CombineML.as_view(), name="CombineML"),
]