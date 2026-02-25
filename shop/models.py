from django.db import models
import uuid

class Product(models.Model):
    product_name = models.CharField(max_length=255)
    price = models.IntegerField()

    def __str__(self):
        return self.product_name

class Transaction(models.Model):
    # Using uuid4 as standard library fallback for uuid7 requirement
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.phone_number} - {self.id}"

class ProductTransaction(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    product = models.CharField(max_length=255)
    product_count = models.IntegerField()

