# --- app/blueprints/clinician.py ---
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, get_flashed_messages
from app.blueprints.forms import SearchPmiForm
from app import ehrbase_api
import json
from app.composition_parser import parse_composition # <-- IMPORT THE PARSER

bp = Blueprint('clinician', __name__) # Remember to remove template_folder

@bp.route('/', methods=['GET', 'POST'])
def home():
    """Search for EHR and display compositions."""
    form = SearchPmiForm()
    ehr_id, searched_nhs, compositions, error_msg = None, None, [], None
    if form.validate_on_submit():
        nhs = form.nhs_number.data; searched_nhs = nhs
        ehr_id_res = ehrbase_api.check_ehr_exists(nhs)
        if ehr_id_res is False: error_msg = "API/Config error checking EHR."
        elif ehr_id_res is None: flash(f"No EHR found for {nhs}.", 'warning'); error_msg = f"No EHR for {nhs}."
        else:
            ehr_id = ehr_id_res
            comps_res = ehrbase_api.get_ehr_compositions(ehr_id)
            if comps_res:
                 compositions = comps_res
                 for c in compositions:
                     # --- THIS IS THE CHANGE ---
                     # 1. Parse the composition to get key data
                     c['parsed_data'] = parse_composition(c)
                     # 2. Keep the raw JSON for the <details> block
                     c['pretty_json'] = json.dumps(c, indent=2)
                     
                 flash(f"Displaying {len(compositions)} entries for EHR {ehr_id}.", 'info')
            elif not get_flashed_messages(category_filter=['error']):
                 flash(f"No entries found in EHR {ehr_id}.", 'info')

    # Use subdirectory in template path
    return render_template(
        'clinician/clinician_home.html',
        title='Clinician View',
        form=form,
        ehr_id=ehr_id,
        searched_nhs=searched_nhs,
        compositions=compositions,
        error_message=error_msg
    )
