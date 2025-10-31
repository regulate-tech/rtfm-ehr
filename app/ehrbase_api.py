# --- app/ehrbase_api.py ---
import requests
import configparser
import os
import json
import datetime
from requests.auth import HTTPBasicAuth
from flask import current_app, flash, get_flashed_messages

def _load_ehrbase_config():
    """Loads EHRBase API configuration from config.ini."""
    config = configparser.ConfigParser()
    config_path = os.path.join(current_app.root_path, '..', 'config.ini')
    if not os.path.exists(config_path):
        return None, None, None
    config.read(config_path)
    if 'ehrbase_api' not in config or 'openehr' not in config:
        return None, None, None
    return dict(config['ehrbase_api']), config['openehr']['patient_id_namespace'], config

def _get_auth(ehrbase_config):
    """Creates BasicAuth object from config."""
    return HTTPBasicAuth(ehrbase_config['user'], ehrbase_config['password'])

def check_ehr_exists(subject_id):
    """
    Checks ehrbase API if an EHR exists for the given subject_id.
    Returns: The ehr_id if found, None if not found (404), False on error.
    """
    ehrbase_config, namespace, _ = _load_ehrbase_config()
    if not ehrbase_config or not namespace:
        flash("EHRBase configuration error in config.ini.", 'error')
        return False
    auth = _get_auth(ehrbase_config)
    url = f"{ehrbase_config['base_url']}/ehr"
    headers = {'Accept': 'application/json'}
    params = {'subject_id': subject_id, 'subject_namespace': namespace}
    try:
        response = requests.get(url, headers=headers, params=params, auth=auth, timeout=5)
        if response.status_code == 200: return response.json().get('ehr_id', {}).get('value')
        elif response.status_code == 404: return None
        else:
            flash(f"Error checking EHR: {response.status_code} - {response.text}", 'error')
            return False
    except requests.exceptions.RequestException as e:
        flash(f"EHRBase connection error during check: {e}. Is server running?", 'error')
        return False
    except Exception as e:
        flash(f"Unexpected error checking EHR: {e}", 'error')
        return False

