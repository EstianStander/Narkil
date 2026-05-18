import bcrypt
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

class NarkilDatabase:
    def __init__(self, uri="mongodb://localhost:27017/"):
        self.client = MongoClient(uri)
        self.db = self.client['narkil_erp']
        
        # Collections
        self.companies = self.db['companies']
        self.users = self.db['users']
        self.orders = self.db['orders']
        self.products = self.db['products']
        self.inventory = self.db['inventory']
        self.production = self.db['production']
        self.tickets = self.db['tickets']
        self.quality = self.db['quality']

    # --- Multi-Tenant Logic ---
    def get_companies(self):
        return list(self.companies.find())

    def authenticate(self, username, password, company_id):
        user = self.users.find_one({
            "username": username, 
            "company_id": ObjectId(company_id)
        })
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
            return user
        return None

    # --- Seed Data ---
    def seed(self):
        if self.companies.count_documents({}) == 0:
            c_id = self.companies.insert_one({
                "company_name": "Narkil Demo Foundry",
                "created_at": datetime.datetime.utcnow()
            }).inserted_id
            
            hashed = bcrypt.hashpw("narkil2026".encode('utf-8'), bcrypt.gensalt())
            self.users.insert_one({
                "username": "admin",
                "password_hash": hashed,
                "company_id": c_id,
                "roles": ["admin"]
            })
            print("Narkil database seeded.")
