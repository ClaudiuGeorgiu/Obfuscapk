package com.obfuscapk.demo;

public class NopDemo {
    public static String getNopMessage(String from) {
        // Just some random instructions...
        String messageStart = "Nop message: ";
        String messageBody = "sending a nop message from ";
        String finalMessage = messageStart + messageBody + from;
        finalMessage += "!";
        return finalMessage;
    }
}