def create_ehr(subject_id):
    """
    Creates a new EHR in ehrbase for the given subject_id using the
    v1.1.0+ method (POSTing a full EHR_STATUS JSON body).
    Returns: The new ehr_id if successful, None on failure.
    """
    ehrbase_config, namespace, _ = _load_ehrbase_config()
    if not ehrbase_config or not namespace:
        flash("EHRBase configuration error in config.ini.", 'error')
        return None

    auth = _get_auth(ehrbase_config)
    url = f"{ehrbase_config['base_url']}/ehr"

    # --- THIS IS THE FIX ---
    # We must build the full JSON payload that your server expects.
    # The 'scheme' is mandatory, as we discovered from the 400 error.
    json_payload = {
        "_type": "EHR_STATUS",
        "archetype_node_id": "openEHR-EHR-EHR_STATUS.generic.v1",
        "name": {"value": "EHR status"},
        "subject": {
            "_type": "PARTY_SELF",
            "external_ref": {
                "_type": "PARTY_REF",
                "id": {
                    "_type": "GENERIC_ID",
                    "value": str(subject_id),
                    "scheme": "pmi-id-scheme"  # This is the mandatory scheme
                },
                "namespace": namespace, # This comes from your config.ini
                "type": "PERSON"
            }
        },
        "is_queryable": True,
        "is_modifiable": True
    }

    # 'Content-Type' IS needed now because we are sending a JSON body
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json', # <--- ADD THIS BACK
        'Prefer': 'return=representation' 
    }

    try:
        # Use 'json=' instead of 'params='
        response = requests.post(
            url,
            headers=headers,
            json=json_payload,  # <--- THIS IS THE FIX
            auth=auth,
            timeout=10
        )

        if response.status_code == 201: # 201 Created
            new_ehr_id = response.json().get('ehr_id', {}).get('value')
            return new_ehr_id
        else:
            flash(f"Failed to create EHR: {response.status_code} - {response.text}", 'error')
            print(f"Failed to create EHR for {subject_id}: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        flash(f"EHRBase connection error during creation: {e}. Is server running?", 'error')
        print(f"Connection error creating EHR for {subject_id}: {e}")
        return None
    except Exception as e:
        flash(f"Unexpected error creating EHR: {e}", 'error')
        print(f"Unexpected error creating EHR for {subject_id}: {e}")
        return None
    
def post_composition(ehr_id, composition):
    """
    Posts a composition JSON/dict to the specified EHR in EHRBase.
    Returns: True on success (201), False otherwise.
    """
    ehrbase_config, _, _ = _load_ehrbase_config()
    if not ehrbase_config:
        flash("EHRBase configuration error in config.ini.", 'error')
        return False
    auth = _get_auth(ehrbase_config)
    url = f"{ehrbase_config['base_url']}/ehr/{ehr_id}/composition"
    headers = {'Accept': 'application/json; charset=UTF-8', 'Content-Type': 'application/json; charset=UTF-8', 'Prefer': 'return=representation'}
    try:
        response = requests.post(url, headers=headers, json=composition, auth=auth, timeout=15)
        if response.status_code == 201:
            print(f"Successfully posted composition to EHR {ehr_id}")
            return True
        else:
            flash(f"Error submitting composition: {response.status_code} - {response.text}", 'error')
            print(f"Error posting composition to EHR {ehr_id}: {response.status_code} - {response.text}")
            try: print(f"--- Failing Payload:\n{json.dumps(composition, indent=2)}\n---")
            except Exception: print("--- Could not serialize failing payload ---")
            return False
    except requests.exceptions.RequestException as e:
        flash(f"EHRBase connection error submitting composition: {e}. Is server running?", 'error')
        print(f"Connection error posting composition: {e}")
        return False
    except Exception as e:
        flash(f"Unexpected error submitting composition: {e}", 'error')
        print(f"Unexpected error posting composition: {e}")
        try: print(f"--- Failing Payload (Unexpected Error):\n{json.dumps(composition, indent=2)}\n---")
        except Exception: print("--- Could not serialize failing payload ---")
        return False

def get_ehr_compositions(ehr_id):
    """
    Retrieves all compositions for a given EHR ID from EHRBase using AQL.
    Returns: A list of compositions (as dictionaries) on success, empty list otherwise.
    """
    ehrbase_config, _, _ = _load_ehrbase_config()
    if not ehrbase_config:
        flash("EHRBase configuration error in config.ini.", 'error')
        return []
    auth = _get_auth(ehrbase_config)
    url = f"{ehrbase_config['base_url']}/query/aql"
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    aql_query = {"q": f"SELECT c FROM EHR [ehr_id/value='{ehr_id}'] CONTAINS COMPOSITION c"}
    print(f"Executing AQL query for EHR ID: {ehr_id}")
    try:
        response = requests.post(url, headers=headers, json=aql_query, auth=auth, timeout=15)
        if response.status_code == 200:
            results = response.json()
            compositions = results.get('rows', [])
            extracted = [row[0] for row in compositions if row and len(row) > 0]
            print(f"Found {len(extracted)} compositions for EHR {ehr_id}")
            return extracted
        else:
            flash(f"Error querying compositions: {response.status_code} - {response.text}", 'error')
            print(f"Error querying AQL for EHR {ehr_id}: {response.status_code} - {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        flash(f"EHRBase connection error querying compositions: {e}. Is server running?", 'error')
        print(f"Connection error querying AQL: {e}")
        return []
    except Exception as e:
        flash(f"An unexpected error occurred querying compositions: {e}", 'error')
        print(f"Unexpected error querying AQL for EHR {ehr_id}: {e}")
        return []
