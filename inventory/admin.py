from django.contrib import admin

# Register your models here.
from .models import Product, Variant, Location, StockEntry

class VarientInLine(admin.TabularInline):
    model = Variant
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "category"]
    search_fields = ["name"]
    inlines = [VarientInLine]

class VariantAdmin(admin.ModelAdmin):
    list_display = ["__str__", "reference_number", "barcode", "price"]
    search_fields = ["reference_number", "barcode"]
    list_filter = ["color"]

admin.site.register(Product,ProductAdmin)
admin.site.register(Variant, VariantAdmin)
admin.site.register(Location)
admin.site.register(StockEntry)