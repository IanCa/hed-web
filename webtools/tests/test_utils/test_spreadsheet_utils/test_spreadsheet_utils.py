import os
import unittest
import shutil


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from hedweb.app_factory import AppFactory
        cls.upload_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../data/upload')
        app = AppFactory.create_app('config.TestConfig')
        with app.app_context():

            from hedweb.routes import route_blueprint
            app.register_blueprint(route_blueprint)
            if not os.path.exists(cls.upload_directory):
                os.mkdir(cls.upload_directory)
            app.config['UPLOAD_FOLDER'] = cls.upload_directory
            cls.app = app.test_client()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.upload_directory)

    # def test_convert_number_str_to_list(self):
    #     from hedweb.utils.spreadsheet_utils import convert_number_str_to_list
    #     other_tag_columns_str = '1,2,3'
    #     expected_other_columns = [1, 2, 3]
    #     other_tag_columns = convert_number_str_to_list(other_tag_columns_str)
    #     self.assertTrue(other_tag_columns)
    #     self.assertEqual(expected_other_columns, other_tag_columns)
    #     other_tag_columns_str = ''
    #     other_tag_columns = convert_number_str_to_list(other_tag_columns_str)
    #     self.assertEqual(len(other_tag_columns), 0, "")
    #     other_tag_columns_str = '2,4,3'
    #     expected_other_columns = [2, 4, 3]
    #     other_tag_columns = convert_number_str_to_list(other_tag_columns_str)
    #     self.assertTrue(other_tag_columns)
    #     self.assertEqual(expected_other_columns, other_tag_columns)
    #     other_tag_columns_str = 'A,B,C'
    #     with self.assertRaises(ValueError):
    #         other_tag_columns = convert_number_str_to_list(other_tag_columns_str)
    #
    # def test_find_all_str_indices_in_list(self):
    #     from hedweb.utils.spreadsheet_utils import find_all_str_indices_in_list
    #     list_1 = ['a', 'a', 'c', 'd']
    #     search_str = 'a'
    #     expected_indices = [1, 2]
    #     indices = find_all_str_indices_in_list(list_1, search_str)
    #     self.assertTrue(indices)
    #     self.assertIsInstance(indices, list)
    #     self.assertEqual(expected_indices, indices)
    #     search_str = 'A'
    #     expected_indices = [1, 2]
    #     indices = find_all_str_indices_in_list(list_1, search_str)
    #     self.assertTrue(indices)
    #     self.assertIsInstance(indices, list)
    #     self.assertEqual(expected_indices, indices)
    #     search_str = 'Apple'
    #     expected_indices = []
    #     indices = find_all_str_indices_in_list(list_1, search_str)
    #     self.assertFalse(indices)
    #     self.assertIsInstance(indices, list)
    #     self.assertEqual(expected_indices, indices)

    def test_generate_input_columns_info(self):
        self.assertTrue(1, "Testing get_delimiter_from_file_extension")

    def test_get_column_delimiter_based_on_file_extension(self):
        self.assertTrue(1, "Testing get_delimiter_from_file_extension")
    #     from hed.hedweb.utils import get_delimiter_from_file_extension
    #     delimiter = get_delimiter_from_file_extension('test.tsv')
    #     self.assertEqual('\t', delimiter, ".tsv files should have a tab delimiter")
    #     delimiter = get_delimiter_from_file_extension('test.TSV')
    #     self.assertEqual('\t', delimiter, ".TSV files should have a tab delimiter")
    #     delimiter = get_delimiter_from_file_extension('test')
    #     self.assertEqual('', delimiter, "Files with no extension should have an empty delimiter")
    #     delimiter = get_delimiter_from_file_extension('test.xlsx')
    #     self.assertEqual('', delimiter, "Excel files should have an empty delimiter")

    def test_get_columns_info(self):
        self.assertTrue(1, "Testing get_delimiter_from_file_extension")

    def test_get_column_info_dictionary(self):
        self.excel_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                       '../../data/ExcelMultipleSheets.xlsx')

    def test_get_other_tag_column_indices(self):
        self.assertTrue(1, "Testing get_other_tag_column_indices")
        # def test_get_spreadsheet_other_tag_column_indices(self):
        #     column_names = ['a,', spreadsheet_constants.OTHER_TAG_COLUMN_NAMES[0]]
        #     expected_indices = [2]
        #     indices = utils.get_other_tag_column_indices(column_names)
        #     self.assertTrue(indices)
        #     self.assertIsInstance(indices, list)
        #     self.assertEqual(indices, expected_indices)
        #

    def test_get_specific_tag_column_indices(self):
        self.assertTrue(1, "Testing get_specific_tag_column_indices")
        # def test_get_spreadsheet_specific_tag_column_indices(self):
        #     column_names = ['a,', spreadsheet_constants.SPECIFIC_TAG_COLUMN_NAMES_DICTIONARY[
        #         spreadsheet_constants.SPECIFIC_TAG_COLUMN_NAMES[0]][0]]
        #     # print(column_names)
        #     indices = utils.get_specific_tag_column_indices(column_names)
        #     self.assertTrue(indices)
        #     self.assertIsInstance(indices, dict)
        #

    def test_get_specific_tag_columns_from_form(self):
        self.assertTrue(1, "Testing get_specific_tag_column_indices")
        # def test_get_spreadsheet_specific_tag_column_indices(self):
        #     column_names = ['a,', spreadsheet_constants.SPECIFIC_TAG_COLUMN_NAMES_DICTIONARY[
        #         spreadsheet_constants.SPECIFIC_TAG_COLUMN_NAMES[0]][0]]
        #     # print(column_names)
        #     indices = utils.get_specific_tag_column_indices(column_names)
        #     self.assertTrue(indices)
        #     self.assertIsInstance(indices, dict)
        #

    def test_get_text_file_column_names(self):
        self.assertTrue(1, "Testing get_text_file_column_names")
        # def test_get_text_file_column_names(self):
        #     column_names = utils.get_text_file_column_names(self.tsv_file1, '\t')
        #     self.assertTrue(column_names)
        #     self.assertIsInstance(column_names, list)
        #

    def test_get_text_file_info(self):
        self.assertTrue(1, "Testing get_text_file_column_names")
        # def test_get_text_file_column_names(self):
        #     column_names = utils.get_text_file_column_names(self.tsv_file1, '\t')
        #     self.assertTrue(column_names)
        #     self.assertIsInstance(column_names, list)
        #

    def test_get_worksheets_info(self):
        info = {}
        self.assertTrue(1, "Testing get_worksheets_info_dictionary")


if __name__ == '__main__':
    unittest.main()
