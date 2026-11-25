# PL1 · Expresiones regulares

**Programación Aplicada · Período 69 · Universidad Politécnica Salesiana**  
**Docente:** Ing. Pablo Torres, Mgtr. · **Calificación:** 10 puntos

## Contexto y objetivos

CampusMonitor recibe nombres, identificadores, correos y lecturas de dispositivos. Antes de almacenar la información necesita validar entradas, localizar coincidencias y convertir registros de texto en datos estructurados.

Implementa ocho requerimientos de dificultad incremental. Practicarás conjuntos de caracteres, cuantificadores, alternativas, coincidencia completa, límites, grupos y búsqueda de múltiples coincidencias. Cada ejercicio se evalúa independientemente.

## Entorno y archivos

- JDK 21 con el módulo `jdk.compiler` y Python 3.12.14.
- Java: `java.util.regex.Pattern` y `Matcher`.
- Pruebas: `unittest` de Python. No se necesita instalar paquetes con pip.
- La compilación se realiza con el compilador del JDK desde el evaluador. No se requiere Gradle ni Maven.
- CI: Ubuntu 24.04, Temurin 21 y Python 3.12.14. La revisión de mantenimiento del JDK 21 la resuelve `setup-java` y queda registrada en `run.json`.

| Ruta | Contenido |
|---|---|
| `src/main/java/edu/ups/pap/regex/Ejercicio01.java` a `Ejercicio08.java` | Implementaciones del estudiante |
| `tests/cases/E01.json` a `E08.json` | Entradas y resultados esperados públicos |
| `tools/Bridge.java` | Adaptador que invoca los métodos Java |
| `tools/evaluate.py` | Pruebas unitarias, compilación y reporte JUnit XML |
| `tools/grade.py` | Calificador independiente |
| `grading/rubric.json` | Ponderaciones e identificadores esperados |
| `.github/workflows/calificacion.yml` | Evaluación automática en GitHub Actions |
| `build/reports/` | Reportes generados localmente, excluidos de Git |

## Reglas comunes

1. Modifica únicamente los ocho archivos `EjercicioNN.java`. Conserva paquetes, nombres, firmas y tipos de retorno.
2. Implementa el reconocimiento de formatos y las búsquedas mediante expresiones regulares de Java. Puedes utilizar condiciones, grupos y listas para procesar resultados. No uses bibliotecas externas, red, archivos ni entradas por consola.
3. Cada clase debe ser autónoma: no invoques otras clases `EjercicioNN`. Puedes agregar constantes y métodos privados dentro de la misma clase.
4. No imprimas desde los métodos evaluados. Devuelve el resultado solicitado.
5. E01–E05 deben validar la entrada completa. No recortes espacios ni normalices la entrada. Devuelve `false` ante `null` o cadena vacía.
6. E06–E08 devuelven listas vacías ante entradas nulas o vacías. Conserva orden de aparición, duplicados y escritura original. Nunca devuelvas `null`.
7. Los dígitos de estos formatos son ASCII, de `0` a `9`. Las letras permitidas se especifican en cada ejercicio.
8. Las pruebas comprueban comportamiento; el uso real de expresiones regulares requiere revisión del código por el docente.

## E01 · Palabras del catálogo · 1 punto

**Contexto:** el catálogo necesita etiquetas sencillas que puedan usarse en sus filtros.

Completa `boolean validar(String texto)` en `Ejercicio01`.

Acepta exclusivamente palabras de **4 a 12 letras minúsculas ASCII**, de `a` a `z`. No se admiten tildes, eñes, números, espacios ni signos.

| Entrada | Resultado |
|---|---|
| `sensor` | `true` |
| `red` | `false` |
| `Sensor` | `false` |

## E02 · Códigos de dispositivos · 1 punto

**Contexto:** cada dispositivo debe tener un código que identifique su familia y número.

Completa `boolean validar(String texto)` en `Ejercicio02`.

