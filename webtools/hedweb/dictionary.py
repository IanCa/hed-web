from flask import current_app
from werkzeug.utils import secure_filename

from hed import models
from hed import schema as hedschema
from hed.errors.error_reporter import get_printable_issue_string
from hed.errors.exceptions import HedFileError
from hedweb.constants import common, file_constants
from hedweb.utils.web_utils import form_has_option, get_hed_schema_from_pull_down
from hedweb.utils.io_utils import generate_filename

app_config = current_app.config


def generate_input_from_dictionary_form(request):
    """Gets the validation function input arguments from a request object associated with the validation form.

    Parameters
    ----------
    request: Request object
        A Request object containing user data from the validation form.

    Returns
    -------
    dictionary
        A dictionary containing input arguments for calling the underlying validation function.
    """
    arguments = {
        common.SCHEMA: None,
        common.JSON_DICTIONARY: None,
        common.JSON_DISPLAY_NAME: '',
        common.COMMAND: request.values.get(common.COMMAND_OPTION, None),
        common.CHECK_FOR_WARNINGS: form_has_option(request, common.CHECK_FOR_WARNINGS, 'on')
    }
    arguments[common.SCHEMA] = get_hed_schema_from_pull_down(request)
    if common.JSON_FILE in request.files:
        f = request.files[common.JSON_FILE]
        arguments[common.JSON_DISPLAY_NAME] = secure_filename(f.filename)
        arguments[common.JSON_DICTIONARY] = \
            models.ColumnDefGroup(json_string=f.read(file_constants.BYTE_LIMIT).decode('ascii'))
    return arguments


def dictionary_process(arguments):
    """Perform the requested action for the dictionary.

    Parameters
    ----------
    arguments: dict
        A dictionary with the input arguments from the dictionary form

    Returns
    -------
      dict
        A dictionary of results.
    """
    hed_schema = arguments.get('schema', None)
    if not hed_schema or not isinstance(hed_schema, hedschema.hed_schema.HedSchema):
        raise HedFileError('BadHedSchema', "Please provide a valid HedSchema", "")
    json_dictionary = arguments.get(common.JSON_DICTIONARY, 'None')
    if not json_dictionary or not isinstance(json_dictionary, models.ColumnDefGroup):
        raise HedFileError('InvalidJSONFile', "Please give a valid JSON file to process", "")
    elif not arguments[common.COMMAND]:
        raise HedFileError('MissingCommand', 'Command is missing', '')
    if arguments[common.COMMAND] == common.COMMAND_VALIDATE:
        results = dictionary_validate(hed_schema, json_dictionary)
    elif arguments[common.COMMAND] == common.COMMAND_TO_SHORT:
        results = dictionary_convert(hed_schema, json_dictionary, command=common.COMMAND_TO_SHORT)
    elif arguments[common.COMMAND] == common.COMMAND_TO_LONG:
        results = dictionary_convert(hed_schema, json_dictionary)
    else:
        raise HedFileError('UnknownProcessingMethod', "Select a dictionary processing method", "")
    return results


def dictionary_convert(hed_schema, json_dictionary, command=common.COMMAND_TO_LONG):
    """Converts a dictionary from short to long unless short_to_long is set to False, then long_to_short

    Parameters
    ----------
    hed_schema:HedSchema
        HedSchema object to be used
    json_dictionary: ColumnDefGroup
        Previously created ColumnDefGroup
    command: str

    Returns
    -------
    dict
        A downloadable dictionary file or a file containing warnings
    """

    schema_version = hed_schema.header_attributes.get('version', 'Unknown version')
    results = dictionary_validate(hed_schema, json_dictionary)
    if results['data']:
        return results
    if command == common.COMMAND_TO_LONG:
        suffix = '_to_long'
    else:
        suffix = '_to_short'
    issues = []
    for column_def in json_dictionary:
        for hed_string, position in column_def.hed_string_iter(include_position=True):
            hed_string_obj = models.HedString(hed_string)
            if suffix == '_to_long':
                errors = hed_string_obj.convert_to_long(hed_schema)
            else:
                errors = hed_string_obj.convert_to_short(hed_schema)
                column_def.set_hed_string(hed_string_obj, position)
            issues = issues + errors
            column_def.set_hed_string(hed_string_obj, position)

    # issues = ErrorHandler.filter_issues_by_severity(issues, ErrorSeverity.ERROR)

    if issues:
        issue_str = get_printable_issue_string(issues,
                                               f"JSON conversion for {json_dictionary.display_name} was unsuccessful")
        file_name = generate_filename(json_dictionary.display_name,
                                      suffix=f"{suffix}_conversion_errors", extension='.txt')
        return {'command': command, 'data': issue_str, 'output_display_name': file_name,
                'schema_version': schema_version, 'msg_category': 'warning',
                'msg': 'JSON file had validation errors'}
    else:
        file_name = generate_filename(json_dictionary.display_name, suffix=suffix, extension='.json')
        data = json_dictionary.get_as_json_string()
        return {'command': command, 'data': data, 'output_display_name': file_name,
                'schema_version': schema_version, 'msg_category': 'success',
                'msg': 'JSON dictionary was successfully converted'}


def dictionary_validate(hed_schema, json_dictionary, display_name='json_dictionary'):
    """ Validates the dictionary and returns the errors and/or a message in a dictionary

    Parameters
    ----------
    hed_schema: str or HedSchema
        Version number or path or HedSchema object to be used
    json_dictionary: ColumnDefGroup
        Dictionary object
    display_name: str
        String used to identify the dictionary in messages and filenames


    Returns
    -------
    dict
        dictionary of response values.
    """

    schema_version = hed_schema.header_attributes.get('version', 'Unknown version')
    if not json_dictionary or not isinstance(json_dictionary, models.ColumnDefGroup):
        raise HedFileError('BadDictionaryFile', "Please provide a dictionary to process", "")

    def_dict, issues = json_dictionary.extract_defs()
    if issues:
        issue_str = get_printable_issue_string(issues,
                                               f"{json_dictionary.display_name} JSON dictionary definition errors")
        file_name = generate_filename(display_name, suffix='_dictionary_errors', extension='.txt')
        return {'command': 'command_validate', 'data': issue_str, 'output_display_name': file_name,
                'schema_version': schema_version, 'msg_category': 'warning',
                'msg': "JSON dictionary had definition errors"}

    issues = json_dictionary.validate_entries(hed_schema)
    if issues:
        issue_str = get_printable_issue_string(issues, f"HED validation errors for dictionary {display_name}")
        file_name = generate_filename(display_name, suffix='validation_errors', extension='.txt')
        return {'command': 'command_validate', 'data': issue_str, 'output_display_name': file_name,
                'schema_version': schema_version, 'msg_category': 'warning',
                'msg': 'JSON dictionary had validation errors'}
    else:
        return {'command': 'command_validate', 'data': '',
                'schema_version': schema_version, 'msg_category': 'success',
                'msg': 'JSON file had no validation errors'}
