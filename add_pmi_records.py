# --- add_pmi_records.py ---
import psycopg2
from faker import Faker
import configparser
import sys
import os
import argparse

CONFIG_FILE = "config.ini"


def load_db_config():
    """Reads pmi_database configuration from config.ini"""
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: '{CONFIG_FILE}' file not found.")
        sys.exit(1)
    config.read(CONFIG_FILE)
    if "pmi_database" not in config:
        print("Error: 'config.ini' must contain a [pmi_database] section.")
        sys.exit(1)
    return dict(config["pmi_database"])


def generate_fake_nhs_number(fake):
    """Generates a plausible 10-digit NHS number."""
    return str(fake.random_number(digits=10, fix_len=True))


def create_fake_patient_data(fake):
    """Generates a dictionary containing fake patient data."""
    first_name = fake.first_name()
    last_name = fake.last_name()
    try:
        gender_guess = fake.gender()
        if gender_guess == "male":
            gender, title = "Male", fake.prefix_male()
        elif gender_guess == "female":
            gender, title = "Female", fake.prefix_female()
        else:
            gender, title = "Other", fake.prefix()
    except AttributeError:
        gender = fake.random_element(elements=("Male", "Female", "Other"))
        if gender == "Male":
            title = fake.prefix_male()
        elif gender == "Female":
            title = fake.prefix_female()
        else:
            title = fake.prefix()
    title = title.replace(".", "") if title else None
    return {
        "nhs_number": generate_fake_nhs_number(fake),
        "title": title,
        "given_name": first_name,
        "family_name": last_name,
        "date_of_birth": fake.date_of_birth(minimum_age=0, maximum_age=115),
        "gender": gender,
        "address_line_1": fake.street_address(),
        "address_line_2": (
            fake.secondary_address()
            if fake.boolean(chance_of_getting_true=25)
            else None
        ),
        "town_or_city": fake.city(),
        "county": fake.county(),
        "postcode": fake.postcode(),
        "phone_mobile": fake.phone_number(),
        "phone_home": (
            fake.phone_number() if fake.boolean(chance_of_getting_true=50) else None
        ),
        "email_address": fake.email(),
    }


def insert_patients(db_config, patients_data):
    """Connects to the database and inserts multiple patient records."""
    conn, cur = None, None
    inserted_count = 0
    sql = """
        INSERT INTO patient_index (
            nhs_number, title, given_name, family_name, date_of_birth, gender,
            address_line_1, address_line_2, town_or_city, county, postcode,
            phone_mobile, phone_home, email_address
        ) VALUES (
            %(nhs_number)s, %(title)s, %(given_name)s, %(family_name)s, %(date_of_birth)s, %(gender)s,
            %(address_line_1)s, %(address_line_2)s, %(town_or_city)s, %(county)s, %(postcode)s,
            %(phone_mobile)s, %(phone_home)s, %(email_address)s
        ) ON CONFLICT (nhs_number) DO NOTHING;
    """
    try:
        conn = psycopg2.connect(**db_config)
        cur = conn.cursor()
        for patient in patients_data:
            try:
                cur.execute(sql, patient)
                if cur.rowcount > 0:
                    inserted_count += 1
            except psycopg2.IntegrityError:
                print(f"  Skipping duplicate NHS Number: {patient['nhs_number']}")
                conn.rollback()
            except Exception as e:
                print(
                    f"  Error inserting record for {patient.get('nhs_number', 'N/A')}: {e}"
                )
                conn.rollback()
        conn.commit()
        print(f"Successfully inserted {inserted_count} new patient records.")
    except psycopg2.Error as e:
        print(f"Database error during insertion: {e}")
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    return inserted_count


def main(num_records):
    """Generates and inserts the specified number of fake patient records."""
    fake = Faker("en_GB")
    print(f"Generating {num_records} fake patient records...")
    patients = [create_fake_patient_data(fake) for _ in range(num_records)]
    print("Generation complete.")
    db_config = load_db_config()
    print(f"Attempting to insert records into database '{db_config['dbname']}'...")
    insert_patients(db_config, patients)
    print("--- Process Finished ---")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add fake patient records to the PMI database."
    )
    parser.add_argument(
        "num_records", type=int, help="The number of fake records to create."
    )
    args = parser.parse_args()
    if args.num_records <= 0:
        print("Error: Number of records must be positive.")
    else:
        main(args.num_records)