El código contiene una letra mayúscula `T`, `H` o `P`, seguida de exactamente tres dígitos. El número debe estar entre **001 y 999**. No se permiten separadores ni sufijos.

| Entrada | Resultado |
|---|---|
| `T007` | `true` |
| `P412` | `true` |
| `H000` | `false` |
| `t007` | `false` |

## E03 · Correos institucionales · 1 punto

**Contexto:** las notificaciones solo se enviarán a direcciones institucionales autorizadas.

Completa `boolean validar(String texto)` en `Ejercicio03`.

- El correo debe contener una parte local, un único `@` y un dominio.
- Solo se aceptan los dominios exactos `ups.edu.ec` y `est.ups.edu.ec`, sin distinguir mayúsculas de minúsculas.
- La parte local contiene letras ASCII, dígitos, punto, guion y guion bajo. Debe empezar y terminar con letra o dígito; puede tener un solo carácter.
- No se admiten puntos consecutivos. No hay un límite adicional de longitud para esta práctica.
- No se admiten otros subdominios, espacios, tildes ni `+`.
- Se valida el formato de la práctica; no se consulta si el buzón existe.

| Entrada | Resultado |
|---|---|
| `maria.lopez@ups.edu.ec` | `true` |
| `A_7@EST.UPS.EDU.EC` | `true` |
| `maria..lopez@ups.edu.ec` | `false` |
| `maria@ups.edu.ec.otro` | `false` |

## E04 · Tramas de sensores · 1 punto

**Contexto:** los dispositivos transmiten una lectura compacta que debe revisarse antes de almacenarse.

Completa `boolean validar(String texto)` en `Ejercicio04`.

La estructura es `codigo;valor;unidad`, sin espacios:

- `codigo` cumple el contrato de E02.
- `valor` puede comenzar con `-`, nunca con `+`. La parte entera tiene entre uno y cuatro dígitos, sin ceros iniciales salvo el propio `0`.
- La parte decimal es opcional. Si existe, se separa con **coma** y contiene uno o dos dígitos. No se utiliza punto ni notación científica.
- Se admiten `-0` y `-0,00`. Se verifica formato; no se imponen rangos físicos.
- La unidad debe corresponder al prefijo según la tabla, respetando mayúsculas.

| Prefijo | Unidad |
|---|---|
| T | C |
| H | PCT |
| P | HPA |

| Entrada | Resultado |
|---|---|
| `T001;35,4;C` | `true` |
| `H028;72;PCT` | `true` |
| `P302;1008,25;HPA` | `true` |
| `T415;-8,5;C` | `true` |
| `H028;72;C` | `false` |
| `T001;035,4;C` | `false` |

## E05 · Direcciones IPv4 · 1 punto

**Contexto:** el sistema registra la dirección de origen de cada dispositivo.

Completa `boolean validar(String texto)` en `Ejercicio05`.

Acepta exactamente cuatro octetos decimales separados por puntos. Cada octeto está entre **0 y 255**, sin signos y sin ceros iniciales salvo el propio `0`. No se admiten puertos, máscaras ni IPv6. Las direcciones `0.0.0.0` y `255.255.255.255` son válidas para este ejercicio de formato.

| Entrada | Resultado |
|---|---|
| `172.16.8.24` | `true` |
| `255.0.10.1` | `true` |
| `172.016.8.24` | `false` |
| `172.16.8.256` | `false` |

## E06 · Palabras dentro de un texto · 1 punto

**Contexto:** soporte necesita localizar una palabra en las observaciones de una incidencia.

Completa `List<String> buscar(String texto, String palabra)` en `Ejercicio06`.

