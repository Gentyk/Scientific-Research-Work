from django.conf.urls import url

from analyse.views import GrammsView, UserView, LogView

urlpatterns = [
    url('user/', UserView.as_view()),
    url('log/', LogView.as_view()),
    url('gramms/', GrammsView.as_view()),
]