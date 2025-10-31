# EHR Demonstrator Application

This project provides a local demonstration environment for a simple Electronic Health Records (EHR) system based on openEHR standards, using EHRBase, PostgreSQL, and a Flask web interface.

It includes:
* A Patient Master Index (PMI) database.
* An EHRBase instance for storing clinical data according to openEHR templates.
* Scripts for setup, template installation, and sample data generation.
* A Flask web application with interfaces for Admin, Data Entry, Clinician, and Patient views.
* A description of the landscape of EHR systems with a focus on openEHR in [EXPLAINER.md](EXPLAINER.md).
* A tutorial designed for helping a non-technical decision maker understand these systems in [TUTORIAL.md](TUTORIAL.md)

---

## 🏛️ Project Structure

The project is organized as follows:

```

ehr_demonstrator/
├── app/                  \# Flask application package
│   ├── **init**.py         \# Flask app factory
│   ├── ehrbase_api.py      \# EHRBase API helper functions
│   ├── blueprints/         \# Flask Blueprints for different sections
│   │   ├── **init**.py
│   │   ├── admin.py
│   │   ├── clinician.py
│   │   ├── data_entry.py
│   │   ├── forms.py        \# WTForms definitions
│   │   └── patient.py
│   ├── static/             \# Static files (CSS, JS, images)
│   │   └── css/
│   │       └── style.css
│   └── templates/          \# Jinja2 HTML templates
│       ├── base.html
│       ├── index.html
│       ├── admin/
│       ├── clinician/
│       ├── data_entry/
│       └── patient/
├── templates/              \# Folder for OpenEHR templates (.opt files)
│   └── clinic_check.opt
│   └── lab_result_hba1c.opt
├── .env                    \# Flask environment variables (SECRET\_KEY) - **Create this\!**
├── .gitignore              \# Git ignore file
├── config.ini              \# Unified config for DBs and EHRBase API
├── config.py               \# Flask config class
├── create_pmi_schema.sql   \# SQL schema for PMI table
├── ehrbase.yml             \# Docker Compose file for EHRBase/Postgres
├── install_templates.py    \# Script to install .opt templates
├── requirements.txt        \# Python dependencies
├── run.py                  \# Script to run the Flask app
├── setup_pmi_database.py   \# Script to create PMI DB and table
├── add_pmi_records.py      \# Script to add fake PMI data
└── sync_pmi_ehrbase.py     \# Original sync script (functionality in Flask admin)

````

---

## 🧩 System Interaction Diagram

This diagram shows how the main components interact:

```mermaid
graph LR
    User[End User] -- Browser HTTP --> Flask[Flask Web App];

    subgraph PostgreSQL Database Server
        PMI_DB[(PMI Database)];
        EHR_DB[(EHR Database)];
    end

    Flask -- SQL queries --> PMI_DB;
    Flask -- REST API (JSON) --> EHRBase[EHRBase API Server];
    EHRBase -- SQL queries --> EHR_DB;

    style User fill:#f9f,stroke:#333,stroke-width:2px
    style Flask fill:#ccf,stroke:#333,stroke-width:2px
    style EHRBase fill:#cfc,stroke:#333,stroke-width:2px
    style PMI_DB fill:#ff9,stroke:#333,stroke-width:2px
    style EHR_DB fill:#ff9,stroke:#333,stroke-width:2px

````

**Explanation:**

1.  The **End User** interacts with the system via their web browser, sending requests to the **Flask Web App**.
2.  The **Flask Web App** handles user requests:
      * It reads and writes patient demographic data directly to the **PMI Database** within PostgreSQL using SQL.
      * It reads and writes clinical record data by making REST API calls (sending/receiving JSON) to the **EHRBase API Server**.
3.  The **EHRBase API Server** processes requests from the Flask app:
      * It manages the storage and retrieval of openEHR-compliant data in the separate **EHR Database** within PostgreSQL using SQL.

-----

## ✅ Prerequisites

Before you begin, ensure you have the following installed:

1.  **Docker and Docker Compose:** Required to run EHRBase and PostgreSQL. Installation guides:
      * Docker: [https://docs.docker.com/engine/install/](https://docs.docker.com/engine/install/)
      * Docker Compose: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)
2.  **Python:** Version 3.10 or newer is recommended.
3.  **pip:** Python's package installer (usually comes with Python).

-----

## ⚙️ Installation Steps

1.  **Get the Code:**

      * Download and unzip the `ehr_demonstrator.zip` file containing the project code.
      * Alternatively, if using Git: `git clone <repository_url>`
      * Navigate into the project directory: `cd ehr_demonstrator`

2.  **Set up Python Virtual Environment:**

      * It's highly recommended to use a virtual environment to isolate dependencies.

    <!-- end list -->

    ```bash
    python -m venv venv
    ```

      * Activate the environment:
          * **macOS/Linux:** `source venv/bin/activate`
          * **Windows (cmd):** `venv\Scripts\activate.bat`
          * **Windows (PowerShell):** `venv\Scripts\Activate.ps1`
      * You should see `(venv)` prepended to your command prompt.

