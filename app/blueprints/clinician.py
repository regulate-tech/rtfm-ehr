# --- app/blueprints/clinician.py ---
from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    current_app,
    get_flashed_messages,
)
from app.blueprints.forms import SearchPmiForm
from app import ehrbase_api
import json
from app.composition_parser import parse_composition
from app import get_node_map  # <-- 1. IMPORT NODE MAP HELPER

bp = Blueprint("clinician", __name__)


@bp.route("/", methods=["GET", "POST"])
def home():
    """Search for EHR and display compositions."""
    form = SearchPmiForm()
    ehr_id, searched_nhs, compositions, error_msg = None, None, [], None

    # 2. INITIALIZE ANIMATION VARS
    anim_data = None
    final_msg = ""

    if form.validate_on_submit():
        nhs = form.nhs_number.data
        searched_nhs = nhs

        # 3. DEFINE ANIMATION STEPS
        steps_list = [
            [
                "You",
                "EHR Manager",
                "1. Clinician device sends query to the EHR Manager...",
                "request",
            ],
            [
                "You",
                "EHR Manager",
                "2. EHR Manager sends back any data it finds...",
                "response",
            ],
        ]
        anim_data = json.dumps(steps_list)

        # --- 4. SET FINAL_MSG BASED ON OUTCOME ---
        ehr_id_res = ehrbase_api.check_ehr_exists(nhs)

        if ehr_id_res is False:
            error_msg = "API/Config error checking EHR."
            final_msg = error_msg  # Set final message for animation

        elif ehr_id_res is None:
            error_msg = f"No EHR for {nhs}."
            final_msg = error_msg  # Set final message for animation

        else:
            ehr_id = ehr_id_res
            comps_res = ehrbase_api.get_ehr_compositions(ehr_id)
            if comps_res:
                compositions = comps_res
                for c in compositions:
                    c["parsed_data"] = parse_composition(c)
                    c["pretty_json"] = json.dumps(c, indent=2)

                # Set final message for animation
                final_msg = f"Displaying {len(compositions)} entries for EHR {ehr_id}."

            elif not get_flashed_messages(category_filter=["error"]):
                # Set final message for animation
                final_msg = f"No entries found in EHR {ehr_id}."

    # Use subdirectory in template path
    return render_template(
        "clinician/clinician_home.html",
        title="Clinician View",
        form=form,
        ehr_id=ehr_id,
        searched_nhs=searched_nhs,
        compositions=compositions,
        error_message=error_msg,
        animation_data=anim_data,  # <-- 5. PASS VARS
        final_message=final_msg,  # <-- 5. PASS VARS
        node_map_data=get_node_map(),  # <-- 5. PASS VARS
    )