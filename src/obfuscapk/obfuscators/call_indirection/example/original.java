package com.obfuscapk.demo;

import java.util.ArrayList;
import java.util.Arrays;

public class OrderDemo {
    public static String getGotoMessage() {
        // Just some ordered instructions.
        ArrayList<String> messages = new ArrayList<>();

        String message1 = "message1";
        messages.add(message1);

        String message2 = "message2";
        messages.add(message2);

        String message3 = "message3";
        messages.add(message3);

        return Arrays.toString(messages.toArray());
    }
}
