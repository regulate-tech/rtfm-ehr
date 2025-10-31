# --- install_templates.py ---
import requests
import os
import time
import sys
import configparser
from requests.auth import HTTPBasicAuth

CONFIG_FILE = 'config.ini'
TEMPLATES_DIR = "templates" # Top-level templates folder

def load_config():
    """Reads ehrbase_api configuration from config.ini"""
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: '{CONFIG_FILE}' file not found.")
        sys.exit(1)
    config.read(CONFIG_FILE)
    if 'ehrbase_api' not in config:
        print("Error: 'config.ini' must contain an [ehrbase_api] section.")
        sys.exit(1)
    return config['ehrbase_api']

def wait_for_ehrbase(base_url, auth, retries=15, delay=3):
    """Actively polls the ehrbase API until it's responsive."""
    print(f"Waiting for EHRbase server to be ready at {base_url}...")
    health_check_url = f"{base_url}/definition/query" # Check basic endpoint
    headers = {'Accept': 'application/json'}
    for i in range(retries):
        try:
            response = requests.get(health_check_url, headers=headers, auth=auth, timeout=3)
            # Expect 404 (no subject ID) or 200 (empty list), indicating server is up
            if response.status_code in [200, 404]:
                print("EHRbase server is responsive.")
                return True
        except requests.exceptions.ConnectionError:
            print(f"  Attempt {i+1}/{retries}: Connection refused. Retrying in {delay}s...")
        except requests.exceptions.ReadTimeout:
            print(f"  Attempt {i+1}/{retries}: Connection timed out. Retrying in {delay}s...")
        except Exception as e:
            print(f"  Attempt {i+1}/{retries}: Error: {e}. Retrying in {delay}s...")
        time.sleep(delay)
    print(f"Error: Could not connect to EHRbase at {base_url} after {retries} attempts.")
    return False

def main():
    config = load_config()
    ehrbase_url = config['base_url']
    auth = HTTPBasicAuth(config['user'], config['password'])

    if not wait_for_ehrbase(ehrbase_url, auth):
        sys.exit(1)

    print("Starting to upload templates...")
    if not os.path.exists(TEMPLATES_DIR) or not os.path.isdir(TEMPLATES_DIR):
        print(f"Error: Cannot find the '{TEMPLATES_DIR}' folder.")
        sys.exit(1)

    for filename in os.listdir(TEMPLATES_DIR):
        if filename.endswith(".opt"):
            filepath = os.path.join(TEMPLATES_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8-sig') as f:
                    xml_content = f.read()
                headers = {"Content-Type": "application/xml", "Prefer": "return=representation"}
                response = requests.post(
                    f"{ehrbase_url}/definition/template/adl1.4",
                    data=xml_content.encode('utf-8'),
                    headers=headers,
                    auth=auth
                )
                if response.status_code == 201:
                    print(f"Successfully uploaded template: {filename}")
                elif response.status_code == 409: # Conflict
                    print(f"Template {filename} already exists on server. Skipping.")
                else:
                    print(f"Error uploading {filename}: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"An error occurred processing {filename}: {e}")
    print("Template upload complete.")

if __name__ == "__main__":
    main()
