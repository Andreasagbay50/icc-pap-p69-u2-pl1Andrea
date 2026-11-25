package edu.ups.pap.regex;

import java.util.regex.Pattern;

/** E04: Tramas de sensores. Contrato completo en README.md. */
public class Ejercicio04 {
    private static final String NUM = "(?!000)[0-9]{3}";
    private static final String VALOR = "-?(?:0|[1-9][0-9]{0,3})(?:,[0-9]{1,2})?";
    private static final Pattern REGEX = Pattern.compile(
            "(?:T" + NUM + ";" + VALOR + ";C"
          + "|H" + NUM + ";" + VALOR + ";PCT"
          + "|P" + NUM + ";" + VALOR + ";HPA)"
    );

    public static boolean validar(String texto) {
        return texto != null && REGEX.matcher(texto).matches();
    }
}