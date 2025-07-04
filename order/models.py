from django.db import models
from customer.models import Customer, Address
from item.models import Item
from user.models import User

# Create your models here.
class Order(models.Model):
    # Choices for money type
    USD = 'USD'
    LBP = 'LBP'
    CURRENCY_CHOICES = [
        (USD, 'USD'),
        (LBP, 'LBP'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders_made')
    driver = models.ForeignKey(User, on_delete=models.PROTECT, related_name='orders_delivered')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='orders')
    quantity = models.PositiveIntegerField()
    discount = models.FloatField(default=0)
    status = models.CharField(max_length=1, default='P')
    money = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='orders')
    customerNotes = models.TextField(null=False, blank=True, default='')
    driverNotes = models.TextField(null=False, blank=True, default='')
    liraRate = models.IntegerField()
    orderedAt = models.DateTimeField(auto_now_add=True, db_index=True)
    deliveredAt = models.DateTimeField(null=True, blank=True, db_index=True)
    isActive = models.BooleanField(default=True, db_index=True)

    def __str__(self):
        return f"{self.item.name} for address {self.address.id}"

class ExchangeRate(models.Model):
    rate = models.FloatField(default=89000)

class BackupDate(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

class Receipt(models.Model):
    orders = models.ManyToManyField(Order)
    file = models.FileField(upload_to='receipts')