from django.contrib import admin
from .models import Product, Transaction, ProductTransaction
# Register your models here.
admin.site.register(Product)
admin.site.register(Transaction)
admin.site.register(ProductTransaction)