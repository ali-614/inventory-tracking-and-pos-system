from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
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

class Variant(models.Model):
    
    def save(self, *args, **kwargs):
        super().save(*args,**kwargs)
        if not self.barcode:
            self.barcode = f"BAR-{self.id:06d}"
            super().save(update_fields=['barcode'])

    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=50)
    reference_number = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=50, unique=True,blank=True)
    price = models.DecimalField(max_digits=10,decimal_places=2)

    pieces_per_carton = models.PositiveBigIntegerField(null = True, blank=True, validators = [MinValueValidator(1)])

    def __str__(self):
        return f"{self.product.name} - {self.color} - {self.size}"
    

class StockEntry(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name= 'stock_entries')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='stock_entries')
    quantity = models.PositiveBigIntegerField(default=0)

    class Meta:
        unique_together = ('variant', 'location')
        verbose_name_plural = "Stock entries"

    def carton_display(self):
        if not self.variant.pieces_per_carton:
            return "--"
        cartons = self.quantity/self.variant.pieces_per_carton
        return f"{cartons:g} cartons"
    carton_display.short_description = "Cartons"
    
    def __str__(self):
        return f"{self.variant} @ {self.location.name}: {self.quantity}"

class Transfer(models.Model):
        variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name='transfers')
        source = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='transfers_out')
        destination = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='transfers_in')
        quantity = models.PositiveIntegerField()
        created_at = models.DateTimeField(auto_now_add=True)

        def execute(self):
            source_entry = StockEntry.objects.filter(variant = self.variant, location = self.source).first()
            if source_entry is None or source_entry.quantity < self.quantity:
                raise ValidationError("Not enough stock at the source location")
            
            with transaction.atomic():
                source_entry.quantity -= self.quantity
                source_entry.save()

                destination_entry, created = StockEntry.objects.get_or_create(
                    variant=self.variant,
                    location= self.destination,
                    defaults={'quantity':0}
                )
                destination_entry.quantity += self.quantity
                destination_entry.save()

        def __str__(self):
            return f"{self.quantity} x {self.variant} : {self.source.name} → {self.destination.name}"
