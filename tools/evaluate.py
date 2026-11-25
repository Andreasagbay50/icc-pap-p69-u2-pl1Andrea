"""Compila cada ejercicio de Java y ejecuta casos de unittest sin dependencias."""
from pathlib import Path
import argparse
import base64
import json
import os
import shutil
import subprocess
import sys
import time
import unittest
import xml.etree.ElementTree as ET
from collections import defaultdict
from grade import load_rubric, report

ROOT = Path(__file__).resolve().parents[1]


def command(args, timeout=30):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True,
                          encoding='utf-8', errors='replace', timeout=timeout)


class JavaCase(unittest.TestCase):
    def __init__(self, case, exercise, classpath):
        super().__init__('runTest')
        self.case, self.exercise, self.classpath = case, exercise, classpath

    def id(self):
        return self.case['id']

    def __str__(self):
        return self.id()

    def runTest(self):
        values = ['~' if value is None else base64.b64encode(value.encode()).decode()
                  for value in self.case['args']]
        try:
            run = command(['java', '-Xmx128m', '-Dfile.encoding=UTF-8', '-cp', self.classpath,
                           'Bridge', self.exercise['id'][1:], self.exercise['method'], *values], timeout=3)
        except subprocess.TimeoutExpired as ex:
            raise RuntimeError('Se excedió el tiempo de ejecución de 3 segundos') from ex
        if run.returncode:
            raise RuntimeError(run.stderr.strip() or f'Java terminó con código {run.returncode}')
        lines = run.stdout.splitlines()
        if lines and lines[0] in ('BOOL:true', 'BOOL:false') and len(lines) == 1:
            actual = lines[0] == 'BOOL:true'
        elif lines and lines[0].startswith('LIST:'):
            count = int(lines[0][5:])
            if count != len(lines) - 1:
                raise RuntimeError('Salida del adaptador incompleta')
            actual = [base64.b64decode(s, validate=True).decode('utf-8') for s in lines[1:]]
        else:
            raise RuntimeError('Salida inválida: no imprimir desde los métodos evaluados')
        self.assertEqual(type(actual), type(self.case['expected']), 'Tipo de retorno incorrecto')
        self.assertEqual(actual, self.case['expected'], f'{self.id()}: revisar el contrato del README')


class XmlResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root = ET.Element('testsuite', name='PL1-regex')

    def startTest(self, test):
        super().startTest(test)
        self.started = time.monotonic()
        self.node = ET.SubElement(self.root, 'testcase', classname=test.exercise['id'], name=test.id())

    def stopTest(self, test):
        self.node.set('time', f'{time.monotonic() - self.started:.4f}')
        super().stopTest(test)

    def addFailure(self, test, err):
        super().addFailure(test, err)
        ET.SubElement(self.node, 'failure', message=str(err[1])).text = self._exc_info_to_string(err, test)

    def addError(self, test, err):
        super().addError(test, err)
        ET.SubElement(self.node, 'error', message=str(err[1])).text = self._exc_info_to_string(err, test)

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        ET.SubElement(self.node, 'skipped', message=reason)


