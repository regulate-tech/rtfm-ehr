# --- app/blueprints/data_entry.py (Cleaned) ---
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, get_flashed_messages
from app.blueprints.forms import DataEntrySearchForm, VitalSignsForm, CsrfOnlyForm
from app import ehrbase_api
import datetime
import uuid
import json
import random
from app import get_node_map  # <-- Import our helper

bp = Blueprint('data_entry', __name__)

# --- Composition Helper 2 (Clinic Check) ---
def create_clinic_check_composition(systolic_value, diastolic_value):
    """
    Creates the openEHR Composition dictionary for Blood Pressure
    based on the clinic_check.opt template structure, applying
    validated JSON structure.
    """
    current_time_iso = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds')
    composition_uuid = str(uuid.uuid4())

    composition = {
        "_type": "COMPOSITION",
        "name": {
            "_type": "DV_TEXT",
            "value": "Clinic Check for BP"
        },
        "archetype_node_id": "openEHR-EHR-COMPOSITION.encounter.v1",
        "category": {
            "value": "event",
            "defining_code": {
                "terminology_id": {"value": "openehr"},
                "code_string": "433"
            }
        },
        "archetype_details": {
            "archetype_id": {"value": "openEHR-EHR-COMPOSITION.encounter.v1"},
            "template_id": {"value": "clinic_check"},
            "rm_version": "1.0.2"
        },
        "language": {
            "code_string": "en",
            "terminology_id": {"value": "ISO_639-1"}
        },
        "territory": {
            "code_string": "GB",
            "terminology_id": {"value": "ISO_3166-1"}
        },
        "composer": {
            "_type": "PARTY_IDENTIFIED",
            "name": "Data Entry User"
        },
        "context": {
            "start_time": {"value": current_time_iso},
            "setting": {
                "defining_code": {
                    "code_string": "238",
                    "terminology_id": {"value": "openehr"}
                },
                "value": "other care"
            }
        },
        "content": [
            {
                "_type": "OBSERVATION",
                "archetype_node_id": "openEHR-EHR-OBSERVATION.blood_pressure.v2",
                "name": {
                    "_type": "DV_TEXT",
                    "value": "Blood pressure"
                },
                "archetype_details": {
                    "archetype_id": {"value": "openEHR-EHR-OBSERVATION.blood_pressure.v2"},
                    "rm_version": "1.0.2"
                },
                "language": {
                    "code_string": "en",
                    "terminology_id": {"value": "ISO_639-1"}
                },
                "encoding": {
                    "code_string": "UTF-8",
                    "terminology_id": {"value": "IANA_character-sets"}
                },
                "subject": {"_type": "PARTY_SELF"},
                "data": {
                    "_type": "HISTORY",
                    "archetype_node_id": "at0001",
                    "name": {
                        "_type": "DV_TEXT",
                        "value": "History"
                    },
                    "origin": {"value": current_time_iso},
                    "events": [
                        {
                            "_type": "POINT_EVENT",
                            "archetype_node_id": "at0006",
                            "name": {
                                "_type": "DV_TEXT",
                                "value": "Any event"
                            },
                            "time": {"value": current_time_iso},
                            "data": {
                                "_type": "ITEM_TREE",
                                "archetype_node_id": "at0003",
                                "name": {
                                    "_type": "DV_TEXT",
                                    "value": "blood pressure"
                                },
                                "items": [
                                    {
                                        "_type": "ELEMENT",
                                        "archetype_node_id": "at0004",
                                        "name": {
                                            "_type": "DV_TEXT",
                                            "value": "Systolic"
                                        },
                                        "value": {
                                            "_type": "DV_QUANTITY",
                                            "magnitude": float(systolic_value),
                                            "units": "mm[Hg]"
                                        }
                                    },
                                    {
                                        "_type": "ELEMENT",
                                        "archetype_node_id": "at0005",
                                        "name": {
                                            "_type": "DV_TEXT",
                                            "value": "Diastolic"
                                        },
                                        "value": {
                                            "_type": "DV_QUANTITY",
                                            "magnitude": float(diastolic_value),
                                            "units": "mm[Hg]"
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        ]
    }
    return composition

# --- Composition Helper 3 (HbA1c) ---
def create_hba1c_composition(hba1c_value):
    """
    Creates the openEHR Composition dictionary for an HbA1c lab result,
    matching the validated template structure.
    """
    current_time_iso = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='milliseconds')
    composition_uuid = str(uuid.uuid4())

    composition = {
        "_type": "COMPOSITION",
        "name": {
            "_type": "DV_TEXT",
            "value": "Lab Test Results"
        },
        "archetype_node_id": "openEHR-EHR-COMPOSITION.report.v1",
        "category": {
            "value": "event",
            "defining_code": {
                "terminology_id": {"value": "openehr"},
                "code_string": "433"
            }
        },
        "archetype_details": {
            "archetype_id": {"value": "openEHR-EHR-COMPOSITION.report.v1"},
            "template_id": {"value": "lab_result_hba1c"},
            "rm_version": "1.0.2"
        },
        "language": {
            "code_string": "en",
            "terminology_id": {"value": "ISO_639-1"}
        },
        "territory": {
            "code_string": "GB",
            "terminology_id": {"value": "ISO_3166-1"}
        },
        "composer": {
            "_type": "PARTY_IDENTIFIED",
            "name": "Automated Lab System"
        },
        "context": {
            "start_time": {"value": current_time_iso},
            "setting": {
                "defining_code": {
                    "code_string": "238",
                    "terminology_id": {"value": "openehr"}
                },
                "value": "other care"
            }
        },
        "content": [
            {
                "_type": "OBSERVATION",
                "archetype_node_id": "openEHR-EHR-OBSERVATION.laboratory_test_result.v1",
                "name": {
                    "_type": "DV_TEXT",
                    "value": "Laboratory test result"
                },
                "archetype_details": {
                    "archetype_id": {"value": "openEHR-EHR-OBSERVATION.laboratory_test_result.v1"},
                    "rm_version": "1.0.2"
                },
                "language": {
                    "code_string": "en",
                    "terminology_id": {"value": "ISO_639-1"}
                },
                "encoding": {
                    "code_string": "UTF-8",
                    "terminology_id": {"value": "IANA_character-sets"}
                },
                "subject": {"_type": "PARTY_SELF"},
                "data": {
                    "_type": "HISTORY",
                    "archetype_node_id": "at0001",
                    "name": {
                        "_type": "DV_TEXT",
                        "value": "Event Series"
                    },
                    "origin": {"value": current_time_iso},
                    "events": [
                        {
                            "_type": "POINT_EVENT",
                            "archetype_node_id": "at0002",
                            "name": {
                                "_type": "DV_TEXT",
                                "value": "Any event"
                            },
                            "time": {"value": current_time_iso},
                            "data": {
                                "_type": "ITEM_TREE",
                                "archetype_node_id": "at0003",
                                "name": {
                                    "_type": "DV_TEXT",
                                    "value": "Tree"
                                },
                                "items": [
                                    {
                                        "_type": "ELEMENT",
                                        "archetype_node_id": "at0005",
                                        "name": {
                                            "_type": "DV_TEXT",
                                            "value": "Test name"
                                        },
                                        "value": {
                                            "_type": "DV_TEXT",
                                            "value": "HbA1c"
                                        }
                                    },
                                    {
                                        "_type": "CLUSTER",
                                        "archetype_node_id": "openEHR-EHR-CLUSTER.laboratory_test_analyte.v1",
                                        "name": {
                                            "_type": "DV_TEXT",
                                            "value": "Laboratory analyte result"
                                        },
                                        "archetype_details": {
                                            "archetype_id": {"value": "openEHR-EHR-CLUSTER.laboratory_test_analyte.v1"},
                                            "rm_version": "1.0.2"
                                        },
                                        "items": [
                                            {
                                                "_type": "ELEMENT",
                                                "archetype_node_id": "at0024",
                                                "name": {
                                                    "_type": "DV_TEXT",
                                                    "value": "Analyte name"
                                                },
                                                "value": {
                                                    "_type": "DV_TEXT",
                                                    "value": "HbA1c"
                                                }
                                            },
                                            {
                                                "_type": "ELEMENT",
                                                "archetype_node_id": "at0001",
                                                "name": {
                                                    "_type": "DV_TEXT",
                                                    "value": "Analyte result"
                                                },
                                                "value": {
                                                    "_type": "DV_QUANTITY",
                                                    "magnitude": round(hba1c_value, 1),
                                                    "units": "mmol"
                                                }
                                            }
                                        ]
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        ]
    }
    return composition

# --- Routes ---

@bp.route('/', methods=['GET', 'POST'])
def search():
    """Search for EHR to enter data."""
    form = DataEntrySearchForm()
    if form.validate_on_submit():
        nhs = form.nhs_number.data
        ehr_id = ehrbase_api.check_ehr_exists(nhs)
        if ehr_id is False: 
            return render_template('data_entry/search_data_entry.html', title='Find Patient EHR', form=form)
        elif ehr_id is None:
            flash(f"No EHR for {nhs}. Create one via Admin.", 'warning')
            return render_template('data_entry/search_data_entry.html', title='Find Patient EHR', form=form)
        else:
            return redirect(url_for('data_entry.dashboard', ehr_id=ehr_id, nhs_number=nhs))
            
    return render_template('data_entry/search_data_entry.html', title='Find Patient EHR', form=form)


@bp.route('/dashboard/<ehr_id>/<nhs_number>')
def dashboard(ehr_id, nhs_number):
    """
    Shows data entry options for a specific patient.
    """
    form = CsrfOnlyForm()
    return render_template(
        'data_entry/data_entry_dashboard.html',
        title='Patient Data Entry',
        ehr_id=ehr_id,
        nhs_number=nhs_number,
        form=form
    )

# --- Clinic Check Route ---
@bp.route('/enter_clinic_check/<ehr_id>', methods=['GET', 'POST'])
def enter_clinic_check(ehr_id):
    """Display form and handle submission for clinic_check template."""
    form = VitalSignsForm()
    nhs = request.args.get('nhs_number', '')

    # These will be 'None' or empty on a GET request
    anim_data = None
    final_msg = ""
    
    if form.validate_on_submit():
        systolic, diastolic = form.systolic.data, form.diastolic.data
        try:
            composition = create_clinic_check_composition(systolic, diastolic)
            success = ehrbase_api.post_composition(ehr_id, composition)
            
            if success:
                # 1. Set the final message for the animation
                final_msg = f"Clinic Check BP submitted for EHR ID: {ehr_id}"
                
                # 2. Define the animation steps
                steps_list = [
                    ['You', 'EHR Manager', '1. Your PC sends data to the EHR Manager via an API call.', 'request'],
                    ['EHR Manager', 'EHR Database', '2. The EHR Manager accepts the data and writes it to the EHR database...', 'request'],
                    ['EHR Manager', 'You', '3. The EHR Manager sends you a confirmation that it has add the record..', 'response']
                ]
                anim_data = json.dumps(steps_list)
                
                # 3. (REMOVED) We no longer redirect or flash.
                # The code will now fall through to the render_template
                # call below, which is what we want.
                
            else:
                # Handle the case where the API call itself fails
                flash("EHR API call failed. Composition not saved.", "error")

        except Exception as e:
            flash(f"Error creating/posting composition: {e}", 'error')
            print(f"Comp error: {e}")
            
    # This render_template is now used for both GET and POST
    return render_template(
        'data_entry/enter_clinic_check.html',
        title='Enter Clinic Check Vitals',
        animation_data=anim_data,
        final_message=final_msg,
        node_map_data=get_node_map(),
        form=form,
        ehr_id=ehr_id,
        nhs_number=nhs
    )

# --- HbA1c Generator Route ---
@bp.route('/generate_hba1c/<ehr_id>/<nhs_number>', methods=['POST'])
def generate_hba1c(ehr_id, nhs_number):
    """
    Auto-generates a random HbA1c lab result and posts it.
    """
    form = CsrfOnlyForm()
    if form.validate_on_submit():
        try:
            hba1c_val = random.uniform(30.0, 50.0)
            composition = create_hba1c_composition(hba1c_val)
            success = ehrbase_api.post_composition(ehr_id, composition)
            
            if success:
                flash(f"Generated HbA1c result ({hba1c_val:.1f} mmol) for EHR {ehr_id}", "success")
        except Exception as e:
            flash(f"Error generating/posting HbA1c: {e}", 'error')
            print(f"HbA1c Comp error: {e}")
    else:
        flash("Invalid request (CSRF token missing or expired).", "error")
        
    return redirect(url_for('data_entry.dashboard', ehr_id=ehr_id, nhs_number=nhs_number))
