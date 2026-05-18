import os
import bcrypt
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

# Load .env so MONGODB_URI is available when this module is imported directly
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

_DEFAULT_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")

class NarkilDatabase:
    def __init__(self, uri=_DEFAULT_URI):
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

    def _to_object_id(self, value):
        if isinstance(value, ObjectId):
            return value
        return ObjectId(value)

    def get_company_by_name(self, company_name):
        return self.companies.find_one({"company_name": company_name.strip()})

    def get_user_by_email(self, email, company_id):
        return self.users.find_one({
            "email": email.strip().lower(),
            "company_id": self._to_object_id(company_id)
        })

    def authenticate(self, email, password, company_id):
        user = self.get_user_by_email(email, company_id)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash']):
            return user
        return None

    def create_company_with_admin(self, company_name, admin_email, admin_password):
        normalized_company = company_name.strip()
        normalized_email = admin_email.strip().lower()

        if not normalized_company or not normalized_email or not admin_password:
            return False, "All company registration fields are required."
        if self.get_company_by_name(normalized_company):
            return False, "A company with this name already exists."

        # Global uniqueness for admin email avoids ambiguous tenant ownership.
        if self.users.find_one({"email": normalized_email}):
            return False, "This admin email is already in use."

        company_id = self.companies.insert_one({
            "company_name": normalized_company,
            "created_at": datetime.datetime.utcnow()
        }).inserted_id

        hashed = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt())
        self.users.insert_one({
            "email": normalized_email,
            "username": normalized_email.split("@")[0],
            "password_hash": hashed,
            "company_id": company_id,
            "roles": ["admin"],
            "two_factor_enabled": True,
            "created_at": datetime.datetime.utcnow()
        })
        return True, "Company and admin account created successfully."

    def register_user(self, company_id, email, password, roles=None, two_factor_enabled=True):
        normalized_email = email.strip().lower()
        if not normalized_email or not password:
            return False, "Email and password are required."

        oid = self._to_object_id(company_id)
        if not self.companies.find_one({"_id": oid}):
            return False, "Selected company does not exist."
        if self.get_user_by_email(normalized_email, oid):
            return False, "This email is already registered in the selected company."

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.users.insert_one({
            "email": normalized_email,
            "username": normalized_email.split("@")[0],
            "password_hash": hashed,
            "company_id": oid,
            "roles": roles or ["user"],
            "two_factor_enabled": bool(two_factor_enabled),
            "created_at": datetime.datetime.utcnow()
        })
        return True, "User registered successfully."

    # --- Seed Data ---
    def seed(self):
        if self.companies.count_documents({}) == 0:
            c_id = self.companies.insert_one({
                "company_name": "Narkil Demo Foundry",
                "created_at": datetime.datetime.utcnow()
            }).inserted_id
            
            hashed = bcrypt.hashpw("narkil2026".encode('utf-8'), bcrypt.gensalt())
            self.users.insert_one({
                "email": "admin@narkil.demo",
                "username": "admin",
                "password_hash": hashed,
                "company_id": c_id,
                "roles": ["admin"],
                "two_factor_enabled": True,
                "created_at": datetime.datetime.utcnow()
            })
            print("Narkil database seeded.")
