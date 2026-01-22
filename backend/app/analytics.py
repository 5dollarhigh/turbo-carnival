from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import func, extract
from collections import defaultdict
import calendar

from app.models import db, Receipt, Item
from app.categorizer import ItemCategorizer

class AnalyticsEngine:
    """Generate comprehensive analytics from receipt data"""

    def __init__(self):
        self.categorizer = ItemCategorizer()

    def get_monthly_spending_trends(self, months: int = 12) -> Dict:
        """Get spending trends for the last N months"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)

        # Query receipts grouped by month
        monthly_data = db.session.query(
            extract('year', Receipt.purchase_date).label('year'),
            extract('month', Receipt.purchase_date).label('month'),
            func.sum(Receipt.total_amount).label('total'),
            func.count(Receipt.id).label('count'),
            func.avg(Receipt.total_amount).label('average')
        ).filter(
            Receipt.purchase_date >= start_date
        ).group_by('year', 'month').order_by('year', 'month').all()

        trends = []
        for year, month, total, count, average in monthly_data:
            month_name = calendar.month_name[int(month)]
            trends.append({
                'year': int(year),
                'month': int(month),
                'month_name': month_name,
                'label': f"{month_name[:3]} {int(year)}",
                'total_spent': round(float(total), 2),
                'receipt_count': count,
                'average_receipt': round(float(average), 2)
            })

        return {
            'trends': trends,
            'total_period_spend': round(sum(t['total_spent'] for t in trends), 2),
            'average_monthly_spend': round(sum(t['total_spent'] for t in trends) / len(trends), 2) if trends else 0
        }

    def get_category_breakdown(self, start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> Dict:
        """Get spending breakdown by category"""
        query = db.session.query(Item).join(Receipt)

        if start_date:
            query = query.filter(Receipt.purchase_date >= start_date)
        if end_date:
            query = query.filter(Receipt.purchase_date <= end_date)

        items = query.all()

        # Group by category
        category_totals = defaultdict(float)
        category_counts = defaultdict(int)

        for item in items:
            category = item.category or 'Other'
            category_totals[category] += item.total_price
            category_counts[category] += 1

        # Format results
        categories = []
        total_spend = sum(category_totals.values())

        for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total_spend * 100) if total_spend > 0 else 0
            categories.append({
                'category': category,
                'total_spent': round(amount, 2),
                'percentage': round(percentage, 2),
                'item_count': category_counts[category],
                'color': self.categorizer.get_category_color(category)
            })

        return {
            'categories': categories,
            'total_spend': round(total_spend, 2)
        }

    def get_top_expensive_items(self, limit: int = 50) -> List[Dict]:
        """Get the most expensive items purchased"""
        items = db.session.query(
            Item.name,
            func.sum(Item.total_price).label('total_spent'),
            func.count(Item.id).label('purchase_count'),
            func.avg(Item.unit_price).label('avg_price'),
            func.min(Item.unit_price).label('min_price'),
            func.max(Item.unit_price).label('max_price'),
            Item.category
        ).group_by(Item.name, Item.category).order_by(
            func.sum(Item.total_price).desc()
        ).limit(limit).all()

        top_items = []
        for name, total, count, avg_price, min_price, max_price, category in items:
            top_items.append({
                'name': name,
                'total_spent': round(float(total), 2),
                'purchase_count': count,
                'average_price': round(float(avg_price), 2),
                'min_price': round(float(min_price), 2),
                'max_price': round(float(max_price), 2),
                'category': category or 'Other'
            })

        return top_items

    def get_store_comparison(self) -> Dict:
        """Compare spending across different stores"""
        store_data = db.session.query(
            Receipt.store_name,
            func.sum(Receipt.total_amount).label('total_spent'),
            func.count(Receipt.id).label('visit_count'),
            func.avg(Receipt.total_amount).label('avg_receipt'),
            func.sum(Receipt.tax_amount).label('total_tax')
        ).group_by(Receipt.store_name).all()

        stores = []
        total_all_stores = sum(float(total) for _, total, _, _, _ in store_data)

        for store, total, count, avg, tax in store_data:
            percentage = (float(total) / total_all_stores * 100) if total_all_stores > 0 else 0
            stores.append({
                'store_name': store,
                'total_spent': round(float(total), 2),
                'visit_count': count,
                'average_receipt': round(float(avg), 2),
                'total_tax': round(float(tax), 2),
                'percentage': round(percentage, 2)
            })

        return {
            'stores': sorted(stores, key=lambda x: x['total_spent'], reverse=True),
            'total_spend': round(total_all_stores, 2)
        }

    def get_shopping_frequency(self) -> Dict:
        """Analyze shopping frequency patterns"""
        # Get all receipts ordered by date
        receipts = Receipt.query.order_by(Receipt.purchase_date).all()

        if not receipts:
            return {'average_days_between_trips': 0, 'shopping_frequency': 'N/A'}

        # Calculate days between shopping trips
        gaps = []
        for i in range(1, len(receipts)):
            gap = (receipts[i].purchase_date - receipts[i-1].purchase_date).days
            if gap > 0:  # Ignore same-day trips
                gaps.append(gap)

        avg_gap = sum(gaps) / len(gaps) if gaps else 0

        # Determine frequency category
        if avg_gap <= 3:
            frequency = "Very Frequent (Multiple times/week)"
        elif avg_gap <= 7:
            frequency = "Weekly"
        elif avg_gap <= 14:
            frequency = "Bi-weekly"
        elif avg_gap <= 30:
            frequency = "Monthly"
        else:
            frequency = "Infrequent"

        return {
            'average_days_between_trips': round(avg_gap, 1),
            'shopping_frequency': frequency,
            'total_trips': len(receipts)
        }

    def get_price_trends(self, item_name: Optional[str] = None) -> List[Dict]:
        """Get price trends for specific items over time"""
        query = db.session.query(
            Item.name,
            Receipt.purchase_date,
            Item.unit_price
        ).join(Receipt)

        if item_name:
            query = query.filter(Item.name.ilike(f'%{item_name}%'))

        query = query.order_by(Receipt.purchase_date)
        results = query.all()

        trends = []
        for name, date, price in results:
            trends.append({
                'item_name': name,
                'date': date.isoformat(),
                'price': round(float(price), 2)
            })

        return trends

    def get_comprehensive_summary(self) -> Dict:
        """Get a comprehensive summary of all spending"""
        # Total spending
        total_spent = db.session.query(func.sum(Receipt.total_amount)).scalar() or 0

        # Total receipts
        total_receipts = Receipt.query.count()

        # Date range
        first_receipt = Receipt.query.order_by(Receipt.purchase_date.asc()).first()
        last_receipt = Receipt.query.order_by(Receipt.purchase_date.desc()).first()

        # Average receipt
        avg_receipt = total_spent / total_receipts if total_receipts > 0 else 0

        # Total items purchased
        total_items = db.session.query(func.sum(Item.quantity)).scalar() or 0

        # Most expensive single item
        most_expensive = db.session.query(Item, Receipt).join(Receipt).order_by(
            Item.total_price.desc()
        ).first()

        # Most common category
        category_counts = db.session.query(
            Item.category,
            func.count(Item.id).label('count')
        ).group_by(Item.category).order_by(func.count(Item.id).desc()).first()

        return {
            'total_spent': round(float(total_spent), 2),
            'total_receipts': total_receipts,
            'average_receipt': round(float(avg_receipt), 2),
            'total_items': int(total_items),
            'first_receipt_date': first_receipt.purchase_date.isoformat() if first_receipt else None,
            'last_receipt_date': last_receipt.purchase_date.isoformat() if last_receipt else None,
            'most_expensive_item': {
                'name': most_expensive[0].name if most_expensive else None,
                'price': round(float(most_expensive[0].total_price), 2) if most_expensive else 0,
                'date': most_expensive[1].purchase_date.isoformat() if most_expensive else None,
                'store': most_expensive[1].store_name if most_expensive else None
            } if most_expensive else None,
            'most_common_category': category_counts[0] if category_counts else 'N/A'
        }

    def get_waste_insights(self) -> Dict:
        """Identify potential waste patterns (frequently purchased but small quantities)"""
        # Items purchased frequently in small quantities might indicate waste
        frequent_items = db.session.query(
            Item.name,
            func.count(Item.id).label('purchase_count'),
            func.avg(Item.quantity).label('avg_quantity'),
            func.sum(Item.total_price).label('total_spent')
        ).group_by(Item.name).having(
            func.count(Item.id) > 3  # Purchased more than 3 times
        ).order_by(func.count(Item.id).desc()).limit(20).all()

        insights = []
        for name, count, avg_qty, total in frequent_items:
            if float(avg_qty) <= 2:  # Small quantities
                insights.append({
                    'item_name': name,
                    'purchase_frequency': count,
                    'average_quantity': round(float(avg_qty), 2),
                    'total_spent': round(float(total), 2),
                    'suggestion': 'Consider buying in bulk to save money'
                })

        return {'insights': insights}
