from django.urls import path, include
from . import views
# from rest_framework.authtoken.views import obtain_auth_token
from django.views.generic import RedirectView

urlpatterns = [
    path('menu-items', views.MenuItemView.as_view()),
    # path('token/', obtain_auth_token),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view(), name='menuitems-detail'),
    path('cart/menu-items', views.CartView.as_view()),
    path('orders', views.OrderView.as_view()),
    path('orders/<int:pk>', views.SingleOrderView.as_view()),
    path('groups/manager/users', views.ManagersView.as_view()),
    path('groups/manager/users/<int:pk>', views.SingleManagersView.as_view()),
    path('groups/delivery-crew/users', views.DeliveryView.as_view()),
    path('groups/delivery-crew/users/<int:pk>', views.SingleDeliveryView.as_view()),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users', RedirectView.as_view(url = 'auth/users', permanent=False, http_method_names = ['post', 'get'])),
    path('users/users/me/', views.url_redirect_me),
]