import pathlib
import unittest

from src import FileOperation


class TestFileOperation(unittest.TestCase):

    def setUp(self):
        self.test_file = pathlib.Path.cwd().joinpath('test_file')
        self.file_op = FileOperation.EditingFile(self.test_file)
        pathlib.Path.touch(self.test_file, exist_ok=True)
        self.test_message = ''.join(str(i) + '\n' for i in range(10))
        self.test_file.write_text(self.test_message, encoding='utf-8')

    # @unittest.skip
    def test_read_of_the_file(self):
        self.assertEqual(self.file_op.read_of_the_file(), self.test_message)

    # @unittest.skip
    def test_edit_file_with_replace(self):
        self.file_op.edit_file('new_lines', old_text='5\n6')
        with open('test_file', encoding='utf-8') as test:
            self.test_message = self.test_message.replace('5\n6', 'new_lines')
            self.assertEqual(test.read(), self.test_message)

    # @unittest.skip
    def test_edit_file_with_append(self):
        self.file_op.edit_file('new_lines')
        with open('test_file', encoding='utf-8') as test:
            self.test_message = self.test_message + 'new_lines'
            self.assertEqual(test.read(), self.test_message)

    # @unittest.skip
    def test_edit_file_wrong_old_text(self):
        self.file_op.edit_file('new_lines', old_text='209')
        with open('test_file', encoding='utf-8') as test:
            self.assertEqual(test.read(), self.test_message)

    def tearDown(self) -> None:
        self.test_file.unlink()


if __name__ == '__main__':
    fi_op_tests = unittest.TestSuite()
    fi_op_tests.addTest(unittest.makeSuite(TestFileOperation))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(fi_op_tests)