3.  **Install Python Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Application:**

      * **`.env` File:** Create a file named `.env` in the project root directory (`ehr_demonstrator/`). Add the following lines, replacing the secret key with your own secure random string (e.g., generate one using `python -c "import secrets; print(secrets.token_hex(16))"`):
        ```text
        FLASK_APP=run.py
        FLASK_ENV=development
        SECRET_KEY='your_super_secret_random_string_here'
        ```
      * **`config.ini` File:** Review the `config.ini` file. The default settings should work if you run Docker locally on standard ports (Postgres on 5432, EHRBase on 8080). Adjust `host`, `port`, `user`, or `password` settings only if your local Docker or PostgreSQL setup differs. **Ensure the passwords in `[postgresql_admin]` and `[pmi_database]` match the `POSTGRES_PASSWORD` in `ehrbase.yml`**. Ensure the `[ehrbase_api]` user/password match the default EHRBase credentials (`ehrbase-user`/`ehrbase-password` unless changed in future EHRBase versions).

5.  **Start EHRBase and PostgreSQL:**

      * Open a new terminal in the `ehr_demonstrator` directory.
      * Run Docker Compose in detached mode:
        ```bash
        docker-compose -f ehrbase.yml up -d
        ```
      * This will download the necessary images (if not already present) and start the containers. It might take a minute or two the first time, especially while EHRBase initializes its database schema.
      * You can check the status with `docker ps`. You should see `ehrbase_postgres` and `ehrbase_server` running.

6.  **Set up the PMI Database:**

      * Ensure your virtual environment is active.
      * Run the setup script:
        ```bash
        python setup_pmi_database.py
        ```
      * This script connects to PostgreSQL (using admin credentials from `config.ini`), creates the `pmi` database, and then creates the `patient_index` table using `create_pmi_schema.sql`.

7.  **Install EHRBase Templates:**

      * Ensure EHRBase is fully running (step 5).
      * Run the template installation script:
        ```bash
        python install_templates.py
        ```
      * This script connects to the EHRBase API (using credentials from `config.ini`) and uploads any `.opt` files found in the `templates/` directory (e.g., `vital_signs.opt`). It includes waits and retries to ensure EHRBase is ready.

8.  **Add Sample PMI Data (Optional but Recommended):**

      * To populate the PMI with fake data for testing:
        ```bash
        python add_pmi_records.py 20
        ```
        *(Replace `20` with the desired number of fake patient records).*

-----

## ▶️ Running the Web Application

1.  **Ensure Docker Containers are Running:** Check `docker ps` to confirm `ehrbase_postgres` and `ehrbase_server` are up.
2.  **Activate Virtual Environment:** If not already active, `source venv/bin/activate` (or Windows equivalent).
3.  **Start Flask Development Server:**
    ```bash
    flask run
    ```
    *(Alternatively, `python run.py`)*
4.  **Access the Application:** Open your web browser and navigate to `http://127.0.0.1:5000` (or `http://localhost:5000`).

-----

## 🧭 Using the Demonstrator

  * **Home:** Provides navigation to the different roles.
  * **Admin:**
      * *Add Single PMI Record:* Manually create a patient in the PMI DB.
      * *Add Batch PMI Records:* Generate multiple fake patients in the PMI DB.
      * *View/Create EHR Record:* Enter an NHS number. Checks EHRBase; if an EHR doesn't exist, it creates one. Shows the EHR ID.
      * *Sync All PMI to EHR:* Checks *all* patients in the PMI DB and creates EHRs in EHRBase for any missing ones (triggered by a button).
  * **Data Entry:**
      * Search for a patient by NHS number.
      * If the EHR exists, presents a form to enter Systolic and Diastolic Blood Pressure.
      * Submitting posts a new Vital Signs Composition to the patient's EHR in EHRBase.
  * **Clinician View:**
      * Search for a patient by NHS number.
      * If the EHR exists, displays a list of all compositions (e.g., submitted vital signs) stored in that EHR, showing basic details and raw JSON.
  * **Patient View:**
      * Search for patient records by NHS Number OR by Full Name + Date of Birth.
      * Displays the matched patient's demographic details from the PMI DB.
      * If an associated EHR exists in EHRBase, displays its compositions (similar to Clinician View).

-----

## 🛑 Stopping the Services

1.  **Stop Flask App:** Press `Ctrl+C` in the terminal where `flask run` is running.
2.  **Stop Docker Containers:** In the terminal where you ran docker-compose (or any terminal in the project directory):
    ```bash
    docker-compose -f ehrbase.yml down
    ```
      * To remove the database volume (delete all data): `docker-compose -f ehrbase.yml down -v`

<!-- end list -->

This updated `README.md` now contains the project structure and the Mermaid diagram, providing a more complete overview directly within the installation instructions.
```

