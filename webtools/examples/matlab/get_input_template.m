function s = get_input_template()

s = struct('service', [], ...
           'schema_version', [], 'schema_string', [], 'schema_url', [], ...
           'json_string', [], 'events_string', [], ...
           'spreadsheet_string', [], 'string_list', [], ...
           'check_for_warnings', [], 'defs_expand', []);