def evaluate(args):
    reports = ROOT/'build/reports'
    # Nunca reutilizar resultados ni clases de una ejecución anterior.
    for folder in (reports, ROOT/'build/classes'):
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True)
    meta = {'commit': os.environ.get('GITHUB_SHA', 'local'), 'exercise': args.exercise,
            'compile_errors': {}, 'infrastructure_error': None, 'configuration_issues': []}
    xml = ET.Element('testsuite', name='PL1-regex', tests='0')
    try:
        rubric = load_rubric(args.rubric)
        if args.exercise and args.exercise not in {e['id'] for e in rubric['exercises']}:
            raise ValueError('Ejercicio desconocido')
        compiler = ['java', '-m', 'jdk.compiler/com.sun.tools.javac.Main']
        probe = command(compiler + ['-version'])
        if probe.returncode:
            raise RuntimeError('Falta un JDK con el módulo jdk.compiler: ' + probe.stderr)
        meta['compiler'] = (probe.stdout + probe.stderr).strip()
        meta['python'] = sys.version
        bridge_dir = ROOT/'build/classes/bridge'
        bridge_dir.mkdir()
        bridge = command(compiler + ['-source', '21', '-target', '21', '-encoding', 'UTF-8', '-d', str(bridge_dir), str(ROOT/'tools/Bridge.java')])
        if bridge.returncode:
            raise RuntimeError('No se pudo compilar el adaptador: ' + bridge.stderr)
        suite = unittest.TestSuite()
        for ex in rubric['exercises']:
            if args.exercise and ex['id'] != args.exercise:
                continue
            target = ROOT/'build/classes'/ex['id']
            target.mkdir()
            source = args.source/f'edu/ups/pap/regex/Ejercicio{ex["id"][1:]}.java'
            if not source.is_file():
                meta['compile_errors'][ex['id']] = 'Archivo de implementación no encontrado'
                continue
            try:
                compiled = command(compiler + ['-source', '21', '-target', '21', '-encoding', 'UTF-8', '-d', str(target), str(source)])
                error = compiled.stderr if compiled.returncode else None
            except subprocess.TimeoutExpired:
                error = 'Tiempo de compilación excedido'
            if error:
                meta['compile_errors'][ex['id']] = error
                log = reports/'compilacion'/f'{ex["id"]}.txt'
                log.parent.mkdir(exist_ok=True)
                log.write_text(error, encoding='utf-8')
                continue
            file = args.cases/f'{ex["id"]}.json'
            items = json.loads(file.read_text(encoding='utf-8')) if file.exists() else []
            indexed = defaultdict(list)
            for item in items:
                indexed[item['id']].append(item)
            extra = set(indexed) - set(ex['tests'])
            if extra:
                meta['configuration_issues'].append('Casos desconocidos: ' + ', '.join(sorted(extra)))
            for case_id in ex['tests']:
                entries = indexed.get(case_id, [])
                if len(entries) != 1:
                    # Eliminados o duplicados no se ejecutan y conservan su denominador.
                    meta['configuration_issues'].append(f'{case_id}: se encontraron {len(entries)} definiciones')
                    continue
                case = entries[0]
                if not isinstance(case['args'], list) or not all(a is None or isinstance(a, str) for a in case['args']):
                    raise ValueError('Entrada de prueba mal configurada')
                suite.addTest(JavaCase(case, ex, os.pathsep.join([str(bridge_dir), str(target)])))
        result = unittest.TextTestRunner(verbosity=1, resultclass=XmlResult).run(suite)
        xml = result.root
        xml.set('tests', str(result.testsRun))
        xml.set('failures', str(len(result.failures)))
        xml.set('errors', str(len(result.errors)))
        xml.set('skipped', str(len(result.skipped)))
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.TimeoutExpired) as ex:
        meta['infrastructure_error'] = f'{type(ex).__name__}: {ex}'
    ET.indent(xml)
    ET.ElementTree(xml).write(reports/'tests.xml', encoding='utf-8', xml_declaration=True)
    (reports/'run.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    try:
        grade = report(args.rubric, reports/'tests.xml', reports/'run.json', reports/'calificacion.md')
    except Exception as ex:
        (reports/'calificacion.md').write_text(f'# Evaluación no concluyente\n\nFallo de configuración: {ex}\n', encoding='utf-8')
        print(f'Fallo de configuración: {ex}', file=sys.stderr)
        return 2
    if meta['infrastructure_error']:
        return 2
    # Fallos académicos no impiden publicar la nota. --strict es útil para el docente.
    if args.strict and (meta['compile_errors'] or any(r['counts']['passed'] != r['expected'] for r in grade['rows'] if not args.exercise or r['id'] == args.exercise)):
        return 1
    return 0


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--exercise', help='Ejemplo: E04; la ejecución parcial no representa la nota completa')
    p.add_argument('--rubric', type=Path, default=ROOT/'grading/rubric.json')
    p.add_argument('--cases', type=Path, default=ROOT/'tests/cases')
    p.add_argument('--source', type=Path, default=ROOT/'src/main/java')
    p.add_argument('--strict', action='store_true')
    sys.exit(evaluate(p.parse_args()))
