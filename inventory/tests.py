from django.test import TestCase
from .models import Product, Variant
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
        