import os
import unittest

from click.testing import CliRunner
from oaklib.cli import search, main
from oakx_robot.robot_implementation import RobotImplementation, OWL_NOTHING

from tests import NUCLEUS

DIR = os.path.dirname(os.path.realpath(__file__)) + '/'
TEST_OWL = DIR + 'input/go-nucleus.owl'
TEST_UNSAT_OWL = DIR + 'input/go-nucleus-unsat.owl'

class TestCommandLineInterface(unittest.TestCase):

    def setUp(self) -> None:
        runner = CliRunner(mix_stderr=False)
        self.runner = runner

    def test_main_help(self):
        result = self.runner.invoke(main, ['--help'])
        out = result.stdout
        err = result.stderr
        self.assertIn('search', out)
        self.assertIn('subset', out)
        self.assertIn('validate', out)
        self.assertEqual(0, result.exit_code)

    def test_main_ontology_is_satisfiable(self):
        """
        Test main ontology is coherent
        """
        result = self.runner.invoke(main, ['-i', f'robot:{TEST_OWL}', 'validate'])
        out = result.stdout
        err = result.stderr
        #self.assertIn('search', out)
        #self.assertIn('subset', out)
        #self.assertIn('validate', out)
        self.assertEqual(0, result.exit_code)
        self.assertNotIn('ERROR', out)

    def test_unsatisfiable(self):
        """
        Test main ontology is coherent
        """
        result = self.runner.invoke(main, ['-i', f'robot:{TEST_UNSAT_OWL}', 'validate'])
        out = result.stdout
        err = result.stderr
        self.assertEqual(0, result.exit_code)
        self.assertIn('ERROR', out)
