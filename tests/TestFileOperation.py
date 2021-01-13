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

    def test_read_of_the_file(self):
        self.assertEqual(self.file_op.read_of_the_file(), self.test_message.split())

    def test_rewrite_file(self):
        self.file_op.rewrite_file('test_lines')
        with open('test_file', 'r', encoding='utf-8') as test:
            self.assertEqual(test.readlines(), ['test_lines\n'])

    def test_edit_file(self):
        self.file_op.edit_file('5', 'new_lines')
        with open('test_file', 'r', encoding='utf-8') as test:
            split_message = self.test_message.split()
            for i in range(len(split_message)):
                if split_message[i] == '5':
                    split_message[i] = 'new_lines'
            self.assertEqual([_.strip() for _ in test.readlines()], split_message)

    def test_edit_file_with_append(self):
        self.file_op.edit_file('10', 'new_lines')
        with open('test_file', 'r', encoding='utf-8') as test:
            split_message = self.test_message.split()
            split_message.append('new_lines')
            self.assertEqual([_.strip() for _ in test.readlines()], split_message)

    def tearDown(self) -> None:
        self.test_file.unlink()


if __name__ == '__main__':
    fi_op_tests = unittest.TestSuite()
    fi_op_tests.addTest(unittest.makeSuite(TestFileOperation))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(fi_op_tests)
