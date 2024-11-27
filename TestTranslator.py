import unittest
from Translator import Translator, SyntaxError

class TestTranslator(unittest.TestCase):

    def setUp(self):
        self.translator = Translator()

    def test_constant_declaration(self):
        config = "port:=8080"
        result = self.translator.parse(config)
        self.assertEqual(self.translator.constants['port'], 8080)

    def test_constant_evaluation(self):
        config = """
        port:=8080
        max_connections:=@(port)
        """
        result = self.translator.parse(config)
        self.assertEqual(self.translator.constants['max_connections'], 8080)

    def test_simple_dictionary(self):
        config = """
        $[
        host:'localhost',
        port:8080,
        debug:true
        ]
        """
        result = self.translator.parse(config)
        expected = {
            "host": "localhost",
            "port": 8080,
            "debug": True
        }
        self.assertEqual(result, expected)

    def test_dictionary_with_constants(self):
        config = """
        port:=8080
        $[
        host:'localhost',
        port:@(port),
        debug:true
        ]
        """
        result = self.translator.parse(config)
        expected = {
            "host": "localhost",
            "port": 8080,
            "debug": True
        }
        self.assertEqual(result, expected)

    def test_invalid_syntax(self):
        config = "invalid_line"
        with self.assertRaises(SyntaxError):
            self.translator.parse(config)

    def test_invalid_constant_reference(self):
        config = """
        $[
        port:@(undefined_constant)
        ]
        """
        with self.assertRaises(SyntaxError):
            self.translator.parse(config)

    def test_toml_conversion(self):
        config = """
        $[
        host:'localhost',
        port:8080,
        debug:true
        ]
        """
        result = self.translator.parse(config)
        toml_output = self.translator.to_toml(result)
        expected_toml = """host = "localhost"
port = 8080
debug = true
"""
        self.assertEqual(toml_output.strip(), expected_toml.strip())

if __name__ == '__main__':
    unittest.main()
