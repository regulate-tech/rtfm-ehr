-----

## 🏥 A Hands-On Guide to Digital Health Records

### What You'll Learn

Welcome to your own "model village" of a hospital's IT system.

In the public sector, we don't just "buy an app." We build (or buy) complex systems made of many independent parts. This tutorial will walk you through setting up a miniature version of a modern Electronic Health Record (EHR) system on your own computer.

By the end of this, you will have a hands-on understanding of:

  * **How a "front-end" (a website) talks to a "back-end" (a database).**
  * **Why we separate data:** You'll see why a patient's *demographics* (name, NHS number) are stored separately from their *clinical data* (blood pressure).
  * **The power of "Standards":** We'll see why "openEHR" (a data standard) is crucial. It's like ensuring every hospital uses the same "filing-form" so data can be shared safely.
  * **The magic of "Containers":** You'll use a tool called **Docker** to launch this complex system in one simple command.

### ⏰ Time and Preparation

  * **Total Time:** About **40-45 minutes** (25 minutes for setup, 20 minutes to explore).
  * **Your "Classroom":** We'll assume you have a helper who has already set up your computer with the necessary background software (specifically **Python**, **Docker**, and a text editor).
  * **Your Role:** Your job is to follow the steps, type the commands, and understand *what* you are doing. You don't need to understand the code itself, just the *idea* behind it.

-----

## 🗺️ Part 1: Understanding the Blueprint (5 minutes)

Every good system starts with a plan. Let's look at the "blueprint" of our model hospital.

This looks technical, but it's simple. Think of it as a department store:

1.  **The User (You):** You are the shopper, using your browser.
2.  **The Flask Web App (The "Shop Front"):** This is the sales assistant you talk to. It's the website you see, with all the buttons and forms.
3.  **The PMI Database (The "Customer Loyalty Database"):** This first filing cabinet *only* stores basic customer information: name, address, NHS number. The sales assistant (Flask) can check this quickly.
4.  **The EHRBase API (The "Secure Warehouse Manager"):** This is a special, high-security manager. The sales assistant is *not allowed* to go into the warehouse. They must ask this manager using a very specific, secure order form (an "API call").
5.  **The EHR Database (The "Secure Warehouse"):** This is the high-security warehouse itself. It stores all the sensitive clinical data (blood pressure, test results).

The most important idea here is the **separation**. We keep the simple "customer list" (PMI) separate from the highly sensitive "medical vault" (EHR). This is a fundamental security and data management principle.

-----

## 🚀 Part 2: Step-by-Step: Building Your "Model Hospital"

### Step 1: Get the Kit and Open the "Workshop"

First, your helper will have downloaded the project. It's just a folder of files.

Now, we need to use the **command line**.

