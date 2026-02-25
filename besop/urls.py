from django.urls import path, include
from shop import views

urlpatterns = [
    path('', views.index, name='index'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('payment/', views.payment, name='payment'),
    path('quan-ly/', views.admin_transactions, name='admin_transactions'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('user/', include('user.urls')),
]