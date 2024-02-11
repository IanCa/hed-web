import os
from io import StringIO
import pandas as pd
import unittest
from werkzeug.test import create_environ
from werkzeug.wrappers import Request

from tests.test_web_base import TestWebBase
from hed.schema import HedSchema, load_schema
from hed.models import Sidecar, TabularInput
from hed.errors.exceptions import HedFileError
from hedweb.constants import base_constants
from hedweb.process_events import ProcessEvents


class Test(TestWebBase):
    cache_schemas = True

    def get_event_proc(self, events_file, sidecar_file, schema_file):
        events_proc = ProcessEvents()
        if schema_file:
            schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), schema_file)
            events_proc.schema = load_schema(schema_path)
        if sidecar_file:
            events_proc.sidecar = Sidecar(files=os.path.join(os.path.dirname(os.path.abspath(__file__)), sidecar_file))
        if events_file:
            events_proc.events = TabularInput(file=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                                events_file), sidecar=events_proc.sidecar)
        events_proc.expand_defs = True
        events_proc.columns_categorical = []
        events_proc.columns_value = []
        events_proc.check_for_warnings = True
        return events_proc

    def test_set_input_from_events_form_empty(self):
        with self.assertRaises(HedFileError):
            with self.app.app_context():
                proc_events = ProcessEvents()
                proc_events.process()

    def test_set_input_from_events_form(self):
        sidecar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.json')
        events_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data/bids_events.tsv')
        with self.app.app_context():

            with open(sidecar_path, 'rb') as fp:
                with open(events_path, 'rb') as fpe:
                    environ = create_environ(data={base_constants.SIDECAR_FILE: fp,
                                                   base_constants.SCHEMA_VERSION: '8.2.0',
                                                   base_constants.EVENTS_FILE: fpe, base_constants.EXPAND_DEFS: 'on',
                                                   base_constants.COMMAND_OPTION: base_constants.COMMAND_ASSEMBLE})
            request = Request(environ)
            event_proc = ProcessEvents()
            event_proc.set_input_from_form(request)
            self.assertIsInstance(event_proc.events, TabularInput,"should have an events object")
            self.assertIsInstance(event_proc.schema, HedSchema,"should have a HED schema")
            self.assertEqual(event_proc.command, base_constants.COMMAND_ASSEMBLE,"should have correct command")
            self.assertTrue(event_proc.expand_defs, "should have expand_defs true when on")

    def test_events_process_empty_file(self):
        with self.assertRaises(HedFileError):
            proc_events = ProcessEvents()
            proc_events.process()

    def test_events_process_invalid(self):
        with self.app.app_context():
            events_proc = self.get_event_proc('data/bids_events.tsv', 'data/bids_events_bad.json', 'data/HED8.2.0.xml')
            events_proc.command = base_constants.COMMAND_VALIDATE
            results = events_proc.process()
            self.assertTrue(isinstance(results, dict),
                            'process validation should return a result dictionary when validation errors')
            self.assertEqual('warning', results['msg_category'],
                             'process validate should return warning when errors')

    def test_events_process_valid(self):
        with self.app.app_context():
            events_proc = self.get_event_proc('data/bids_events.tsv', 'data/bids_events.json', 'data/HED8.2.0.xml')
            events_proc.command = base_constants.COMMAND_VALIDATE
            results = events_proc.process()
            self.assertTrue(isinstance(results, dict), "should return a dictionary when validation errors")
            self.assertEqual('success', results['msg_category'], "should give success when no errors")
            self.assertFalse(results["data"], 'process not return data no no errors')

    def test_events_assemble_invalid(self):
        with self.app.app_context():
            events_proc = self.get_event_proc('data/bids_events.tsv', 'data/bids_events_bad.json', 'data/HED8.2.0.xml')
            events_proc.check_for_warnings = False
            events_proc.command = base_constants.COMMAND_ASSEMBLE
            results = events_proc.process()
            self.assertTrue('data' in results,'should have a data key when no errors')
            self.assertEqual('warning', results["msg_category"], 'should be warning when errors')

    def test_events_assemble_valid(self):
        with self.app.app_context():
            events_proc = self.get_event_proc('data/bids_events.tsv', 'data/bids_events.json', 'data/HED8.2.0.xml')
            events_proc.check_for_warnings = False
            events_proc.command = base_constants.COMMAND_ASSEMBLE
            results = events_proc.process()
            self.assertTrue(results['data'], "should have a data key when no errors")
            self.assertEqual('success', results['msg_category'], "should be success when no errors")

    def test_generate_sidecar_invalid(self):
        with self.app.app_context():
            events_proc = self.get_event_proc('data/bids_events.tsv', '', 'data/HED8.2.0.xml')
            events_proc.command = base_constants.COMMAND_GENERATE_SIDECAR
            events_proc.columns_skip = ['event_type']
            events_proc.columns_value = ['event_type']
            results = events_proc.process()
            self.assertTrue('data' in results, 'make_query results should have a data key when errors')
            self.assertEqual('warning', results["msg_category"],
                             'make_query msg_category should be warning when errors')

    def test_generate_sidecar_valid(self):
        events_proc = self.get_event_proc('data/bids_events.tsv', 'data/bids_events.json', 'data/HED8.2.0.xml')
        events_proc.command = base_constants.COMMAND_GENERATE_SIDECAR
        events_proc.expand_defs = True
        events_proc.columns_value = ['trial']
        events_proc.columns_skip = ['onset', 'duration', 'sample']
        events_proc.check_for_warnings = False
        results = events_proc.process()
        self.assertTrue(results['data'],
                        'generate_sidecar results should have a data key when no errors')
        self.assertEqual('success', results['msg_category'],
                         'generate_sidecar msg_category should be success when no errors')

    def test_search_invalid(self):
        with self.app.app_context():
            events_proc = self.get_event_proc('data/bids_events.tsv', 'data/bids_events.json', 'data/HED8.2.0.xml')
            events_proc.query = ""
            events_proc.command = base_constants.COMMAND_SEARCH
            results = events_proc.process()
            self.assertTrue('data' in results, 'make_query results should have a data key when errors')
            self.assertEqual('warning', results["msg_category"],
                             'make_query msg_category should be warning when errors')

    def test_events_search_valid(self):
        with self.app.app_context():
            events_proc = self.get_event_proc('data/bids_events.tsv', 'data/bids_events.json', 'data/HED8.2.0.xml')
            events_proc.command = base_constants.COMMAND_SEARCH
            events_proc.queries = ["Sensory-event"]
            results = events_proc.process()
            self.assertTrue(results['data'], 'should have a data key when no errors')
            self.assertEqual('success', results['msg_category'], 'should be success when no errors')

    def test_events_validate_invalid(self):
        events_proc = self.get_event_proc('data/bids_events.tsv', 'data/bids_events_bad.json', 'data/HED8.2.0.xml')
        events_proc.command = base_constants.COMMAND_VALIDATE
        with self.app.app_context():
            results = events_proc.process()
            self.assertTrue(results['data'], 'should have a data key when validation errors')
            self.assertEqual('warning', results["msg_category"],'should be warning when errors')

    def test_events_validate_valid(self):
        events_proc = self.get_event_proc('data/bids_events.tsv', 'data/bids_events.json', 'data/HED8.2.0.xml')
        events_proc.command = base_constants.COMMAND_VALIDATE
        with self.app.app_context():
            results = events_proc.process()
            self.assertFalse(results['data'], 'should not have a data key when no validation errors')
            self.assertEqual('success', results['msg_category'], 'should be success when no errors')

    def test_events_remodel_valid_no_hed(self):
        rmdl1 = [{
            "operation": "remove_columns",
            "description": "Remove unwanted columns prior to analysis",
            "parameters": {
                "column_names": ["value", "sample", "junk"],
                "ignore_missing": True
            }
        }]
        events_proc = self.get_event_proc('data/sub-002_task-FacePerception_run-1_events.tsv', None, None)
        events_proc.command = base_constants.COMMAND_REMODEL
        events_proc.remodel_operations =  {'name': 'test', 'operations': rmdl1}
        cols_orig = events_proc.events.columns
        rows_orig = len(events_proc.events.dataframe)
        with self.app.app_context():
            results = events_proc.process()
        self.assertTrue(results['data'], 'remodel results should have a data key when successful')
        self.assertEqual('success', results['msg_category'], 'remodel msg_category should be success when no errors')
        df = pd.read_csv(StringIO(results['data']), sep='\t')
        self.assertEqual(len(df.columns), len(cols_orig) - 2),
        self.assertEqual(len(df), rows_orig)

    def test_events_remodel_invalid_no_hed(self):
            rmdl1 = [{
                "operation": "remove_columns",
                "description": "Remove unwanted columns prior to analysis",
                "parameters": {
                    "column_names": ["value", "sample", "junk"],
                    "ignore_missing": False
                }
            }]
            events_proc = self.get_event_proc('data/sub-002_task-FacePerception_run-1_events.tsv', None, None)
            events_proc.command = base_constants.COMMAND_REMODEL
            events_proc.remodel_operations = {'name': 'test', 'operations': rmdl1}
            with self.app.app_context():
                with self.assertRaises(KeyError) as ex:
                    events_proc.process()
            self.assertEqual(ex.exception.args[0], 'MissingColumnCannotBeRemoved')

    def test_events_remodel_valid_with_hed(self):
        rmdl1 = [{
                    "operation": "factor_hed_type",
                    "description": "Factor condition variables.",
                    "parameters": {
                        "type_tag": "Condition-variable"
                    }
                }]
        events_proc = self.get_event_proc('data/sub-002_task-FacePerception_run-1_events.tsv',
                                          'data/task-FacePerception_events.json', 'data/HED8.2.0.xml')
        events_proc.command = base_constants.COMMAND_REMODEL
        cols_orig = events_proc.events.columns
        rows_orig = len(events_proc.events.dataframe)
        events_proc.remodel_operations = {'name': 'test', 'operations': rmdl1}
        with self.app.app_context():
            results = events_proc.process()
        self.assertTrue(results['data'], 'remodel results should have a data key when successful')
        self.assertEqual('success', results['msg_category'], 'remodel msg_category should be success when no errors')
        df = pd.read_csv(StringIO(results['data']), sep='\t')
        self.assertEqual(len(df.columns), len(cols_orig) + 7),
        self.assertEqual(len(df), rows_orig)


if __name__ == '__main__':
    unittest.main()
