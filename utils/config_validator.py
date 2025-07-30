import yaml
from typing import Dict, Any, List, Tuple
from config.default_schemas import *
import sys


schemas = {
        'diodeIV': DIODE_IV_SCHEMA,
        'diodeCV': DIODE_CV_SCHEMA,
        'gcdmos': GCDMOS_SCHEMA,
        'strip': STRIP_SCHEMA
    }


def _handle_errors(errors: List[str]):
    print("Configuration file has errors:")
    for e in errors:
        print(f"- Missing key: {e}")

    a = input("Config has errors. Would you like to continue anyway? (y/n): ")
    if a.lower() != 'y':
        print("Exiting due to configuration errors.")
        sys.exit(1)


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


def validate_config_structure(file_path: str) -> Dict[str, Any]:
    """
    Loads and validates a YAML configuration file. Interacts with user if errors are found.

    Args:
        file_path (str): The path to the YAML configuration file.

    Returns:
        Dict[str, Any]: The parsed configuration dictionary if valid or approved by user.
    """
    errors = []

    try:
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)
        if not isinstance(config, dict):
            print("YAML content is not a valid dictionary.")
            sys.exit(1)
    except FileNotFoundError:
        print(f"File not found at '{file_path}'.")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        sys.exit(1)

    # Print YAML nicely
    print("Parsed configuration:\n")
    print(yaml.dump(config, default_flow_style=False))

    # Validate against base schema
    errors.extend(_check_keys_recursively(config, BASE_SCHEMA))

    if 'measurement_type' not in config:
        errors.append("Critical: 'measurement_type' key is missing. Cannot proceed with validation.")
        _handle_errors(errors)

    measurement_type = config.get('measurement_type')
    if measurement_type in schemas:
        errors.extend(_check_keys_recursively(config, schemas[measurement_type]))
    else:
        errors.append(f"Warning: No validation schema found for measurement_type '{measurement_type}'.")

    # GCDMOS logic
    if measurement_type == 'gcdmos':
        measurements = config.get('measurements', {})
        devices = config.get('devices', {})
        testset = measurements.get('testset', [])

        has_gcd = 'gcd' in testset
        has_mos = 'mos2000' in testset or 'moshalf' in testset

        if has_gcd and not has_mos:
            if 'IV' not in measurements:
                errors.append("For 'gcdmos' with 'gcd' in testset, 'measurements.IV' is required.")
        if has_mos and not has_gcd:
            if 'CV' not in measurements:
                errors.append("For 'gcdmos' with 'mos2000' or 'moshalf' in testset, 'measurements.CV' is required.")
        if has_gcd and has_mos:
            if 'IV' not in measurements:
                errors.append("For 'gcdmos' with both, 'measurements.IV' is required.")
            if 'CV' not in measurements:
                errors.append("For 'gcdmos' with both, 'measurements.CV' is required.")
            if 'switch' not in devices:
                errors.append("For 'gcdmos' with both, 'devices.switch' is required.")

    # Irradiation
    if 'irradiation' in config:
        if not isinstance(config['irradiation'], dict):
            errors.append("'irradiation' should be a dictionary.")
        else:
            errors.extend(_check_keys_recursively(config['irradiation'], IRRADIATION_SCHEMA, path='irradiation'))

    # Exclusivity check: cannot have both irradiation and annealing
    if 'irradiation' in config and 'annealing' in config:
        errors.append("Invalid configuration: 'irradiation' and 'annealing' cannot both be present. continuing will only run irradiation loop.")
    
    if 'annealing' in config:
        if not isinstance(config['annealing'], dict):
            errors.append("'annealing' should be a dictionary.")
        else:
            errors.extend(_check_keys_recursively(config['annealing'], ANNEALING_SCHEMA, path='annealing'))

    # Final error handling
    if errors:
        _handle_errors(errors)
    else:
        print("Configuration matches schema. Proceeding.")

    return config  # return parsed config for later use
