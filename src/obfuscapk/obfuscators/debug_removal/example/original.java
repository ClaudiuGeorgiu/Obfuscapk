package com.obfuscapk.demo;

import android.support.annotation.NonNull;

public class DebugInfoDemo {
    public static String getDebugMessage(@NonNull String from) {
        return String.format("Debug message from %s", from);
    }
}