> **What is the Command Line?**
>
>   * **Analogy:** Think of it as **texting your computer**. Instead of clicking icons, you type precise, one-line commands to tell it exactly what to do.
>   * Your helper will show you how to open it (it's called **Terminal** or **Command Prompt**).

You'll start by telling your computer you want to work inside the project folder. Your helper will show you the command, which will look something like:

`cd path/to/the/ehr_demonstrator`

*(This just means "Change Directory" to that folder).*

### Step 2: Set Up Your "Private Workbench" (Time: 2 mins)

We are about to install several "tools." We don't want to mix them up with other projects on your computer. So, we'll create a "private workbench" just for this project.

> **What is a Virtual Environment (`venv`)?**
>
>   * **Analogy:** This is like setting up a dedicated, clean workbench. Instead of using all the tools in your main (and messy) garage, you create a new, empty bench and only add the *specific* tools this one project needs.

Type this command to **create** the workbench:
> **A Quick Note:** Your helper might have set up your computer to use `python3` instead of `python`. If `python` gives you an error, just try `python3` in its place for all commands in this tutorial\!

```bash
python -m venv venv
```
(Or, if `python` gives an error, use `python3`):

```bash
python3 -m venv venv
```
Now, type this command to **activate** it (on macOS/Linux):

```bash
source venv/bin/activate
```
**If you are on Windows (using 'Command Prompt' or 'Powershell'):**

```bash
venv\Scripts\activate
```

*(This command says, "I am now working at this new workbench." You'll see `(venv)` appear in your prompt, showing you it's active).*

### Step 3: Install Your "Tools" (Time: 3-5 mins)

Now that we're at our clean workbench, we need to install our Python tools. The project comes with a "shopping list" called `requirements.txt`.

> **What is `pip`?**
>
>   * **Analogy:** `pip` is your **personal shopper**. It reads your `requirements.txt` list, goes to the internet, and automatically downloads and installs every tool for you.

Type this command:

```bash
pip install -r requirements.txt
```

*(You'll see it downloading and installing things like "Flask" – our "Shop Front" software).*

### Step 4: Assemble the "Secure Warehouse" (Time: 3-5 mins)

This is the most "magical" step. We need to set up two complex servers: the **PostgreSQL Database** (the filing cabinets) and the **EHRBase Server** (the "Warehouse Manager").

This used to take days. Now, we use **Docker**.

> **What are Docker and Docker Compose?**
>
>   * **Analogy:** Think of **Docker** as a **standard, sealed shipping container** for software. A developer carefully packs *everything* an application needs (the code, the settings, the database) into one of these containers. The great thing about a real shipping container is that any port, any crane, and any ship can handle it, no matter what's inside. Docker is the same: your computer can run this "container" without having to worry about what's inside or if it will conflict with other software.
>   * **Docker Compose** is the **"shipping manifest"** (the `ehrbase.yml` file). Our "model hospital" isn't just one container; it's a *system* of two (the database and the warehouse manager). Docker Compose is the instruction list that says, "Please deliver one 'PostgreSQL' container and one 'EHRBase' container, and connect them together exactly like this so they can work as a team."

Type this command to build and run your back-end system:

```bash
docker-compose -f ehrbase.yml up -d
```

*(This may take a few minutes as it downloads the "shipping containers." The `-d` just means "run this in the background.")*

### Step 5: Prepare the Filing Cabinets (Time: 2 mins)

Our "warehouse" is running, but it's empty. We need to prepare it. The project includes "setup wizards" (Python scripts) to do this.

First, let's create the **"Customer Loyalty Database" (PMI)**:

```bash
python setup_pmi_database.py
```
(Or use `python3`):

```bash
python3 setup_pmi_database.py
```

*(This wizard just built the empty `patient_index` table, ready for patient names and NHS numbers).*

Next, let's install the **"standardized forms"** into our "Secure Warehouse":

```bash
python install_templates.py
```

(Or use `python3`):

```bash
python3 install_templates.py
```

*(This is a vital step\! This wizard just installed **two** "standardized forms" into the "Warehouse Manager" (EHRBase):*

  * `clinic_check.opt`: *A form for a nurse to enter blood pressure.*
  * `lab_results_hba1c.opt`: *A form for a lab machine to report a blood sugar (HbA1c) test.*

*This is what **data standards** are all about\! The system now *knows* what a valid blood pressure or lab result looks like.*)

### Step 6: Add "Fake Patients" (Time: 1 min)

An empty hospital isn't very useful. Let's add 20 fake patients to our "Customer Loyalty Database" (PMI).

Type this command:

```bash
python add_pmi_records.py 20
```

(Or use `python3`):

```bash
python3 add_pmi_records.py 20
```

*(This just populated our PMI database with 20 dummy records, e.g., "Jane Doe, NHS Number 99999901").*

### Step 7: Open the "Shop" for Business\! (Time: 1 min)

All the pieces are built. It's time to "open the doors."

Type this command to start your **"Shop Front" (the Flask web app)**:

```bash
flask run
```

Your command line will show that a server is running. Now, open your web browser (like Chrome or Edge) and go to this address:

**`http://127.0.0.1:5000`**

*(This address just means "my own computer" on "door number 5000").*

You should now see the "EHR Demonstrator Application" homepage\!

-----

## 👩‍⚕️ Part 3: Using Your Model Hospital (15-20 mins)

This is the most important part. Let's use the system to see how the data flows. We'll "role-play" as different staff members.

### Role 1: The Administrator

You've added 20 patients to the PMI (the "customer list"), but they don't have "secure medical files" yet. Let's create them.

1.  On the website, click **Admin**.
2.  Click the button that says **"Sync All PMI to EHR"**.

**What just happened?**
You just told the "Shop Assistant" (Flask) to:

1.  Read all 20 names from the "Customer List" (PMI).
2.  Go to the "Secure Warehouse Manager" (EHRBase) and say, "Please create 20 *new, empty, secure medical files*, one for each of these NHS numbers."

Now, our 20 patients are "in the system," ready to have clinical data added.

### Role 2: The Data Entry Clerk

Now, let's pretend a patient has had their blood pressure taken and a lab test done.

1.  First, we need a patient's NHS number. Go back to the **Admin** page, click **"View/Create EHR Record"**, and **copy** the NHS number of the first patient (e.g., `99999901`).
2.  Now, click **Data Entry** on the main navigation.
3.  **Paste** the NHS number (`99999901`) into the search box and click **"Search Patient"**.
4.  You'll see the patient's details and two new buttons. This is because we installed *two* different "standardized forms" (templates) in Step 5.
5.  **Try this first:** Click the **"Enter Vitals (Clinic Check Template)"** button.
      * A form appears. This form is defined by the `clinic_check.opt` template.
      * Enter a **Systolic** value (e.g., `120`) and a **Diastolic** value (e.g., `80`).
      * Click **"Submit Vitals"**.
6.  **Now, try this:** You should be back on the patient's data entry page. Click the **"Generate Random HbA1c Result (30-50mmol)"** button.
      * This time, you don't have to type anything. The system simulates a lab machine automatically sending a new blood sugar (HbA1c) result.
      * You should see a success message.

**What just happened?**
You just submitted clinical data in two different ways\!

  * First, you **manually** entered data (blood pressure) using a standard form, just like a nurse.
  * Second, you triggered an **automated** data feed (the lab result), just like a lab machine would.
  * Both data sets were packaged into their "standardized forms" and given to the "Warehouse Manager" (EHRBase), who filed them securely in patient `99999901`'s "Secure Medical File" (EHR).

### Role 3: The Clinician

Now, let's be a doctor looking up that patient's history.

1.  Click **Clinician View**.
2.  **Paste** the same NHS number (`99999901`) and click **"Search Patient"**.

You will now see **two** "compositions" listed:

  * The "Clinic Check" (blood pressure) you just entered manually.
  * The "Lab Result" (HbA1c) that was generated automatically.

You can see the raw data (in a format called JSON), proving both are stored securely and separately in the EHR.

### Role 4: The Patient

Finally, let's see this from the patient's perspective.

1.  Click **Patient View**.
2.  **Paste** the same NHS number (`99999901`) and click **"Search by NHS No"**.

Notice what you see:

  * **Demographic Details:** The patient's name, address, and date of birth are pulled from the **"Customer List" (PMI)**.
  * **Clinical Data:** *Both* the "Clinic Check" (120/80) and the "Lab Result (HbA1c)" are pulled from the **"Secure Warehouse" (EHR)**.

This is a perfect "Patient Portal," and it demonstrates the core concept: a single application securely pulling *multiple* records from two completely separate, specialized databases.

### Step 8: Closing the Shop

When you're finished, you need to shut down your model village.

1.  **Stop the "Shop Front":** Go to the command line window where you typed `flask run`. Press **`Ctrl + C`** on your keyboard.

2.  **Stop the "Warehouses":** Go to the command line window where you ran Docker. Type this:

    ```bash
    docker-compose -f ehrbase.yml down
    ```

*(This tells Docker to pack up the "shipping containers" (EHRBase and Postgres) and stop them).*

-----

## 🎓 Summary: What You've Learned

Congratulations\! You've just built and run a miniature, modern digital health system.

Here are the key takeaways for your next policy or procurement meeting:

  * **Systems are "De-Coupled":** You saw that the "Shop Front" (Flask) is separate from the "Data Warehouse" (EHRBase). This is a good design. It means you could build a *new* app (e.g., a mobile app for paramedics) that talks to the *same* "Secure Warehouse," without rebuilding everything.
  * **Separation of Concerns:** You learned that **demographic data** (PMI) and **clinical data** (EHR) are stored separately. This is a vital principle for security, privacy, and performance.
  * **Standards are Everything:** The system only worked because we gave it **"standardized forms"** (`clinic_check.opt` and `lab_results_hba1c.opt`). This is what **openEHR** provides. It gives us a 'common language' for both a nurse's manual entry *and* an automated lab machine's report. When you procure systems, asking "does this adhere to an open standard like openEHR?" is a crucial question. It's what ensures data can be shared and understood between different systems.
  * **"Shipping Containers" (Docker) Make it Possible:** You launched this entire, complex system with one command (`docker-compose up`). This "shipping container" technology is what allows modern services to be built, updated, and scaled reliably.

### 📚 Want to Learn More?

If you're curious about the technologies you just used, here are some non-technical starting points:

  * **openEHR Foundation:** The organization behind the data standard. [https://openehr.org/](https://openehr.org/)
  * **What is Docker?** A simple, 5-minute explanation. [https://www.docker.com/why-docker/](https://www.docker.com/why-docker/)
  * **What is Flask?** The "Shop Front" you used. [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)
  * **The NHS and openEHR:** The Apperta Foundation (a UK-based clinical-led organisation) strongly advocates for these open standards in the NHS. [https://apperta.org/](https://apperta.org/)

