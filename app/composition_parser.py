# --- app/composition_parser.py ---

def parse_composition(composition_json):
    """
    Main parser function.
    It checks the template_id and calls the correct sub-parser.
    """
    try:
        template_id = composition_json.get('archetype_details', {}).get('template_id', {}).get('value')
        
        if template_id == 'lab_result_hba1c':
            return _parse_hba1c(composition_json)
        elif template_id == 'clinic_check':
            return _parse_clinic_check(composition_json)
        elif template_id == 'Vital Signs Encounter (Composition)': # Handle the old template
            return _parse_vital_signs(composition_json)
        else:
            return [] # Return empty list for unknown templates
    except Exception as e:
        print(f"Error parsing composition: {e}")
        return []

def _parse_hba1c(comp):
    """Parses an HbA1c lab result composition."""
    results = []
    try:
        # Navigate the path to the analyte cluster
        # content[0] -> data -> events[0] -> data -> items[1] (the cluster)
        cluster = comp.get('content', [{}])[0].get('data', {}).get('events', [{}])[0].get('data', {}).get('items', [])[1]
        
        # Find the analyte result within the cluster's items
        for item in cluster.get('items', []):
            if item.get('archetype_node_id') == 'at0001': # 'Analyte result'
                value_obj = item.get('value', {})
                name = item.get('name', {}).get('value', 'HbA1c')
                magnitude = value_obj.get('magnitude')
                units = value_obj.get('units')
                
                if magnitude is not None and units:
                    results.append({
                        'name': name,
                        'value': magnitude,
                        'units': units
                    })
        return results
    except Exception as e:
        print(f"Error in _parse_hba1c: {e}")
        return []

def _parse_clinic_check(comp):
    """Parses a clinic_check (BP) composition."""
    results = []
    try:
        # content[0] -> data -> events[0] -> data -> items
        items = comp.get('content', [{}])[0].get('data', {}).get('events', [{}])[0].get('data', {}).get('items', [])
        
        for item in items:
            node_id = item.get('archetype_node_id')
            value_obj = item.get('value', {})
            
            if node_id == 'at0004': # Systolic
                name = 'Systolic'
                magnitude = value_obj.get('magnitude')
                units = value_obj.get('units')
            elif node_id == 'at0005': # Diastolic
                name = 'Diastolic'
                magnitude = value_obj.get('magnitude')
                units = value_obj.get('units')
            else:
                continue # Skip other items
                
            if magnitude is not None and units:
                results.append({
                    'name': name,
                    'value': magnitude,
                    'units': units
                })
        return results
    except Exception as e:
        print(f"Error in _parse_clinic_check: {e}")
        return []

def _parse_vital_signs(comp):
    """Parses the old vital_signs (BP) composition (with SECTION)."""
    results = []
    try:
        # content[0] (SECTION) -> items[0] (OBSERVATION) -> data -> events[0] -> data -> items
        items = comp.get('content', [{}])[0].get('items', [{}])[0].get('data', {}).get('events', [{}])[0].get('data', {}).get('items', [])
        
        for item in items:
            node_id = item.get('archetype_node_id')
            value_obj = item.get('value', {})
            
            if node_id == 'at0004': # Systolic
                name = 'Systolic'
                magnitude = value_obj.get('magnitude')
                units = value_obj.get('units')
            elif node_id == 'at0005': # Diastolic
                name = 'Diastolic'
                magnitude = value_obj.get('magnitude')
                units = value_obj.get('units')
            else:
                continue # Skip other items
                
            if magnitude is not None and units:
                results.append({
                    'name': name,
                    'value': magnitude,
                    'units': units
                })
        return results
    except Exception as e:
        print(f"Error in _parse_vital_signs: {e}")
        return []
