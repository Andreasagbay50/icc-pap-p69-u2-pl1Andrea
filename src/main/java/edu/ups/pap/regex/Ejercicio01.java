package edu.ups.pap.regex;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Ejercicio01 {

    private final static Pattern REGEX = Pattern.compile("[a-z]{4,12}");

    public static boolean validar(String texto){
       //if(texto == null){

      // }
       //Matcher matcher = REGEX.matcher(texto);
       //if(matcher.matches()){
        //return true;
       //}
       //return false;

       return texto !=null && REGEX.matcher(texto).matches();
    
    }
}
