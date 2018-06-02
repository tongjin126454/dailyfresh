from apps.user.views import RegisterView,ActiveView,LoginView

from django.conf.urls import  url


urlpatterns = [
    url(r'^register$',RegisterView.as_view(),name='register'),
    url(r'^active/(?P<token>.*)$',ActiveView.as_view(),name='active'),
    url(r'^login$',LoginView.as_view(),name='login'),
    # url(r'^register_handle',views.register_handle,name='register_handle'),

  # 购物车模块

]
