import cv2
import numpy as np
import pytesseract
from pyzbar.pyzbar import decode
from typing import Dict, Optional, Tuple
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)

class ImageProcessor:
    @staticmethod
    def process_receipt(image_path: str) -> Dict:
        """Process receipt image and extract relevant information"""
        try:
            # Read image
            img = cv2.imread(image_path)
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding to preprocess the image
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

            # Apply OCR
            text = pytesseract.image_to_string(gray)
            
            # Extract information
            return ImageProcessor._parse_receipt_text(text)
        except Exception as e:
            logger.error(f"Error processing receipt: {e}")
            return {}

    @staticmethod
    def process_barcode(image_path: str) -> Optional[str]:
        """Process barcode image and return barcode number"""
        try:
            # Read image
            img = cv2.imread(image_path)
            
            # Decode barcodes
            barcodes = decode(img)
            
            if barcodes:
                return barcodes[0].data.decode('utf-8')
            return None
        except Exception as e:
            logger.error(f"Error processing barcode: {e}")
            return None

    @staticmethod
    def _parse_receipt_text(text: str) -> Dict:
        """Parse receipt text to extract relevant information"""
        result = {
            'items': [],
            'total': 0.0,
            'date': None
        }

        lines = text.split('\n')
        
        # Regular expressions for matching
        price_pattern = r'\$?\d+\.\d{2}'
        date_patterns = [
            r'\d{2}/\d{2}/\d{4}',
            r'\d{2}-\d{2}-\d{4}'
        ]

        current_item = None
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue

            # Try to find date
            if not result['date']:
                for pattern in date_patterns:
                    date_match = re.search(pattern, line)
                    if date_match:
                        try:
                            result['date'] = datetime.strptime(
                                date_match.group(), 
                                '%d/%m/%Y' if '/' in date_match.group() else '%d-%m-%Y'
                            )
                            break
                        except ValueError:
                            continue

            # Look for prices
            price_match = re.search(price_pattern, line)
            if price_match:
                price = float(price_match.group().replace('$', ''))
                
                # If line contains more than just the price, it's probably an item
                if len(line) > len(price_match.group()) + 2:
                    item_name = line[:price_match.start()].strip()
                    result['items'].append({
                        'name': item_name,
                        'price': price
                    })
                    result['total'] += price

        return result
