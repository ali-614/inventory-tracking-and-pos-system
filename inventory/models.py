from django.db import models

# Create your models here.
class Location(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Varient(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='varients')
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=50)
    reference_number = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10,decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.color} - {self.size}"
    

class StockEntry(models.Model):
    varient = models.ForeignKey(Varient, on_delete=models.CASCADE, related_name= 'stock_entries')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='stock_entries')
    quantity = models.PositiveBigIntegerField(default=0)

    class Meta:
        unique_together = ('varient', 'location')

    def __str__(self):
        return f"{self.variant} @ {self.location.name}: {self.quantity}"