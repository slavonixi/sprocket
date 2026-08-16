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
*   **Real-time reliable Inventory:** Tracks the physical quantity of elements currently in stock. Inventory business-logic is meticulously designed to avoid conflicts and critical races between stock operations. Every inventory operation is tracked and saved in the movements history, tagged with detailed information about the movement.
*   **Pdf/xlsx automated scanner:** Built-in file scanner to migrate excel inventories directly in the software. Forget spending nights to insert manually data into the software.
### 🛠 Maintenance Operations
*   **Maintenance Reports:** Formalized **`Report`** entities that track the status (Draft, Open, Closed) of every intervention, also providing several information about the customer, machineries, involved stocks and items.
*   **Detailed Operations:** A single report can contain multiple **`Operation`** records, detailing specific tasks performed over several days and materials usage per single task.
*   **Professional dashboard:** Administration-oriented dashboard provided by the browser platform allows offices to consult information about reports, technicians, inventory, clients, machineries, and manage documents.
### 👥 Client & HR Management
*   **Workforce Management:** Detailed technical staff profiles with associated tasks tracking.
*   **Technicians mobile app:** User-friendly mobile application allows technicians to manage their own workflow and tasks, materials usage, and operations reportage. With asynchronous task handling and local information storage, the app is able to work even without internet access ensuring information synchronization and coherence.
*   **Customer records:** Customer data and operation history allows to track progress, maintenance operations and client characteristics through several months or years.

Based on our implementation, **Sprocket** prioritizes data integrity and performance:

*   **Concurrency & Integrity:** Inventory operations utilize atomic transactions to prevent race conditions during simultaneous maintenance tasks.
*   **Asynchronous Logging:** Successful stock movements and errors are logged out-of-process via **Celery**. This ensures the UI remains responsive while maintaining a persistent audit trail in PostgreSQL.
*   **Structured Exceptions:** The system uses data-driven exceptions that return rich JSON objects (including SKU, requested quantity, and unit symbols), allowing the frontend to display localized, precise error messages.
*   **Service Layer Pattern:** Business logic is decoupled from views into specialized Services and Action Classes, keeping the codebase modular and avoiding monolithic orchestrators.

## 📝 Developing progress

*   **16/08/2026 - Inventory business logic:** Developing API inventory business logic, Movement tracking and retrieve operations (git branch 'movement-business-logic')

## ✔️ Todo

*   **Permissions and autorizations:** Implement user permissions through BasePermission class in DRF and django-rules 
*   **micro-service modules:** Decompose 'api' django application into service apps (e.g. inventory, HR_management, Report...) 
*   **Backend and API business logic:** Implement business logic of the other domains
*   **Unit-test:** Implement unit tests with pytests
*   **Web interface:**: develop web interface using react


## 📥 Installation

```bash
# Clone the repository
git clone https://github.com/sprocket/sprocket.git

# Build and start the containers
docker-compose up --build

# Migrations will automatically run
```

