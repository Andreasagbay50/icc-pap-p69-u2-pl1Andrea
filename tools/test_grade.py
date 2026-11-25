"""Pruebas del calificador. No forman parte de la nota del estudiante."""
from pathlib import Path
from fractions import Fraction
import contextlib
import io
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from grade import calculate, load_rubric, report, ROOT


class CalificadorTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.rubric = load_rubric(ROOT/'grading/rubric.json')
        self.xml = ET.Element('testsuite')

    def add_case(self, key, state=None):
        node = ET.SubElement(self.xml, 'testcase', name=key, classname=key.split('-')[0])
        if state:
            ET.SubElement(node, state)
        return node

    def all_pass(self):
        for ex in self.rubric['exercises']:
            for key in ex['tests']:
                self.add_case(key)

    def score(self):
        path = self.folder/'tests.xml'
        ET.ElementTree(self.xml).write(path, encoding='utf-8')
        return calculate(self.rubric, path)

    def test_empty_is_zero(self):
        self.assertEqual(self.score()['total'], 0)

    def test_all_pass_is_ten(self):
        self.all_pass()
        self.assertEqual(self.score()['total_fraction'], '10')

    def test_complete_exercises_weighted(self):
        for ex in self.rubric['exercises']:
            if ex['id'] in ('E01', 'E08'):
                for key in ex['tests']:
                    self.add_case(key)
        self.assertEqual(self.score()['total_fraction'], '3')

    def test_partial_exercise_exact_fraction(self):
        ex = self.rubric['exercises'][6]
        for key in ex['tests'][:3]:
            self.add_case(key)
        self.assertEqual(Fraction(self.score()['total_fraction']), Fraction(3, 16) * 2)

    def test_failure_error_skip_no_credit(self):
        keys = self.rubric['exercises'][0]['tests']
        for key, tag in zip(keys, ['failure', 'error', 'skipped']):
            self.add_case(key, tag)
        data = self.score()
        self.assertEqual(data['total'], 0)
        self.assertEqual(data['rows'][0]['counts']['missing'], 9)

    def test_deleted_case_fixed_denominator(self):
        self.all_pass()
        self.xml.remove(self.xml[0])
        self.assertEqual(Fraction(self.score()['total_fraction']), 10 - Fraction(1, 12))

    def test_duplicate_even_if_both_pass_gets_zero(self):
        self.all_pass()
        self.add_case('E01-C001')
        data = self.score()
        self.assertEqual(Fraction(data['total_fraction']), 10 - Fraction(1, 12))
        self.assertEqual(data['rows'][0]['counts']['duplicate'], 1)

    def test_unknown_is_ignored(self):
        self.add_case('E01-NOEXISTE')
        self.assertEqual(self.score()['total'], 0)

    def test_wrong_classname_does_not_pass(self):
        node = self.add_case('E01-C001')
        node.set('classname', 'E08')
        self.assertEqual(self.score()['total'], 0)

    def invalid_manifest(self, change):
        change(self.rubric)
        file = self.folder/'rubric.json'
        file.write_text(json.dumps(self.rubric))
        with self.assertRaises(ValueError):
            load_rubric(file)

    def test_duplicate_manifest_rejected(self):
        self.invalid_manifest(lambda r: r['exercises'][0]['tests'].append('E01-C001'))

    def test_bad_sum_rejected(self):
        self.invalid_manifest(lambda r: r.update(scale=11))

    def test_negative_points_rejected(self):
        self.invalid_manifest(lambda r: r['exercises'][0].update(points=-1))

    def test_empty_exercise_rejected(self):
        self.invalid_manifest(lambda r: r['exercises'][0].update(tests=[]))

    def test_bad_xml_rejected(self):
        path = self.folder/'bad.xml'
        path.write_text('<testsuite>')
        with self.assertRaises(ET.ParseError):
            calculate(self.rubric, path)

    def test_infrastructure_has_no_final_grade(self):
        self.all_pass()
        self.score()
        meta = self.folder/'run.json'
        meta.write_text(json.dumps({'infrastructure_error':'JDK no disponible'}))
        with contextlib.redirect_stdout(io.StringIO()):
            data = report(ROOT/'grading/rubric.json', self.folder/'tests.xml', meta, self.folder/'result.md')
        self.assertIsNone(data['total'])
        self.assertFalse(data['conclusive'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
