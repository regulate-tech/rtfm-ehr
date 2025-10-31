# --- app/blueprints/admin.py ---
from flask import (
    Blueprint, render_template, request, flash, redirect, url_for,
    current_app, get_flashed_messages, session # Added session
)
from flask_wtf.csrf import generate_csrf # To manually add CSRF token
from app.blueprints.forms import AddPmiForm, BatchPmiForm, SearchPmiForm, GeneralSearchForm, DeletePmiForm
import psycopg2
import psycopg2.extras
import configparser
import os
from faker import Faker
from app import ehrbase_api

bp = Blueprint('admin', __name__, template_folder='../templates/admin')

# --- Database Helper ---
def get_db_connection():
    config = configparser.ConfigParser()
    config_path = os.path.join(current_app.root_path, '..', 'config.ini')
    if not os.path.exists(config_path):
        flash('Configuration file (config.ini) not found.', 'error'); return None
    config.read(config_path)
    if 'pmi_database' not in config:
        flash('Missing [pmi_database] section in config.ini.', 'error'); return None
    db_config = dict(config['pmi_database'])
    try:
        conn = psycopg2.connect(**db_config, cursor_factory=psycopg2.extras.DictCursor)
        return conn
    except psycopg2.Error as e:
        flash(f"Database connection error: {e}", 'error'); return None

# --- Faker Helpers ---
def generate_fake_nhs_number(fake): return str(fake.random_number(digits=10, fix_len=True))

def create_fake_patient_data(fake):
    first_name, last_name = fake.first_name(), fake.last_name()
    try:
        gender_guess = fake.gender()
        if gender_guess == 'male': gender, title = 'Male', fake.prefix_male()
        elif gender_guess == 'female': gender, title = 'Female', fake.prefix_female()
        else: gender, title = 'Other', fake.prefix()
    except AttributeError:
        gender = fake.random_element(('Male', 'Female', 'Other'))
        if gender == 'Male': title = fake.prefix_male()
        elif gender == 'Female': title = fake.prefix_female()
        else: title = fake.prefix()
    title = title.replace('.', '') if title else None
    return {'nhs_number': generate_fake_nhs_number(fake), 'title': title, 'given_name': first_name, 'family_name': last_name, 'date_of_birth': fake.date_of_birth(minimum_age=0, maximum_age=115), 'gender': gender, 'address_line_1': fake.street_address(), 'address_line_2': fake.secondary_address() if fake.boolean(25) else None, 'town_or_city': fake.city(), 'county': fake.county(), 'postcode': fake.postcode(), 'phone_mobile': fake.phone_number(), 'phone_home': fake.phone_number() if fake.boolean(50) else None, 'email_address': fake.email()}

def insert_batch_patients(patients_data):
    conn = get_db_connection();
    if not conn: return 0
    cur = None; inserted_count, skipped_count = 0, 0
    sql = """INSERT INTO patient_index (nhs_number, title, given_name, family_name, date_of_birth, gender, address_line_1, address_line_2, town_or_city, county, postcode, phone_mobile, phone_home, email_address) VALUES (%(nhs_number)s, %(title)s, %(given_name)s, %(family_name)s, %(date_of_birth)s, %(gender)s, %(address_line_1)s, %(address_line_2)s, %(town_or_city)s, %(county)s, %(postcode)s, %(phone_mobile)s, %(phone_home)s, %(email_address)s) ON CONFLICT (nhs_number) DO NOTHING;"""
    try:
        cur = conn.cursor()
        for patient in patients_data:
            try: cur.execute(sql, patient); inserted_count += cur.rowcount
            except psycopg2.Error as e: print(f"DB Error inserting {patient.get('nhs_number')}: {e}"); conn.rollback(); skipped_count += 1
        conn.commit()
        if skipped_count > 0: flash(f"Skipped {skipped_count} records due to errors.", 'warning')
    except psycopg2.Error as e: flash(f"DB error during batch: {e}", 'error'); conn.rollback(); return 0
    finally:
        if cur: cur.close()
        if conn: conn.close()
    return inserted_count

