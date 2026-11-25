package edu.ups.pap.regex;

import java.util.ArrayList;
import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** E07: Extracción de tramas. Contrato completo en README.md. */
public class Ejercicio07 {
    private static final String DELIM = " \\t\\n\\r\\u000B\\f\\[\\](){}";
    private static final String NUM = "(?!000)[0-9]{3}";
    private static final String VALOR = "-?(?:0|[1-9][0-9]{0,3})(?:,[0-9]{1,2})?";
    private static final String TRAMA = "(?:T" + NUM + ";" + VALOR + ";C"
            + "|H" + NUM + ";" + VALOR + ";PCT"
            + "|P" + NUM + ";" + VALOR + ";HPA)";

    private static final Pattern FORMATO = Pattern.compile(
            "(?<![" + "^" + DELIM + "])" + TRAMA + "(?![" + "^" + DELIM + "])"
    );

    public static List<String> extraer(String texto) {
        List<String> resultados = new ArrayList<>();
        if (texto == null || texto.isEmpty()) {
            return resultados;
        }

        Matcher matcher = FORMATO.matcher(texto);
        while (matcher.find()) {
            resultados.add(matcher.group());
        }
        return resultados;
    }
}