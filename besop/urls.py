from django.urls import path, include
from shop import views

urlpatterns = [
    path('', views.about, name='about'),
    path('shop/', views.index, name='index'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('payment/', views.payment, name='payment'),
    path('quan-ly/', views.admin_transactions, name='admin_transactions'),
    path('quan-ly/export/', views.extract_revenue_report_excel, name='extract_revenue_report_excel'),
    path('quan-ly/add-product/', views.add_product, name='add_product'),
    path('quan-ly/edit-product/<int:pk>/', views.edit_product, name='edit_product'),
    path('quan-ly/products/', views.admin_products, name='admin_products'),
    path('quan-ly/delete-product/<int:pk>/', views.delete_product, name='delete_product'),
    path('transaction/revert/<uuid:transaction_id>/', views.revert_transaction, name='revert_transaction'),
    path('transaction/delete/<uuid:transaction_id>/', views.delete_transaction, name='delete_transaction'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
        path('user/', include('user.urls')),
    ]
    
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    