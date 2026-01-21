from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from app.models import db, Receipt, Item
from app.receipt_processor import ReceiptProcessor
from app.email_parser import EmailReceiptParser
from app.categorizer import ItemCategorizer
from app.analytics import AnalyticsEngine

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grocery_tracker.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

    # Initialize extensions
    db.init_app(app)
    CORS(app)

    # Initialize processors
    receipt_processor = ReceiptProcessor()
    email_parser = EmailReceiptParser()
    categorizer = ItemCategorizer()
    analytics = AnalyticsEngine()

    # Create tables
    with app.app_context():
        db.create_all()

    # Helper function to save receipt and items
    def save_receipt_to_db(receipt_data, source_type, source_file):
        """Save receipt and items to database"""
        try:
            receipt = Receipt(
                store_name=receipt_data.get('store_name', 'Unknown'),
                purchase_date=receipt_data.get('purchase_date', datetime.now()),
                total_amount=receipt_data.get('total_amount', 0.0),
                tax_amount=receipt_data.get('tax_amount', 0.0),
                source_type=source_type,
                source_file=source_file,
                raw_text=receipt_data.get('raw_text', '')
            )

            db.session.add(receipt)
            db.session.flush()  # Get receipt ID

            # Add items
            for item_data in receipt_data.get('items', []):
                # Categorize item
                category = categorizer.categorize_item(item_data['name'])

                item = Item(
                    receipt_id=receipt.id,
                    name=item_data['name'],
                    quantity=item_data.get('quantity', 1.0),
                    unit_price=item_data.get('unit_price', 0.0),
                    total_price=item_data.get('total_price', 0.0),
                    category=category
                )
                db.session.add(item)

            db.session.commit()
            return receipt

        except Exception as e:
            db.session.rollback()
            raise e

    # Routes
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

    @app.route('/api/receipts/upload-scan', methods=['POST'])
    def upload_scanned_receipt():
        """Upload and process a scanned receipt image"""
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400

            # Save file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'receipts', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)

            # Process receipt
            with open(filepath, 'rb') as f:
                image_data = f.read()

            receipt_data = receipt_processor.process_image(image_data)
            receipt = save_receipt_to_db(receipt_data, 'scan', filename)

            return jsonify({
                'success': True,
                'receipt': receipt.to_dict(),
                'message': 'Receipt processed successfully'
            }), 201

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/receipts/upload-email', methods=['POST'])
    def upload_email_receipt():
        """Upload and process an email receipt (.eml file)"""
        try:
            if 'file' not in request.files:
                return jsonify({'error': 'No file provided'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No file selected'}), 400

            if not file.filename.endswith('.eml'):
                return jsonify({'error': 'Only .eml files are supported'}), 400

            # Save file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'emails', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            file.save(filepath)

            # Process email
            with open(filepath, 'rb') as f:
                eml_data = f.read()

            receipt_data = email_parser.parse_eml_file(eml_data)
            receipt = save_receipt_to_db(receipt_data, 'email', filename)

            return jsonify({
                'success': True,
                'receipt': receipt.to_dict(),
                'message': 'Email receipt processed successfully'
            }), 201

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/receipts', methods=['GET'])
    def get_receipts():
        """Get all receipts with optional filtering"""
        try:
            # Query parameters
            store = request.args.get('store')
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            limit = request.args.get('limit', type=int, default=100)
            offset = request.args.get('offset', type=int, default=0)

            query = Receipt.query

            if store:
                query = query.filter(Receipt.store_name.ilike(f'%{store}%'))
            if start_date:
                query = query.filter(Receipt.purchase_date >= datetime.fromisoformat(start_date))
            if end_date:
                query = query.filter(Receipt.purchase_date <= datetime.fromisoformat(end_date))

            query = query.order_by(Receipt.purchase_date.desc())
            total = query.count()
            receipts = query.limit(limit).offset(offset).all()

            return jsonify({
                'receipts': [r.to_dict() for r in receipts],
                'total': total,
                'limit': limit,
                'offset': offset
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/receipts/<int:receipt_id>', methods=['GET'])
    def get_receipt(receipt_id):
        """Get a specific receipt by ID"""
        try:
            receipt = Receipt.query.get_or_404(receipt_id)
            return jsonify(receipt.to_dict())
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/receipts/<int:receipt_id>', methods=['DELETE'])
    def delete_receipt(receipt_id):
        """Delete a receipt"""
        try:
            receipt = Receipt.query.get_or_404(receipt_id)
            db.session.delete(receipt)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Receipt deleted'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/api/analytics/monthly-trends', methods=['GET'])
    def get_monthly_trends():
        """Get monthly spending trends"""
        try:
            months = request.args.get('months', type=int, default=12)
            data = analytics.get_monthly_spending_trends(months)
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/analytics/category-breakdown', methods=['GET'])
    def get_category_breakdown():
        """Get spending breakdown by category"""
        try:
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')

            start = datetime.fromisoformat(start_date) if start_date else None
            end = datetime.fromisoformat(end_date) if end_date else None

            data = analytics.get_category_breakdown(start, end)
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/analytics/top-items', methods=['GET'])
    def get_top_items():
        """Get top expensive items"""
        try:
            limit = request.args.get('limit', type=int, default=50)
            items = analytics.get_top_expensive_items(limit)
            return jsonify({'items': items})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/analytics/store-comparison', methods=['GET'])
    def get_store_comparison():
        """Get store comparison"""
        try:
            data = analytics.get_store_comparison()
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/analytics/shopping-frequency', methods=['GET'])
    def get_shopping_frequency():
        """Get shopping frequency analysis"""
        try:
            data = analytics.get_shopping_frequency()
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/analytics/summary', methods=['GET'])
    def get_summary():
        """Get comprehensive summary"""
        try:
            data = analytics.get_comprehensive_summary()
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/analytics/waste-insights', methods=['GET'])
    def get_waste_insights():
        """Get waste insights"""
        try:
            data = analytics.get_waste_insights()
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/categories', methods=['GET'])
    def get_categories():
        """Get all categories"""
        try:
            categories = categorizer.get_all_categories()
            return jsonify({'categories': categories})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return app
