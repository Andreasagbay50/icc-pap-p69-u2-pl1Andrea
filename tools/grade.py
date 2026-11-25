"""Calificador independiente: manifiesto fijo + reporte JUnit XML."""
from pathlib import Path
import argparse
import json
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from fractions import Fraction

ROOT = Path(__file__).resolve().parents[1]


def load_rubric(path):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    exercises = data['exercises']
    ids, cases = [], []
    total = Fraction(0)
    for ex in exercises:
        ids.append(ex['id'])
        points = Fraction(str(ex['points']))
        if points <= 0 or not ex['tests']:
            raise ValueError('Ponderación o lista de pruebas inválida')
        if any(not isinstance(t, str) or not t.startswith(ex['id'] + '-') for t in ex['tests']):
            raise ValueError('Identificador de caso inválido')
        total += points
        cases.extend(ex['tests'])
    if not ids or len(set(ids)) != len(ids) or len(set(cases)) != len(cases):
        raise ValueError('Identificadores duplicados o configuración vacía')
    if total != Fraction(str(data['scale'])) or total <= 0:
        raise ValueError('La suma de ponderaciones no coincide con la escala')
    return data


def calculate(rubric, xml_path):
    root = ET.parse(xml_path).getroot()
    if root.tag not in ('testsuite', 'testsuites'):
        raise ValueError('Raíz JUnit XML inválida')
    observations = defaultdict(list)
    known = {t for e in rubric['exercises'] for t in e['tests']}
    unknown = []
    for case in root.iter('testcase'):
        key = case.get('name', '')
        if key not in known:
            unknown.append(key)
            continue
        state = 'passed'
        if case.find('error') is not None:
            state = 'error'
        elif case.find('failure') is not None:
            state = 'failed'
        elif case.find('skipped') is not None:
            state = 'skipped'
        if case.get('classname') != key.split('-')[0]:
            state = 'error'
        observations[key].append(state)
    rows, total, details = [], Fraction(0), {}
    for ex in rubric['exercises']:
        counts = Counter({k: 0 for k in ('passed', 'failed', 'error', 'skipped', 'missing', 'duplicate')})
        for key in ex['tests']:
            items = observations[key]
            state = 'missing' if not items else 'duplicate' if len(items) != 1 else items[0]
            counts[state] += 1
            details[key] = state
        score = Fraction(counts['passed'], len(ex['tests'])) * Fraction(str(ex['points']))
        rows.append({'id': ex['id'], 'expected': len(ex['tests']), 'counts': dict(counts),
                     'points': ex['points'], 'score_fraction': str(score), 'score': float(score)})
        total += score
    if not 0 <= total <= Fraction(str(rubric['scale'])):
        raise ValueError('Nota fuera de escala')
    return {'rows': rows, 'total_fraction': str(total), 'total': float(total),
            'scale': rubric['scale'], 'cases': details, 'unknown': unknown}


def report(rubric_path, xml_path, meta_path, output):
    rubric = load_rubric(rubric_path)
    meta = json.loads(Path(meta_path).read_text(encoding='utf-8'))
    result = calculate(rubric, xml_path)
    infra = meta.get('infrastructure_error')
    selected = meta.get('exercise')
    if infra:
        state = 'Fallo de infraestructura: evaluación no concluyente'
    elif selected:
        state = f'Ejecución parcial de {selected}: no es la nota final de la entrega'
    elif meta.get('compile_errors'):
        state = 'Error de compilación: los ejercicios afectados no fueron evaluados'
    elif result['total_fraction'] == str(rubric['scale']):
        state = 'Solución correcta en las pruebas ejecutadas'
    else:
        state = 'Solución incompleta'
    result.update({'state': state, 'commit': meta.get('commit', 'local'), 'conclusive': not bool(infra) and not bool(selected)})
    if infra:
        result['total'] = None
        result['total_fraction'] = None
    lines = [f'# {rubric["title"]}', '', f'**Estado:** {state}', '',
             f'**Commit:** `{result["commit"]}`', '',
             '| Ejercicio | Esperadas | Aprobadas | Fallidas | Error | Omitidas | No ejecutadas | Duplicadas | Nota | Máximo |',
             '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for row in result['rows']:
        c = row['counts']
        lines.append(f'| {row["id"]} | {row["expected"]} | {c["passed"]} | {c["failed"]} | {c["error"]} | {c["skipped"]} | {c["missing"]} | {c["duplicate"]} | {row["score"]:.4f} | {row["points"]} |')
    if infra:
        lines += ['', '**Sin calificación definitiva.**', '', str(infra)]
    else:
        label = 'Puntaje de esta ejecución parcial' if selected else 'Calificación final'
        lines += ['', f'**{label}: {result["total"]:.2f} / {result["scale"]:.2f}**',
                  f'Cumplimiento: {result["total"] / result["scale"] * 100:.2f} %.',
                  '', 'El cálculo usa fracciones exactas; solo la nota final se redondea a dos decimales.']
    if meta.get('compile_errors'):
        lines += ['', 'Errores de compilación: ' + ', '.join(sorted(meta['compile_errors'])) + '. Consultar `compilacion/`.']
    if result['unknown']:
        lines += ['', f'Casos desconocidos ignorados: {len(result["unknown"])}.']
    lines += ['', '## Detalle por caso', '', '| Caso | Estado |', '|---|---|']
    labels = {'passed':'Aprobada','failed':'Fallida','error':'Error de ejecución','skipped':'Omitida','missing':'No ejecutada','duplicate':'Duplicada, sin puntaje'}
    lines += [f'| {key} | {labels[value]} |' for key, value in result['cases'].items()]
    text = '\n'.join(lines) + '\n'
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding='utf-8')
    output.with_suffix('.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(text.split('## Detalle por caso')[0])
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--rubric', type=Path, default=ROOT/'grading/rubric.json')
    parser.add_argument('--xml', type=Path, default=ROOT/'build/reports/tests.xml')
    parser.add_argument('--meta', type=Path, default=ROOT/'build/reports/run.json')
    parser.add_argument('--output', type=Path, default=ROOT/'build/reports/calificacion.md')
    args = parser.parse_args()
    report(args.rubric, args.xml, args.meta, args.output)
