# NARKIL ERP - Advanced Foundry Management System

Narkil is a high-performance, modular ERP solution specifically engineered for the foundry and casting industry. It provides deep visibility into production, inventory, and quality metrics through a professional, dark-themed interface.

## System Architecture

Narkil is built with a modular Python architecture for maximum scalability:
- `core/`: Database and business logic.
- `modules/`: Feature-specific modules (Inventory, Production, Quality, etc.).
- `ui/`: Branding, themes, and shared UI components.
- `assets/`: Logos and visual resources.

## Key Features

- **Multi-Tenant Login**: Secure access for multiple foundry sites with data isolation.
- **Inventory Control**: Real-time tracking of raw materials, alloys, and finished castings.
- **Production & Melt Control**: Active furnace monitoring and production queue management.
- **Quality & Traceability**: Batch-level inspection history and automated quality metrics.
- **Modern Dark Theme**: Optimized for industrial environments with the Narkil branding.

## Installation

1. **Install Prerequisites**:
   ```bash
   pip install PyQt6 pymongo bcrypt
   ```
2. **Database**: Ensure MongoDB is running locally or update the URI in `core/database.py`.
3. **Launch**:
   ```bash
   python main.py
   ```

## Default Credentials
- **Foundry**: Narkil Demo Foundry
- **Username**: `admin`
- **Password**: `narkil2026`
