package edu.ups.pap.regex;

import java.util.List;
import java.util.regex.Pattern;
import java.util.regex.Matcher;

/** E05: Direcciones IPv4. Contrato completo en README.md. */
public class Ejercicio05 {
    private final static Pattern FORMATO = Pattern.compile(
            "(0|[1-9][0-9]{0,2})\\.(0|[1-9][0-9]{0,2})\\.(0|[1-9][0-9]{0,2})\\.(0|[1-9][0-9]{0,2})"
    );

    public static boolean validar(String texto) {
        if (texto == null) {
            return false;
        }
        Matcher m = FORMATO.matcher(texto);
        if (!m.matches()) {
            return false;
        }

        for (int i = 1; i <= 4; i++) {
            int octeto = Integer.parseInt(m.group(i));
            if (octeto > 255) {
                return false;
            }
        }
        return true;
    }
}