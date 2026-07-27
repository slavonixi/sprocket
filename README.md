# Sprocket: Industrial Maintenance SaaS

> [!NOTE]
> The application is currently being developed


**Sprocket** aims to be a specialized SaaS platform designed for companies providing maintenance for industrial machinery, plants, and equipment. It streamlines technical interventions by managing resources, reports, and real-time inventory movements through a robust, data-driven backend. Its main goal is to boost technician's efficiency directly in the field, providing an easy-access platform to quickly record every maintenance operation detail. Then, a management dashboard will report every operations data and allows administrators to manage technicians workflow, inventories, and get data overviews.

## 🛠 Tech Stack

*   **Backend:** Django & Django Rest Framework (DRF).
*   **Database:** PostgreSQL with schemas to handle multi-tenancy.
*   **Task Queue & Caching:** Celery & Redis.
*   **DevOps:** Docker & Docker Compose.

## 🚀 Key Features

### 📦 Inventory & Stock Management
*   **Masterdata Control:** Centralized repository for all materials and spare parts via **`Inv_masterdata`**, including details like SKU, weight, and pricing.
*   **Custom EAN13 Barcodes:** Includes a specialized **`EAN13Field`** that ensures every barcode follows the 13-digit numeric standard.
*   **Real-time Inventory:** Tracks the physical quantity of elements currently in stock. Inventory business-logic is meticulously designed to avoid conflicts and critical races between stock operations.

### 🛠 Maintenance Operations
*   **Maintenance Reports:** Formalized **`Report`** entities that track the status (Draft, Open, Closed) of every intervention, also providing several information about the customer, machineries, involved stocks and items.
*   **Detailed Operations:** A single report can contain multiple **`Operation`** records, detailing specific tasks performed over several days.

### 👥 Client & HR Management
*   **Customer Records:** Stores client details with unique **UUID4** identifiers for secure and collision-free integration.
*   **Workforce Management:** Detailed technical staff profiles with associated labor cost tracking.

## 🏗 Architectural Highlights

Based on our implementation, **Sprocket** prioritizes data integrity and performance:

*   **Concurrency & Integrity:** Inventory operations utilize atomic transactions to prevent race conditions during simultaneous maintenance tasks.
*   **Asynchronous Logging:** Successful stock movements and errors are logged out-of-process via **Celery**. This ensures the UI remains responsive while maintaining a persistent audit trail in PostgreSQL.
*   **Structured Exceptions:** The system uses data-driven exceptions that return rich JSON objects (including SKU, requested quantity, and unit symbols), allowing the frontend to display localized, precise error messages.
*   **Service Layer Pattern:** Business logic is decoupled from views into specialized Services and Action Classes, keeping the codebase modular and avoiding monolithic orchestrators.

## 📥 Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/sprocket.git

# Build and start the containers
docker-compose up --build

# Run migrations
docker-compose exec web python manage.py migrate
```

## 🧪 Testing Suite
The project uses Django's built-in testing framework along with pytest (optional) to ensure the reliability of maintenance operations and stock integrity.
Running Tests
Since the application is containerized, you should run tests inside the web container to ensure the correct environment (Postgres, Redis) is used:

```bash
# Run all tests
docker-compose exec web python manage.py test

# Run tests for a specific module (e.g., Inventory)
docker-compose exec web python manage.py test inventory.tests
```