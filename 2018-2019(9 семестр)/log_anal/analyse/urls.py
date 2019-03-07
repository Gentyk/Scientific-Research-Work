from django.conf.urls import url

from analyse.views import UserView, UsersView, BaseView, AnalyseView, InfoView

urlpatterns = [
    url('info/$', InfoView.as_view()),
    url('user/$', UserView.as_view()),
    url('users/$', UsersView.as_view(), name="users"),
    url('base/$', BaseView.as_view(), name="database"),
    url('analyse/$', AnalyseView.as_view(), name="analyse"),
]