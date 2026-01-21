import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pytesseract
from PIL import Image
import io

class ReceiptProcessor:
    """Process scanned receipts using OCR and extract structured data"""

    def __init__(self):
        self.store_patterns = {
            'walmart': r'walmart|wal-mart',
            'kroger': r'kroger',
            'target': r'target',
            'costco': r'costco',
            'whole foods': r'whole\s*foods',
            'trader joe': r'trader\s*joe',
            'safeway': r'safeway',
            'publix': r'publix',
            'albertsons': r'albertsons',
            'aldi': r'aldi',
        }

    def process_image(self, image_data: bytes) -> Dict:
        """Process receipt image and extract data"""
        try:
            image = Image.open(io.BytesIO(image_data))
            # Preprocess image for better OCR
            image = self._preprocess_image(image)
            # Extract text using OCR
            text = pytesseract.image_to_string(image)
            return self.parse_receipt_text(text)
        except Exception as e:
            raise ValueError(f"Failed to process image: {str(e)}")

    def _preprocess_image(self, image: Image) -> Image:
        """Preprocess image for better OCR results"""
        # Convert to grayscale
        image = image.convert('L')
        # Resize if too small
        if image.width < 1000:
            ratio = 1000 / image.width
            new_size = (1000, int(image.height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        return image

    def parse_receipt_text(self, text: str) -> Dict:
        """Parse receipt text and extract structured data"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        store_name = self._extract_store_name(text)
        purchase_date = self._extract_date(text)
        items = self._extract_items(lines)
        total, tax = self._extract_totals(text)

        return {
            'store_name': store_name,
            'purchase_date': purchase_date,
            'items': items,
            'total_amount': total,
            'tax_amount': tax,
            'raw_text': text
        }

    def _extract_store_name(self, text: str) -> str:
        """Extract store name from receipt text"""
        text_lower = text.lower()
        for store, pattern in self.store_patterns.items():
            if re.search(pattern, text_lower):
                return store.title()
        return "Unknown Store"

    def _extract_date(self, text: str) -> Optional[datetime]:
        """Extract purchase date from receipt text"""
        # Common date patterns
        patterns = [
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',  # MM/DD/YYYY or MM-DD-YY
            r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})',    # YYYY-MM-DD
            r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{2,4})',  # DD Mon YYYY
        ]

        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                date_str = match.group(1)
                # Try to parse the date
                for fmt in ['%m/%d/%Y', '%m-%d-%Y', '%m/%d/%y', '%m-%d-%y',
                           '%Y-%m-%d', '%Y/%m/%d', '%d %b %Y', '%d %B %Y']:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue

        # Default to current date if not found
        return datetime.now()

    def _extract_items(self, lines: List[str]) -> List[Dict]:
        """Extract items with prices from receipt lines"""
        items = []

        # Pattern to match item lines with prices
        # Examples: "BANANAS  1.99", "MILK 2 @ 3.99  7.98", "BREAD  $2.50"
        price_pattern = r'[\$]?\s*(\d+\.\d{2})\s*$'
        quantity_pattern = r'(\d+)\s*@\s*[\$]?(\d+\.\d{2})'

        for line in lines:
            # Skip common non-item lines
            if any(skip in line.lower() for skip in ['total', 'subtotal', 'tax', 'balance',
                                                       'payment', 'change', 'visa', 'mastercard',
                                                       'cash', 'credit', 'debit', '***', '---',
                                                       'thank you', 'receipt', 'store', 'date']):
                continue

            # Check for quantity @ price pattern
            qty_match = re.search(quantity_pattern, line)
            if qty_match:
                quantity = float(qty_match.group(1))
                unit_price = float(qty_match.group(2))
                total_price = quantity * unit_price
                name = re.sub(quantity_pattern, '', line).strip()

                if name and len(name) > 2:
                    items.append({
                        'name': self._clean_item_name(name),
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'total_price': total_price
                    })
                continue

            # Check for simple price pattern
            price_match = re.search(price_pattern, line)
            if price_match:
                price = float(price_match.group(1))
                name = re.sub(price_pattern, '', line).strip()

                # Filter out invalid items
                if name and len(name) > 2 and price > 0:
                    items.append({
                        'name': self._clean_item_name(name),
                        'quantity': 1.0,
                        'unit_price': price,
                        'total_price': price
                    })

        return items

    def _clean_item_name(self, name: str) -> str:
        """Clean and normalize item names"""
        # Remove extra spaces, special characters, and common codes
        name = re.sub(r'\s+', ' ', name)
        name = re.sub(r'[^\w\s-]', '', name)
        name = name.strip()
        return name.title()

    def _extract_totals(self, text: str) -> Tuple[float, float]:
        """Extract total and tax amounts from receipt"""
        total = 0.0
        tax = 0.0

        # Pattern for total
        total_pattern = r'(?:total|amount due|balance)[\s:]*[\$]?\s*(\d+\.\d{2})'
        total_match = re.search(total_pattern, text.lower())
        if total_match:
            total = float(total_match.group(1))

        # Pattern for tax
        tax_pattern = r'(?:tax|sales tax)[\s:]*[\$]?\s*(\d+\.\d{2})'
        tax_match = re.search(tax_pattern, text.lower())
        if tax_match:
            tax = float(tax_match.group(1))

        return total, tax