- `palabra` debe contener una o más letras ASCII, mayúsculas o minúsculas. Si no cumple este contrato, devuelve una lista vacía. No se interpreta como expresión regular proporcionada por el usuario.
- Busca sus apariciones sin distinguir mayúsculas de minúsculas.
- Solo cuenta coincidencias completas: el carácter anterior y el siguiente, si existen, no pueden ser letra ASCII, dígito ASCII ni guion bajo.
- Los demás caracteres actúan como límites. En este contrato simplificado incluso `ñ` o una letra acentuada actúan como límite.
- Devuelve el texto original de cada coincidencia, sin cambiar sus mayúsculas.

| Texto | Palabra | Resultado |
|---|---|---|
| `Alarma, ALARMA y alarmas.` | `alarma` | `["Alarma", "ALARMA"]` |
| `error_error error2 (error)` | `error` | `["error"]` |
| `sensor y sensor` | `s.*` | `[]` |

## E07 · Extracción de tramas · 2 puntos

**Contexto:** los informes de mantenimiento mezclan observaciones con varias lecturas de sensores.

Completa `List<String> extraer(String texto)` en `Ejercicio07`.

- Extrae todas las tramas válidas según E04.
- Una trama debe estar delimitada por el inicio o fin del texto, por espacio ASCII, tabulación, salto de línea, retorno de carro, tabulación vertical, salto de página o por cualquiera de estos caracteres: `[ ] ( ) { }`.
- Cada lado se verifica de manera independiente; no hace falta que los delimitadores formen una pareja.
- No extraigas una subcadena válida dentro de un token inválido. Coma, punto, guion, `!`, guion bajo y punto y coma adicional **no** son delimitadores.
- Mantén orden, duplicados y el contenido exacto de cada trama.

| Texto | Resultado |
|---|---|
| `Lecturas [T007;18,2;C] y (H028;72;PCT)` | `["T007;18,2;C", "H028;72;PCT"]` |
| `T007;18;C T007;18;C` | `["T007;18;C", "T007;18;C"]` |
| `XT007;18;C T007;18;C;extra` | `[]` |
| `T007;18;C,H028;72;PCT` | `[]` |

## E08 · Análisis de registros · 2 puntos

**Contexto:** el equipo de operaciones quiere convertir una bitácora en filas que puedan importarse a una tabla.

Completa `List<String> analizar(String texto)` en `Ejercicio08`.

- El texto contiene líneas separadas por LF o CRLF. Un retorno de carro aislado no es un separador válido.
- Cada línea válida tiene la estructura `NIVEL IP TRAMA`, con exactamente un espacio ASCII entre los tres campos y sin espacios al inicio o al final.
- `NIVEL` es exactamente `INFO`, `WARN` o `ERROR` en mayúsculas.
- `IP` cumple E05 y `TRAMA` cumple E04, incluida la correspondencia entre prefijo y unidad.
- Ignora las líneas inválidas y vacías sin detener el procesamiento de las siguientes.
- Por cada línea válida, devuelve una cadena con cinco campos: `NIVEL|IP|codigo|valor|unidad`.
- Conserva el valor como texto: no cambies la coma por punto, no redondees y no elimines ceros decimales ni signos.

Entrada:

```text
INFO 172.16.8.24 T007;18,20;C
WARN 256.1.1.1 H028;72;PCT
ERROR 10.0.0.3 P302;-1,5;HPA
```

Resultado:

```text
["INFO|172.16.8.24|T007|18,20|C", "ERROR|10.0.0.3|P302|-1,5|HPA"]
```

## Ejecución local

Clona tu fork y ejecuta los comandos desde la raíz del proyecto. En Windows puedes usar `py -3.12` en lugar de `python3`.

```bash
java -version
python3 --version

# Compilar cada clase, ejecutar todos los casos y generar la nota
python3 tools/evaluate.py

# Ejecutar solamente E04; limpia los reportes anteriores
python3 tools/evaluate.py --exercise E04

# Volver a obtener la nota completa
python3 tools/evaluate.py

# Recalcular a partir del XML y metadatos de la última ejecución
python3 tools/grade.py
```

