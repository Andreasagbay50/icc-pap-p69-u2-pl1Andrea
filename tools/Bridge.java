import java.lang.reflect.InvocationTargetException;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.List;

/** Adaptador de pruebas. No contiene reglas ni soluciones de los ejercicios. */
public class Bridge {
    public static void main(String[] args) {
        try {
            Class<?> type = Class.forName("edu.ups.pap.regex.Ejercicio" + args[0]);
            String[] values = new String[args.length - 2];
            Class<?>[] signature = new Class<?>[values.length];
            for (int i = 0; i < values.length; i++) {
                values[i] = args[i + 2].equals("~") ? null : new String(
                    Base64.getDecoder().decode(args[i + 2]), StandardCharsets.UTF_8);
                signature[i] = String.class;
            }
            Object result = type.getMethod(args[1], signature).invoke(null, (Object[]) values);
            if (result instanceof Boolean b) {
                System.out.println("BOOL:" + b);
            } else if (result instanceof List<?> items) {
                System.out.println("LIST:" + items.size());
                for (Object item : items) {
                    if (!(item instanceof String s)) throw new IllegalArgumentException("Se esperaba String");
                    System.out.println(Base64.getEncoder().encodeToString(s.getBytes(StandardCharsets.UTF_8)));
                }
            } else {
                throw new IllegalArgumentException("Tipo de retorno inválido o null");
            }
        } catch (Throwable ex) {
            Throwable cause = ex instanceof InvocationTargetException ? ex.getCause() : ex;
            System.err.println(cause.getClass().getSimpleName() + ": " + cause.getMessage());
            System.exit(2);
        }
    }
}
