from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.
class Item(models.Model):
    name = models.CharField(max_length=255, null=False, blank=False, db_index=True)
    stockQuantity = models.PositiveIntegerField(blank=False, null=False, default=0)
    price = models.FloatField(blank=False, null=False, validators=[MinValueValidator(0.01)], db_index=True)
    type = models.CharField(max_length=50, blank=True, null=False, default="", db_index=True)
    limit = models.IntegerField(default=10)
    image = models.ImageField(upload_to='items', default='')
    note = models.CharField(max_length=255, null=False, blank=True, default='')
    isActive = models.BooleanField(default=True, db_index=True)
    buyPrice = models.FloatField(blank=False, null=False, validators=[MinValueValidator(0.01)], db_index=True)
    tva = models.BooleanField(default=False, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['type']),
            models.Index(fields=['isActive']),
        ]

    def __str__(self):
        return f"{self.name} {self.type}"
    
class Source(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="sources", db_index=True)
    name = models.CharField(max_length=255, null=False, blank=False)
    price = models.FloatField(blank=False, null=False, validators=[MinValueValidator(0.01)])
    isActive = models.BooleanField(default=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['item']),
            models.Index(fields=['isActive']),
        ]
        
    def __str__(self):
        return f"Source: {self.name} for {self.item.name}: ${self.price}"
    