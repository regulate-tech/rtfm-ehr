# --- app/blueprints/patient.py ---
from flask import (
    Blueprint,
    render_template,
    flash,
    current_app,
    get_flashed_messages,
)
from app.blueprints.forms import PatientSearchForm
from app import ehrbase_api
import psycopg2
import psycopg2.extras
import configparser
import os
import json
from app.composition_parser import parse_composition  # <-- 1. IMPORT THE PARSER
from app import get_node_map  # <-- IMPORT THE NODE MAP HELPER

bp = Blueprint("patient", __name__)


# --- Database Helper ---
def get_pmi_db_connection():
    config = configparser.ConfigParser()
    config_path = os.path.join(current_app.root_path, "..", "config.ini")
    if not os.path.exists(config_path):
        flash("Config file not found.", "error")
        return None
    config.read(config_path)
    if "pmi_database" not in config:
        flash("Missing [pmi_database] config.", "error")
        return None
    db_config = dict(config["pmi_database"])
    try:
        conn = psycopg2.connect(**db_config, cursor_factory=psycopg2.extras.DictCursor)
        return conn
    except psycopg2.Error as e:
        flash(f"DB connection error: {e}", "error")
        return None


def find_patient_in_pmi(criteria):
    """
    Searches PMI. Returns dict, None (not found), "Multiple", or False (error).
    * MODIFIED to not flash messages *
    """
    conn = get_pmi_db_connection()
    if not conn:
        return False
    cur = None
    patient = None
    try:
        cur = conn.cursor()
        sql = "SELECT * FROM patient_index WHERE "
        params = {}
        if criteria.get("nhs_number"):
            sql += "nhs_number = %(nhs_number)s"
            params["nhs_number"] = criteria["nhs_number"]
        elif all(k in criteria for k in ("given_name", "family_name", "date_of_birth")):
            sql += "LOWER(given_name)=LOWER(%(gn)s) AND LOWER(family_name)=LOWER(%(fn)s) AND date_of_birth=%(dob)s"
            params = {
                "gn": criteria["given_name"],
                "fn": criteria["family_name"],
                "dob": criteria["date_of_birth"],
            }
        else:
            flash("Invalid search.", "error")
            return False

        cur.execute(sql, params)
        results = cur.fetchall()

        if len(results) == 1:
            patient = dict(results[0])
        elif len(results) == 0:
            patient = None  # Return None for "not found"
        else:
            patient = "Multiple"  # Return "Multiple" for ambiguity

    except psycopg2.Error as e:
        flash(f"DB search error: {e}", "error")
        # This flash is OK (real error)
        patient = False
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
    return patient


# --- Route ---
@bp.route("/", methods=["GET", "POST"])
def search_my_records():
    """Handle patient search form and display results."""
    form = PatientSearchForm()
    patient_details, ehr_id, compositions = None, None, []
    search_performed = False

    anim_data = None
    final_msg = ""

    if form.validate_on_submit():
        search_performed = True
        criteria = {}
        if form.nhs_number.data:
            criteria["nhs_number"] = form.nhs_number.data
            print(f"Patient: Search NHS {criteria['nhs_number']}")
        else:
            criteria = {
                "given_name": form.given_name.data,
                "family_name": form.family_name.data,
                "date_of_birth": form.date_of_birth.data,
            }
            print(
                f"Patient: Search Name/DOB {criteria['given_name']} {criteria['family_name']}"
            )

        # --- 1. Define Animation Steps (Always play animation) ---
        steps_list = [
            [
                "You",
                "PMI Database",
                "1. Search patient master index for my details...",
                "request",
            ],
            [
                "PMI Database",
                "EHR Manager",
                "2. Look for an associated Electronic Health Record...",
                "request",
            ],
            [
                "You",
                "EHR Manager",
                "3. EHR Manager sends back any records it found...",
                "response",
            ],
        ]
        anim_data = json.dumps(steps_list)

        # --- 2. Perform Search ---
        patient_details = find_patient_in_pmi(criteria)

        # --- 3. Set Final Message Based on Result ---
        if patient_details and isinstance(patient_details, dict):
            # --- SUCCESS: RECORD FOUND ---
            final_msg = "Search complete. Displaying results."
            pmi_nhs = patient_details.get("nhs_number")
            print(f"Patient: Found PMI {pmi_nhs}")
            if pmi_nhs:
                ehr_id_res = ehrbase_api.check_ehr_exists(pmi_nhs)
                if ehr_id_res is False:
                    print(f"Patient: API error check EHR {pmi_nhs}")
                elif ehr_id_res is None:
                    flash(
                        "Your patient record was found, but no associated Electronic Health Record exists yet.",
                        "info",
                    )
                    print(f"Patient: No EHR for {pmi_nhs}")
                    final_msg = (
                        "PMI record found. No EHR exists."  # More specific message
                    )
                else:
                    ehr_id = ehr_id_res
                    print(f"Patient: Found EHR {ehr_id}. Fetching...")
                    comps_res = ehrbase_api.get_ehr_compositions(ehr_id)
                    if comps_res:
                        compositions = comps_res
                        for c in compositions:
                            c["parsed_data"] = parse_composition(c)
                            c["pretty_json"] = json.dumps(c, indent=2)
                        print(f"Patient: Got {len(compositions)} comps.")
                    elif not get_flashed_messages(["error"]):
                        flash(
                            "Your Electronic Health Record was found, but it contains no entries yet.",
                            "info",
                        )
                        print(f"Patient: No comps for {ehr_id}")
                        final_msg = (
                            "EHR found, but it is empty."  # More specific message
                        )
            else:
                flash("PMI record missing NHS number, cannot check EHR.", "warning")
                final_msg = (
                    "PMI record found, but has no NHS Number."  # More specific message
                )

        elif patient_details is None:
            # --- FAIL: NOT FOUND ---
            final_msg = "Record not found."
            patient_details = None  # Ensure it's None for the template

        elif patient_details == "Multiple":
            # --- FAIL: MULTIPLE FOUND ---
            final_msg = "Multiple records match. Please search by NHS Number."
            patient_details = None  # Don't show any results

        elif patient_details is False:
            # --- FAIL: DB ERROR ---
            final_msg = "A search error occurred. See message above."
            patient_details = None  # Don't show any results

    return render_template(
        "patient/patient_home.html",  # Use subdirectory path
        title="Patient Record View",
        form=form,
        patient=patient_details if isinstance(patient_details, dict) else None,
        ehr_id=ehr_id,
        compositions=compositions,
        search_performed=search_performed,
        animation_data=anim_data,
        final_message=final_msg,
        node_map_data=get_node_map(),
    )