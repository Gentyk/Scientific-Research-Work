from django.conf.urls import url

from analyse.views import UserView, UsersView, BaseView, AnalyseView

urlpatterns = [
    url('user/$', UserView.as_view()),
    url('users/$', UsersView.as_view()),
    url('base/$', BaseView.as_view()),
    url('analyse/$', AnalyseView.as_view()),
]