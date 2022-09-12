import os
import unittest

from oaklib.selector import get_resource_from_shorthand, get_implementation_from_shorthand
from oaklib.implementations import discovered_plugins
from oakx_robot.robot_implementation import RobotImplementation, OWL_NOTHING

from tests import NUCLEUS

DIR = os.path.dirname(os.path.realpath(__file__)) + '/'
TEST_OWL = DIR + 'input/go-nucleus.owl'
TEST_UNSAT_OWL = DIR + 'input/go-nucleus-unsat.owl'

class TestSqlDatabaseImplementation(unittest.TestCase):

    def setUp(self) -> None:
        self.oi = get_implementation_from_shorthand(f'robot:{TEST_OWL}')
        self.unsat_oi = get_implementation_from_shorthand(f'robot:{TEST_UNSAT_OWL}')

    def test_plugin(self):
        plugins = discovered_plugins
        self.assertIn('oakx_robot', plugins)
        slug = f'robot:{TEST_OWL}'
        r = get_resource_from_shorthand(slug)
        self.assertEqual(r.implementation_class, RobotImplementation)

    def test_all_entities(self):
        """
        Test basic functionality
        """
        curies = list(self.oi.all_entity_curies())
        self.assertIn(NUCLEUS, curies)

    def test_main_ontology_is_satisfiable(self):
        """
        Test main ontology is coherent
        """
        assert self.oi.is_coherent()
        unsats = list(self.oi.unsatisfiable_classes(exclude_nothing=False))
        self.assertEqual(1, len(unsats))
        self.assertCountEqual([OWL_NOTHING], unsats)
        unsats = list(self.oi.unsatisfiable_classes())
        self.assertEqual([], unsats)
        results = list(self.oi.validate())
        self.assertEqual([], results)

    def test_find_unsatisfiable_classes(self):
        unsat_oi = self.unsat_oi
        assert not unsat_oi.is_coherent()
        unsats = list(unsat_oi.unsatisfiable_classes(exclude_nothing=True))
        self.assertEqual(1, len(unsats))
        self.assertCountEqual(['GO:0031965'], unsats)
        results = list(unsat_oi.validate())
        self.assertEqual(1, len(results))
        result = results[0]
        self.assertEqual('ERROR', str(result.severity))
