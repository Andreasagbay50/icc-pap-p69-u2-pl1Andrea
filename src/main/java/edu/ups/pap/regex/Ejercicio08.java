package edu.ups.pap.regex;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** E08: Análisis de registros. Contrato completo en README.md. */
public class Ejercicio08 {
    private static final String OCTETO = "(?:25[0-5]|2[0-4][0-9]|1[0-9]{2}|[1-9]?[0-9])";
    private static final String IP = OCTETO + "(?:\\." + OCTETO + "){3}";
    private static final String VALOR = "-?(?:0|[1-9][0-9]{0,3})(?:,[0-9]{1,2})?";

    private static final Pattern LINEA = Pattern.compile(
            "(INFO|WARN|ERROR) (" + IP + ") ([THP](?!000)[0-9]{3});(" + VALOR + ");(C|PCT|HPA)"
    );

    public static List<String> analizar(String texto) {
        List<String> resultados = new ArrayList<>();
        if (texto == null || texto.isEmpty()) {
            return resultados;
        }

        String[] lineas = texto.split("\\r?\\n", -1);
        for (String linea : lineas) {
            Matcher m = LINEA.matcher(linea);
            if (!m.matches()) {
                continue;
            }

            String nivel = m.group(1);
            String ip = m.group(2);
            String codigo = m.group(3);
            String valor = m.group(4);
            String unidad = m.group(5);

            char prefijo = codigo.charAt(0);
            boolean unidadValida = (prefijo == 'T' && unidad.equals("C"))
                    || (prefijo == 'H' && unidad.equals("PCT"))
                    || (prefijo == 'P' && unidad.equals("HPA"));

            if (unidadValida) {
                resultados.add(nivel + "|" + ip + "|" + codigo + "|" + valor + "|" + unidad);
            }
        }
        return resultados;
    }
}
