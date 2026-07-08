from django.test import TestCase
from .models import Product, Variant, Location, StockEntry, Transfer
from django.core.exceptions import ValidationError
# Create your tests here.

class BarcodeGenerationTest(TestCase):
    def test_barcode_auto_generated(self):
        product = Product.objects.create(name="Test Zipper", category = "Zippers")
        variant = Variant.objects.create(
            product=product,
            color="Green",
            size="10cm",
            reference_number="TEST-REF-001",
            price=100
        )
        self.assertTrue(variant.barcode.startswith("BAR-"))
        
class TransferTest(TestCase):
    def setUp(self):
        self.warehouse = Location.objects.create(name="Warehouse")
        self.shop = Location.objects.create(name="Shop")
        self.product = Product.objects.create(name="Test Zipper", category="Zippers")
        self.variant = Variant.objects.create(
            product=self.product, color="Red", size="M",
            reference_number="T-REF-1", price=100
        )
        StockEntry.objects.create(variant=self.variant, location=self.warehouse, quantity=100)

    def test_valid_transfer_moves_stock(self):
        transfer = Transfer.objects.create(
            variant=self.variant, source=self.warehouse,
            destination=self.shop, quantity=30
        )
        transfer.execute()

        warehouse_entry = StockEntry.objects.get(variant=self.variant, location=self.warehouse)
        shop_entry = StockEntry.objects.get(variant=self.variant, location=self.shop)

        self.assertEqual(warehouse_entry.quantity, 70)
        self.assertEqual(shop_entry.quantity, 30)

    def test_transfer_exceeding_stock_is_rejected(self):
        transfer = Transfer.objects.create(
            variant=self.variant, source=self.warehouse,
            destination=self.shop, quantity=500
        )
        with self.assertRaises(ValidationError):
            transfer.execute()

        warehouse_entry = StockEntry.objects.get(variant=self.variant, location=self.warehouse)
        self.assertEqual(warehouse_entry.quantity, 100)