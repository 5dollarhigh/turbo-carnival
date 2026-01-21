import email
import re
from datetime import datetime
from typing import Dict, List, Optional
from email import policy
from email.parser import BytesParser
from bs4 import BeautifulSoup

class EmailReceiptParser:
    """Parse email receipts (.eml files) and extract structured data"""

    def __init__(self):
        self.store_patterns = {
            'walmart': r'walmart|wal-mart',
            'amazon': r'amazon',
            'kroger': r'kroger',
            'target': r'target',
            'instacart': r'instacart',
            'whole foods': r'whole\s*foods',
            'trader joe': r'trader\s*joe',
        }

    def parse_eml_file(self, eml_data: bytes) -> Dict:
        """Parse .eml file and extract receipt data"""
        try:
            msg = BytesParser(policy=policy.default).parsebytes(eml_data)

            # Extract email metadata
            subject = msg['subject']
            date = self._parse_email_date(msg['date'])
            sender = msg['from']

            # Extract body content
            body = self._extract_email_body(msg)

            # Parse receipt data from body
            receipt_data = self._parse_receipt_from_body(body, subject, sender)
            receipt_data['purchase_date'] = date

            return receipt_data

        except Exception as e:
            raise ValueError(f"Failed to parse email: {str(e)}")

    def _parse_email_date(self, date_str: str) -> datetime:
        """Parse email date header"""
        try:
            # Email dates are typically in RFC 2822 format
            return email.utils.parsedate_to_datetime(date_str)
        except:
            return datetime.now()

    def _extract_email_body(self, msg) -> str:
        """Extract text content from email message"""
        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()

                if content_type == "text/plain":
                    try:
                        body += part.get_payload(decode=True).decode()
                    except:
                        pass
                elif content_type == "text/html":
                    try:
                        html_content = part.get_payload(decode=True).decode()
                        # Parse HTML and extract text
                        soup = BeautifulSoup(html_content, 'html.parser')
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        body += soup.get_text()
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode()
            except:
                body = str(msg.get_payload())

        return body

    def _parse_receipt_from_body(self, body: str, subject: str, sender: str) -> Dict:
        """Parse receipt data from email body"""
        # Identify store
        store_name = self._identify_store(body, subject, sender)

        # Extract items and totals
        items = self._extract_items_from_email(body, store_name)
        total, tax = self._extract_totals_from_email(body)

        return {
            'store_name': store_name,
            'items': items,
            'total_amount': total,
            'tax_amount': tax,
            'raw_text': body[:1000]  # Store first 1000 chars
        }

    def _identify_store(self, body: str, subject: str, sender: str) -> str:
        """Identify the store from email content"""
        combined_text = f"{subject} {sender} {body}".lower()

        for store, pattern in self.store_patterns.items():
            if re.search(pattern, combined_text):
                return store.title()

        return "Unknown Store"

    def _extract_items_from_email(self, body: str, store_name: str) -> List[Dict]:
        """Extract items from email body based on store format"""
        items = []

        # Generic patterns for common email receipt formats
        lines = body.split('\n')

        # Pattern 1: "Item Name   Qty   Price   Total"
        # Pattern 2: "Item Name $X.XX"
        # Pattern 3: "X x Item Name @ $Y.YY = $Z.ZZ"

        for line in lines:
            line = line.strip()

            # Skip empty lines and headers
            if not line or len(line) < 5:
                continue

            # Skip common non-item lines
            if any(skip in line.lower() for skip in ['order summary', 'subtotal', 'total',
                                                       'tax', 'shipping', 'delivery',
                                                       'payment', 'thank you', 'questions',
                                                       'customer service', '***', '---',
                                                       'visit us', 'follow us']):
                continue

            # Try pattern: "X x Item @ $Y.YY = $Z.ZZ" or "X x Item $Z.ZZ"
            pattern1 = r'(\d+)\s*x\s*(.+?)(?:@\s*[\$]?(\d+\.\d{2}))?\s*[\$]?\s*(\d+\.\d{2})'
            match1 = re.search(pattern1, line, re.IGNORECASE)

            if match1:
                quantity = float(match1.group(1))
                name = match1.group(2).strip()
                unit_price = float(match1.group(3)) if match1.group(3) else 0
                total_price = float(match1.group(4))

                if not unit_price:
                    unit_price = total_price / quantity

                items.append({
                    'name': self._clean_item_name(name),
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total_price': total_price
                })
                continue

            # Try pattern: "Item Name $X.XX" or "Item Name   X.XX"
            pattern2 = r'(.+?)[\s]{2,}[\$]?\s*(\d+\.\d{2})\s*$'
            match2 = re.search(pattern2, line)

            if match2:
                name = match2.group(1).strip()
                price = float(match2.group(2))

                # Filter out likely subtotals/totals based on price
                if len(name) > 2 and price > 0 and price < 500:  # Assume no single item > $500
                    items.append({
                        'name': self._clean_item_name(name),
                        'quantity': 1.0,
                        'unit_price': price,
                        'total_price': price
                    })

        return items

    def _clean_item_name(self, name: str) -> str:
        """Clean and normalize item names"""
        # Remove extra spaces and special characters
        name = re.sub(r'\s+', ' ', name)
        # Remove leading numbers/codes
        name = re.sub(r'^\d+\s*', '', name)
        # Remove common suffixes
        name = re.sub(r'\s*(ea|each|lb|oz|kg|g)\s*$', '', name, flags=re.IGNORECASE)
        name = name.strip()
        return name.title()

    def _extract_totals_from_email(self, body: str) -> tuple:
        """Extract total and tax from email body"""
        total = 0.0
        tax = 0.0

        # Look for total
        total_patterns = [
            r'(?:order\s+)?total[\s:]+[\$]?\s*(\d+\.\d{2})',
            r'amount\s+(?:due|charged)[\s:]+[\$]?\s*(\d+\.\d{2})',
            r'grand\s+total[\s:]+[\$]?\s*(\d+\.\d{2})',
        ]

        for pattern in total_patterns:
            match = re.search(pattern, body.lower())
            if match:
                total = float(match.group(1))
                break

        # Look for tax
        tax_patterns = [
            r'(?:sales\s+)?tax[\s:]+[\$]?\s*(\d+\.\d{2})',
            r'estimated\s+tax[\s:]+[\$]?\s*(\d+\.\d{2})',
        ]

        for pattern in tax_patterns:
            match = re.search(pattern, body.lower())
            if match:
                tax = float(match.group(1))
                break

        return total, tax
