from typing import Dict, List
import re

class ItemCategorizer:
    """Categorize grocery items into food categories"""

    def __init__(self):
        # Define categories with keywords and colors for visualization
        self.categories = {
            'Produce': {
                'keywords': ['apple', 'banana', 'orange', 'grape', 'berry', 'strawberry',
                           'lettuce', 'tomato', 'potato', 'onion', 'carrot', 'broccoli',
                           'spinach', 'celery', 'pepper', 'avocado', 'cucumber', 'fruit',
                           'vegetable', 'salad', 'melon', 'peach', 'pear', 'plum', 'mango',
                           'pineapple', 'kale', 'cabbage', 'squash', 'zucchini', 'corn'],
                'color': '#4CAF50'
            },
            'Meat & Seafood': {
                'keywords': ['chicken', 'beef', 'pork', 'turkey', 'fish', 'salmon', 'tuna',
                           'shrimp', 'meat', 'steak', 'ground', 'bacon', 'sausage', 'ham',
                           'lamb', 'tilapia', 'cod', 'ribeye', 'sirloin', 'brisket'],
                'color': '#F44336'
            },
            'Dairy & Eggs': {
                'keywords': ['milk', 'cheese', 'yogurt', 'butter', 'cream', 'egg',
                           'sour cream', 'cottage', 'cheddar', 'mozzarella', 'parmesan',
                           'ice cream', 'whipped', 'half and half', 'dairy'],
                'color': '#FFF9C4'
            },
            'Bakery & Bread': {
                'keywords': ['bread', 'bagel', 'roll', 'bun', 'baguette', 'croissant',
                           'muffin', 'donut', 'cake', 'cookie', 'pastry', 'tortilla',
                           'wrap', 'pita', 'bakery'],
                'color': '#D7CCC8'
            },
            'Pantry & Canned': {
                'keywords': ['pasta', 'rice', 'bean', 'sauce', 'soup', 'cereal', 'oats',
                           'flour', 'sugar', 'salt', 'pepper', 'spice', 'oil', 'vinegar',
                           'can', 'canned', 'jar', 'box', 'bag', 'chips', 'crackers',
                           'peanut butter', 'jelly', 'jam', 'honey', 'syrup'],
                'color': '#FF9800'
            },
            'Beverages': {
                'keywords': ['water', 'juice', 'soda', 'coffee', 'tea', 'beer', 'wine',
                           'alcohol', 'drink', 'beverage', 'lemonade', 'cola', 'sprite',
                           'energy drink', 'sports drink', 'smoothie'],
                'color': '#2196F3'
            },
            'Frozen': {
                'keywords': ['frozen', 'ice', 'pizza', 'freezer', 'popsicle', 'ice cream'],
                'color': '#B3E5FC'
            },
            'Snacks & Sweets': {
                'keywords': ['candy', 'chocolate', 'snack', 'chip', 'popcorn', 'pretzel',
                           'cracker', 'granola', 'bar', 'gum', 'mint', 'cookie'],
                'color': '#E91E63'
            },
            'Condiments & Sauces': {
                'keywords': ['ketchup', 'mustard', 'mayo', 'mayonnaise', 'dressing',
                           'salsa', 'hot sauce', 'bbq', 'marinade', 'soy sauce',
                           'worcestershire', 'relish', 'pickle'],
                'color': '#795548'
            },
            'Other': {
                'keywords': [],
                'color': '#9E9E9E'
            }
        }

    def categorize_item(self, item_name: str) -> str:
        """Categorize a single item based on its name"""
        if not item_name:
            return 'Other'

        item_lower = item_name.lower()

        # Check each category's keywords
        for category, data in self.categories.items():
            if category == 'Other':
                continue

            for keyword in data['keywords']:
                # Use word boundaries for better matching
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, item_lower):
                    return category

        return 'Other'

    def get_category_color(self, category: str) -> str:
        """Get the color for a category"""
        return self.categories.get(category, {}).get('color', '#9E9E9E')

    def get_all_categories(self) -> Dict:
        """Get all categories with their colors"""
        return {
            cat: {'color': data['color']}
            for cat, data in self.categories.items()
        }
