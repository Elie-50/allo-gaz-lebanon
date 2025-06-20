from django.db import models
from django.core.validators import RegexValidator

phone_regex = RegexValidator(
    regex=r'^\+[1-9]\d{6,14}$',
    message='Enter a valid international phone number in E.164 format (e.g., +12345678901).'
)

# Create your models here.
class Customer(models.Model):
    firstName = models.CharField(max_length=50, db_index=True)
    middleName = models.CharField(max_length=50, db_index=True)
    lastName = models.CharField(max_length=50, db_index=True)
    nickName = models.CharField(max_length=50, null=False, blank=True, default='')
    discount = models.FloatField(default=0)
    createdAt = models.DateTimeField(auto_now_add=True)
    isActive = models.BooleanField(default=True, db_index=True)
    residenceZgharta = models.BooleanField(default=False)
    residenceEhden = models.BooleanField(default=False)
    residenceTripoli = models.BooleanField(default=False)
    residenceKoura = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.firstName} {self.middleName} {self.lastName}"

    class Meta:
        unique_together = ('firstName', 'middleName', 'lastName')

class Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses', db_index=True)
    email = models.CharField(max_length=70, db_index=True)
    landline = models.CharField(max_length=40, null=False, blank=True, default='', db_index=True)
    link = models.CharField(max_length=50 ,null=False, blank=False)
    region = models.CharField(max_length=100, null=False, default="")
    street = models.CharField(max_length=100, null=False, default="")
    building = models.CharField(max_length=100, null=False, default="")
    floor = models.CharField(max_length=50, null=False, default="")
    image = models.ImageField(upload_to='addresses', null=True, blank=True)

    def __str__(self):
        return f"Address {self.id}: {self.region} {self.street} {self.building} {self.floor}"

class PhoneNumber(models.Model):
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='mobile_numbers', db_index=True)
    mobile = models.CharField(max_length=40, null=False, blank=False, default='' , validators=[phone_regex], db_index=True)
    priority = models.IntegerField()

    def __str__(self):
        return f"Phone: {self.mobile}"