# --- Routes ---
@bp.route('/')
def home():
    # Pass csrf_token for manual form
    csrf = generate_csrf()
    return render_template('admin_home.html', title='Admin Tools', csrf_token=csrf)

@bp.route('/add_pmi', methods=['GET', 'POST'])
def add_pmi():
    form = AddPmiForm()
    if form.validate_on_submit():
        conn = get_db_connection();
        if conn:
            cur = None
            try:
                cur = conn.cursor()
                sql = """INSERT INTO patient_index (nhs_number, title, given_name, family_name, date_of_birth, gender, address_line_1, address_line_2, town_or_city, county, postcode, phone_mobile, phone_home, email_address) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                cur.execute(sql, (form.nhs_number.data, form.title.data or None, form.given_name.data, form.family_name.data, form.date_of_birth.data, form.gender.data or None, form.address_line_1.data or None, form.address_line_2.data or None, form.town_or_city.data or None, form.county.data or None, form.postcode.data or None, form.phone_mobile.data or None, form.phone_home.data or None, form.email_address.data or None))
                conn.commit()
                flash(f'Patient {form.given_name.data} {form.family_name.data} added!', 'success')
                return redirect(url_for('admin.add_pmi'))
            except psycopg2.errors.UniqueViolation: conn.rollback(); flash(f'Error: NHS Number {form.nhs_number.data} exists.', 'error')
            except psycopg2.Error as e: conn.rollback(); flash(f'DB error: {e}', 'error')
            finally:
                if cur: cur.close()
                if conn: conn.close()
    return render_template('add_pmi.html', title='Add PMI Record', form=form)

@bp.route('/batch_pmi', methods=['GET', 'POST'])
def batch_pmi():
    form = BatchPmiForm()
    if form.validate_on_submit():
        num = form.num_records.data; fake = Faker('en_GB')
        try:
            print(f"Generating {num} fake records...")
            data = [create_fake_patient_data(fake) for _ in range(num)]
            print("Inserting...")
            inserted = insert_batch_patients(data)
            if inserted > 0: flash(f'Added {inserted} batch records!', 'success')
            elif not get_flashed_messages(category_filter=['error']): flash('No new records added (duplicates?).', 'info')
            return redirect(url_for('admin.batch_pmi'))
        except Exception as e: flash(f"Error generating/inserting: {e}", 'error')
    return render_template('batch_pmi.html', title='Add Batch PMI Records', form=form)

@bp.route('/view_create_ehr', methods=['GET', 'POST'])
def view_create_ehr():
    form = SearchPmiForm(); ehr_id, searched_nhs, action = None, None, None
    if form.validate_on_submit():
        nhs = form.nhs_number.data; searched_nhs = nhs
        print(f"Checking EHR for {nhs}")
        result = ehrbase_api.check_ehr_exists(nhs)
        if result is False: pass # Error flashed
        elif result is None:
            flash(f"No EHR for {nhs}. Creating...", 'info'); print(f"Creating EHR for {nhs}")
            new_id = ehrbase_api.create_ehr(nhs)
            if new_id: ehr_id, action = new_id, 'created'; flash(f"Created EHR: {ehr_id}", 'success'); print(f"Created {ehr_id}")
            else: action = 'creation_failed'; print(f"Failed create for {nhs}") # Error flashed
        else: ehr_id, action = result, 'found'; flash(f"EHR exists: {ehr_id}", 'info'); print(f"Found {ehr_id}")
    return render_template('view_create_ehr.html', title='View/Create EHR', form=form, ehr_id=ehr_id, searched_nhs=searched_nhs, action_taken=action)

@bp.route('/sync_pmi_ehr', methods=['POST'])
def sync_pmi_ehr():
    print("Starting PMI sync...")
    conn = get_db_connection();
    if not conn: return redirect(url_for('admin.home'))
    cur = None; total, found, created, pmi_err, api_err = 0, 0, 0, 0, 0
    try:
        cur = conn.cursor()
        cur.execute("SELECT nhs_number FROM patient_index WHERE nhs_number IS NOT NULL AND nhs_number != '';")
        records = cur.fetchall(); total = len(records)
        print(f"Found {total} records in PMI.")
        if total == 0: flash("No records in PMI.", 'info'); return redirect(url_for('admin.home'))
        for rec in records:
            nhs = rec['nhs_number'].strip()
            if not nhs: pmi_err += 1; continue
            print(f"  Syncing {nhs}...")
            result = ehrbase_api.check_ehr_exists(nhs)
            if result is False: api_err += 1; print(f"    Check error for {nhs}.")
            elif result is None:
                print(f"    Creating EHR for {nhs}...")
                new_id = ehrbase_api.create_ehr(nhs)
                if new_id: created += 1; print(f"    Created {new_id}")
                else: api_err += 1; print(f"    Create failed for {nhs}.")
            else: found += 1; print(f"    Exists: {result}")
    except psycopg2.Error as e: flash(f"DB error fetching records: {e}", 'error'); pmi_err = total; print(f"DB error: {e}")
    except Exception as e: flash(f"Unexpected sync error: {e}", 'error'); api_err = total - found - created; print(f"Sync error: {e}")
    finally:
        if cur: cur.close()
        if conn: conn.close()
    summary = f"Sync Complete. Total: {total}, Found: {found}, Created: {created}. "
    if pmi_err > 0: summary += f"PMI Errors: {pmi_err}. "
    if api_err > 0: summary += f"API Errors: {api_err}."; flash(summary, 'warning')
    else: flash(summary, 'success')
    print(f"Sync finished: {summary}")
    return redirect(url_for('admin.home'))

# --- At the end of app/blueprints/admin.py ---

@bp.route('/search', methods=['GET', 'POST'])
def search_pmi():
    """
    Provides a page to search for patients by name and delete them.
    """
    form = GeneralSearchForm()
    delete_form = DeletePmiForm() # We pass this to the template for the delete buttons
    results = []

    if form.validate_on_submit():
        # This is our "GET" part for search results
        search_term = form.term.data
        conn = get_db_connection()
        if conn:
            cur = None
            try:
                cur = conn.cursor()
                # Use ILIKE for case-insensitive search
                # Use %s for parameterization to prevent SQL injection
                query = """
                    SELECT * FROM patient_index
                    WHERE given_name ILIKE %s OR family_name ILIKE %s
                    ORDER BY family_name, given_name
                    LIMIT 100;
                """
                # The '%' are for the LIKE wildcard, not string formatting
                wildcard_term = f"%{search_term}%"

                cur.execute(query, (wildcard_term, wildcard_term))
                results = cur.fetchall()

                if not results:
                    flash(f"No patients found matching '{search_term}'.", 'info')

            except psycopg2.Error as e:
                flash(f"Database search error: {e}", 'error')
            finally:
                if cur: cur.close()
                if conn: conn.close()

    # This renders the page on initial load (GET) OR after a search (POST)
    return render_template(
        'search_pmi.html', 
        title='Search & Delete PMI', 
        form=form, 
        delete_form=delete_form, 
        results=results
    )

@bp.route('/delete_pmi/<nhs_number>', methods=['POST'])
def delete_pmi(nhs_number):
    """
    Securely deletes a patient record.
    This route ONLY accepts POST requests.
    """
    # We instantiate the form to validate the CSRF token
    form = DeletePmiForm()

    # form.validate_on_submit() is the key. It checks the CSRF token.
    if form.validate_on_submit():
        conn = get_db_connection()
        if conn:
            cur = None
            try:
                cur = conn.cursor()
                cur.execute("DELETE FROM patient_index WHERE nhs_number = %s", (nhs_number,))
                conn.commit()
                if cur.rowcount > 0:
                    flash(f"Successfully deleted patient {nhs_number}.", 'success')
                else:
                    flash(f"Could not find patient {nhs_number} to delete.", 'warning')
            except psycopg2.Error as e:
                flash(f"Database delete error: {e}", 'error')
                conn.rollback()
            finally:
                if cur: cur.close()
                if conn: conn.close()
    else:
        # This happens if the CSRF token is missing or invalid
        flash("Invalid or missing security token. Deletion failed.", 'error')

    # Redirect back to the main admin page
    return redirect(url_for('admin.home'))