El evaluador invoca el compilador mediante `java -m jdk.compiler/com.sun.tools.javac.Main`. Si falta ese módulo, instala un JDK 21 completo. No hay una fase de instalación de dependencias externas.

Consulta `build/reports/calificacion.md`, `calificacion.json`, `tests.xml` y `run.json`. Los errores de compilación se guardan en `build/reports/compilacion/`.

Cada caso tiene un identificador estable y se ejecuta en un proceso Java independiente con un límite de 3 segundos. Cada clase debe compilar sin depender de las demás. El código inicial compila, pero sus métodos pendientes producen errores de ejecución y **0/10**.

## Calificación

| Ejercicio | Casos públicos | Máximo |
|---|---:|---:|
| E01 | 12 | 1 |
| E02 | 13 | 1 |
| E03 | 17 | 1 |
| E04 | 20 | 1 |
| E05 | 16 | 1 |
| E06 | 14 | 1 |
| E07 | 16 | 2 |
| E08 | 18 | 2 |
| **Total** | **126** | **10** |

**Puntaje por ejercicio = aprobadas / esperadas × máximo del ejercicio.** La nota es la suma, calculada sin redondeos intermedios; se redondea al final a dos decimales.

Solo generan puntaje los casos aprobados. Los fallidos, con error, omitidos, eliminados, no ejecutados o duplicados no generan puntaje. La cantidad de casos esperados permanece en el manifiesto; eliminar una prueba no reduce el denominador. Un resultado duplicado queda sin puntaje. Los casos desconocidos se ignoran.

| Estado | Significado |
|---|---|
| Solución incompleta | Hay casos pendientes, fallidos o con errores; se publica la nota parcial |
| Solución correcta | Se aprobaron todos los casos esperados |
| Error de compilación | El ejercicio afectado queda sin casos ejecutados; los demás se evalúan |
| Fallo de infraestructura o configuración | Evaluación no concluyente; no hay nota definitiva |
| Ejecución de un solo ejercicio | Retroalimentación parcial; vuelve a ejecutar todo para obtener la nota completa |

El comando normal devuelve código 0 cuando la evaluación funciona, aunque la solución esté incompleta, y código 2 ante un fallo de infraestructura. `--strict` devuelve código 1 si hay incumplimientos académicos. Un workflow verde indica que el evaluador funcionó; la nota se consulta en el resumen.

## GitHub Actions y entrega

1. Haz **Fork** del [repositorio base](https://github.com/PabloT18/icc-pap-p69-u2-pl1) hacia tu cuenta.
2. En tu fork, entra en **Actions** y habilita los workflows si GitHub lo solicita.
3. Clona **tu fork**, no el repositorio del docente:

   ```bash
   git clone https://github.com/TU_USUARIO/icc-pap-p69-u2-pl1.git
   cd icc-pap-p69-u2-pl1
   ```

4. Implementa los ejercicios y verifica la nota localmente.
5. Guarda avances con commits descriptivos y realiza push:

   ```bash
   git add src/main/java
   git commit -m "feat: implementar validación de tramas e IPv4"
   git push
   ```

6. Consulta **Actions → Calificación PL1 - Expresiones regulares → ejecución del último commit → Summary**. Allí se muestran la nota y el detalle por caso. Los reportes también se descargan desde **Artifacts**.
7. Para ejecutar manualmente: **Actions → Calificación PL1 - Expresiones regulares → Run workflow**.
8. Entrega en el **AVAC únicamente la URL del repositorio remoto de tu fork**. No entregues ZIP, capturas ni archivos sueltos.

No modifiques pruebas, scripts, ponderaciones, identificadores ni el workflow de evaluación. Las pruebas públicas contienen datos y respuestas esperadas, pero no soluciones ni expresiones regulares de referencia. La retroalimentación del fork no garantiza integridad académica: el docente puede reevaluar el código con su copia controlada y casos reservados.
