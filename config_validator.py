import yaml
from typing import Dict, Any, List, Tuple
from default_schemas import *


def _check_keys_recursively(config: Dict[str, Any], schema: Dict[str, Any], path: str = "") -> List[str]:
    """Helper function to recursively check for missing keys."""
    missing = []
    for key, sub_schema in schema.items():
        current_path = f"{path}.{key}" if path else key
        if key not in config:
            missing.append(current_path)
        elif isinstance(sub_schema, dict) and isinstance(config.get(key), dict):
            # Recurse into nested dictionaries
            missing.extend(_check_keys_recursively(config[key], sub_schema, path=current_path))
    return missing

def validate_config_structure(file_path: str) -> Tuple[bool, List[str]]:
    """
    Validates the structure of a YAML configuration file based on its 'measurement_type'.

    Args:
        file_path (str): The path to the YAML configuration file.

    Returns:
        Tuple[bool, List[str]]: A tuple containing a boolean indicating validity
                                 and a list of human-readable error messages.
    """
    errors = []
    try:
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)
        if not isinstance(config, dict):
            return False, ["YAML content is not a valid dictionary."]
    except FileNotFoundError:
        return False, [f"File not found at '{file_path}'."]
    except yaml.YAMLError as e:
        return False, [f"Error parsing YAML file: {e}"]

    # 1. Validate against the base structure required for all types
    errors.extend(_check_keys_recursively(config, BASE_SCHEMA))

    # Stop if fundamental keys are missing
    if 'measurement_type' not in config:
        errors.append("Critical: 'measurement_type' key is missing. Cannot proceed with validation.")
        return False, errors

    measurement_type = config.get('measurement_type')
    
    # 2. Select and validate against the specific schema
    schemas = {
        'diodeIV': DIODE_IV_SCHEMA,
        'diodeCV': DIODE_CV_SCHEMA,
        'gcdmos': GCDMOS_SCHEMA,
        'strip': STRIP_SCHEMA
    }

    if measurement_type in schemas:
        errors.extend(_check_keys_recursively(config, schemas[measurement_type]))
    else:
        errors.append(f"Warning: No validation schema found for measurement_type '{measurement_type}'.")

    # 3. Apply special logical checks for 'gcdmos'
    if measurement_type == 'gcdmos':
        measurements = config.get('measurements', {})
        devices = config.get('devices', {})
        testset = measurements.get('testset', [])
        
        has_gcd = 'gcd' in testset
        has_mos = 'mos2000' in testset or 'moshalf' in testset

        if has_gcd and not has_mos: # Only GCD
            if 'IV' not in measurements:
                errors.append("For 'gcdmos' with 'gcd' in testset, 'measurements.IV' is required.")
        
        if has_mos and not has_gcd: # Only MOS
            if 'CV' not in measurements:
                errors.append("For 'gcdmos' with 'mos2000' or 'moshalf' in testset, 'measurements.CV' is required.")

        if has_gcd and has_mos: # Both
            if 'IV' not in measurements:
                errors.append("For 'gcdmos' with 'gcd' and MOS in testset, 'measurements.IV' is required.")
            if 'CV' not in measurements:
                errors.append("For 'gcdmos' with 'gcd' and MOS in testset, 'measurements.CV' is required.")
            if 'switch' not in devices:
                errors.append("For 'gcdmos' with 'gcd' and MOS in testset, 'devices.switch' is required.")

    if not errors:
        return True, []
    else:
        # Prepend "Missing key:" to make it clearer
        return False, [f"Missing key: {e}" for e in errors]


