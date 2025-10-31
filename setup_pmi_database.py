# --- setup_pmi_database.py ---
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import configparser
import sys
import os

def read_config():
    """Reads database configuration from config.ini"""
    config = configparser.ConfigParser()
    config_file = 'config.ini'
    if not os.path.exists(config_file):
        print(f"Error: '{config_file}' file not found.")
        sys.exit(1)
    config.read(config_file)
    if 'postgresql_admin' not in config:
        print("Error: 'config.ini' must contain a [postgresql_admin] section.")
        sys.exit(1)
    if 'pmi_database' not in config:
        print("Error: 'config.ini' must contain a [pmi_database] section.")
        sys.exit(1)
    return config

def create_database(admin_config, pmi_config):
    """Connects to the default DB and creates the new PMI database."""
    new_db_name = pmi_config['dbname']
    conn, cur = None, None
    try:
        conn = psycopg2.connect(**admin_config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        print(f"Attempting to create database '{new_db_name}'...")
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(new_db_name)))
        print(f"Successfully created database '{new_db_name}'.")
    except psycopg2.errors.DuplicateDatabase:
        print(f"Database '{new_db_name}' already exists. Skipping creation.")
    except psycopg2.Error as e:
        print(f"An error occurred while creating database: {e}")
        sys.exit(1)
    finally:
        if cur: cur.close()
        if conn: conn.close()

def execute_sql_from_file(pmi_config, sql_file):
    """Connects to the PMI database and executes SQL from a file."""
    if not os.path.exists(sql_file):
        print(f"Error: SQL file '{sql_file}' not found.")
        sys.exit(1)
    conn, cur = None, None
    try:
        conn = psycopg2.connect(**pmi_config)
        cur = conn.cursor()
        with open(sql_file, 'r') as f:
            sql_commands = f.read()
        print(f"Connecting to '{pmi_config['dbname']}' and executing SQL from '{sql_file}'...")
        cur.execute(sql_commands)
        conn.commit()
        print(f"Successfully executed schema setup in '{pmi_config['dbname']}'.")
    except psycopg2.Error as e:
        print(f"An error occurred while executing SQL: {e}")
        if conn: conn.rollback()
        sys.exit(1)
    finally:
        if cur: cur.close()
        if conn: conn.close()

def main():
    """Main function to run the setup process."""
    sql_file = 'create_pmi_schema.sql'
    print("--- Starting Patient Master Index (PMI) Database Setup ---")
    print("1. Reading configuration from 'config.ini'...")
    config = read_config()
    admin_config = dict(config['postgresql_admin'])
    pmi_config = dict(config['pmi_database'])
    print("\n2. Starting database creation step...")
    create_database(admin_config, pmi_config)
    print("\n3. Starting table creation step...")
    execute_sql_from_file(pmi_config, sql_file)
    print("\n--- Database setup complete! ---")

if __name__ == "__main__":
    main()
