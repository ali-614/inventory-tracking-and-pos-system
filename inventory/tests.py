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

class CartonConversionTest(TestCase):
    def setUp(self):
        self.warehouse = Location.objects.create(name="Warehouse")
        self.shop = Location.objects.create(name="Shop")
        self.product = Product.objects.create(name="Ribbon", category="Ribbons")
        self.variant = Variant.objects.create(
            product=self.product, color="Red", size="20mm",
            reference_number="RIB-1", price=500, pieces_per_carton=10
        )
        StockEntry.objects.create(variant=self.variant, location=self.warehouse, quantity=100)

    def test_carton_transfer_converts_to_pieces(self):
        self.client.post("/transfer/", {
            "variant": self.variant.id,
            "source": self.warehouse.id,
            "destination": self.shop.id,
            "quantity": 2,
            "unit": "cartons",
        })
        warehouse_entry = StockEntry.objects.get(variant=self.variant, location=self.warehouse)
        shop_entry = StockEntry.objects.get(variant=self.variant, location=self.shop)
        self.assertEqual(warehouse_entry.quantity, 80)
        self.assertEqual(shop_entry.quantity, 20)

    def test_carton_transfer_rejected_for_piece_only_variant(self):
        piece_only = Variant.objects.create(
            product=self.product, color="Blue", size="10mm",
            reference_number="RIB-2", price=300
        )
        StockEntry.objects.create(variant=piece_only, location=self.warehouse, quantity=50)
        self.client.post("/transfer/", {
            "variant": piece_only.id,
            "source": self.warehouse.id,
            "destination": self.shop.id,
            "quantity": 2,
            "unit": "cartons",
        })
        warehouse_entry = StockEntry.objects.get(variant=piece_only, location=self.warehouse)
        self.assertEqual(warehouse_entry.quantity, 50)