package com.obfuscapk.demo;

public class NativeLibraryDemo {

    // Used to load the 'native-lib' library.
    static {
        // This is the instruction that will be replaced by loading the encrypted lib from assets.
        System.loadLibrary("native-lib");
    }

    private native String stringFromJNI();

    public String getMessageFromNativeLib() {
        return stringFromJNI();
    }
}
