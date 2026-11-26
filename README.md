# SmartFactory — Order-to-Audit System

A prototype order-to-audit system for a small food manufacturer, covering the workflow from sales orders and inventory management to production, dispatch, payments, and reporting.

## Tech Stack

- **Python** — application logic
- **Flask** — web application and routing
- **SQLite** — lightweight database for the prototype
- **SQLAlchemy** — ORM and database operations
- **Flask-Migrate / Alembic** — database migrations
- **HTML, CSS, Bootstrap** — web interface

## Features

- Sales order creation
- Order approval
- Raw material purchasing and inventory updates
- Production planning and batch recording
- BOM-based material consumption
- Finished goods inventory
- Dispatch management with partial dispatch support
- Payment recording and outstanding balance tracking
- Reports and dashboard

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/poonkavi/smartfactory-order-to-audit.git
   cd smartfactory-order-to-audit
   ```

2. Create and activate a virtual environment:

   **Windows:**
   ```powershell
   python -m venv venv
   venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Initialize the database and load benchmark data:

   ```bash
   python init_db.py
   ```

5. Run the application:

   ```bash
   python run.py
   ```

6. Open the local URL shown in your terminal, usually:

   `http://127.0.0.1:5000`

## Assumptions

- The prototype uses a small food manufacturer as the benchmark business.
- Orders require approval before dispatch.
- Production consumes raw materials based on the configured Bill of Materials (BOM).
- Dispatch can be partial when stock is insufficient.
- Payments may be partial, with outstanding balances tracked.

## Known Gaps

- The prototype is intended for demonstration and evaluation, not production deployment.
- Authentication and role access require further security hardening.
- No external payment gateway is integrated.
- Offline synchronization and multi-user deployment require further development.

## Benchmark

Benchmark verification was performed using purchase, production, sales, dispatch and payment flows.

Detailed benchmark quantities, costs, stock movements and financial values are documented in the submission design note.