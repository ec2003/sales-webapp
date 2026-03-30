from django.db import models
import uuid

class Product(models.Model):
    product_name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return self.product_name

class Transaction(models.Model):
    # Using uuid4 as standard library fallback for uuid7 requirement
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    is_confirmed = models.BooleanField(default=False)
    revenue = models.IntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return f"{self.phone_number} - {self.id}"
    
    def save(self, *args, **kwargs):
        if self.is_confirmed and self.revenue == 0:
            total_revenue = 0
            for pt in self.producttransaction_set.all():
                total_revenue += pt.product_count * pt.product.price
            if Transaction.objects.count() <= 100:
                total_revenue *= 0.7
            self.revenue = total_revenue
        super().save(*args, **kwargs)
class ProductTransaction(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE)
    product_count = models.IntegerField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product} x {self.product_count}, Transaction: {self.transaction.id}"
    
