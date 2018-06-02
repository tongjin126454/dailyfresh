from apps.goods import views
from django.conf.urls import  url


urlpatterns = [

    url(r'^index$',views.index ,name='index'),
  # 购物车模块

]
