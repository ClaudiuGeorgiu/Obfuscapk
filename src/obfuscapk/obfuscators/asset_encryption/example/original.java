package com.obfuscapk.demo;

import android.content.res.AssetManager;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;

public class AssetDemo {
    // Helper method.
    private static byte[] readBytes(InputStream inputStream) throws IOException {
        byte[] array = new byte[1024];
        ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream();
        while (true) {
            int read = inputStream.read(array);
            if (read == -1) {
                break;
            }
            byteArrayOutputStream.write(array, 0, read);
        }
        return byteArrayOutputStream.toByteArray();
    }

    public String getMessageFromAsset(AssetManager assetManager) throws IOException {
        // This is the instruction that will be replaced by loading the encrypted asset.
        InputStream assetInputStream = assetManager.open("message.txt");
        return new String(readBytes(assetInputStream));
    }
}
