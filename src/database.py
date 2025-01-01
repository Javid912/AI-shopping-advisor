from datetime import datetime
from typing import Dict, List, Optional
import pymongo
from pymongo import MongoClient
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, connection_string: str = "mongodb://localhost:27017/"):
        self.client = MongoClient(connection_string)
        self.db = self.client.grocery_manager
        self.products = self.db.products
        self.users = self.db.users
        self._setup_indexes()

    def _setup_indexes(self):
        """Setup database indexes"""
        # Create indexes for faster queries
        self.products.create_index([("user_id", pymongo.ASCENDING)])
        self.products.create_index([("expiry_date", pymongo.ASCENDING)])
        self.users.create_index([("user_id", pymongo.ASCENDING)], unique=True)

    def add_user(self, user_id: int, username: str) -> bool:
        """Add a new user or update existing user"""
        try:
            self.users.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "username": username,
                        "last_active": datetime.now(),
                        "settings": {"notifications_enabled": True}
                    }
                },
                upsert=True
            )
            return True
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return False

    def add_product(self, user_id: int, product_data: Dict) -> bool:
        """Add a new product to the database"""
        try:
            product_data["user_id"] = user_id
            product_data["added_date"] = datetime.now()
            self.products.insert_one(product_data)
            return True
        except Exception as e:
            logger.error(f"Error adding product: {e}")
            return False

    def get_expiring_products(self, user_id: int, days: int = 7) -> List[Dict]:
        """Get products expiring within specified days"""
        expiry_date = datetime.now() + timedelta(days=days)
        try:
            return list(self.products.find({
                "user_id": user_id,
                "expiry_date": {
                    "$gte": datetime.now(),
                    "$lte": expiry_date
                }
            }))
        except Exception as e:
            logger.error(f"Error getting expiring products: {e}")
            return []

    def get_user_products(self, user_id: int) -> List[Dict]:
        """Get all products for a user"""
        try:
            return list(self.products.find({"user_id": user_id}))
        except Exception as e:
            logger.error(f"Error getting user products: {e}")
            return []

    def get_monthly_spending(self, user_id: int, month: int, year: int) -> float:
        """Get total spending for a specific month"""
        try:
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)

            result = self.products.aggregate([
                {
                    "$match": {
                        "user_id": user_id,
                        "added_date": {
                            "$gte": start_date,
                            "$lt": end_date
                        }
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total": {"$sum": "$price"}
                    }
                }
            ])
            
            result_list = list(result)
            return result_list[0]["total"] if result_list else 0.0
        except Exception as e:
            logger.error(f"Error getting monthly spending: {e}")
            return 0.0
