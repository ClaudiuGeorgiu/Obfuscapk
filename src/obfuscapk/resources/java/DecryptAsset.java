package com.decryptassetmanager;

import android.content.res.AssetManager;
import android.os.Build;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;

import javax.crypto.Cipher;
import javax.crypto.spec.SecretKeySpec;

public class DecryptAsset {
    public static InputStream decryptAsset(AssetManager assetManager, String assetName) {
        try {
            return new FileInputStream(decryptAssetFileUsingContext(assetManager, assetName));
        } catch (Exception ignored) { }

        return null;
    }

    public static void loadEncryptedLibrary(Class invokingClass, String libraryName) {
        String architecture = Build.SUPPORTED_ABIS[0];
        String encryptedLibraryName = String.format("lib.%s.%s.so", architecture, libraryName);

        File decryptedLibrary = decryptAssetFileUsingClassLoader(invokingClass,
                encryptedLibraryName);
        if (decryptedLibrary != null && decryptedLibrary.exists()) {
            System.load(decryptedLibrary.getPath());
        }
    }

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

    private static File decryptAssetFileUsingContext(AssetManager assetManager, String assetName) {
        try {
            SecretKeySpec secretKeySpec = new SecretKeySpec(
                    "This-key-need-to-be-32-character".getBytes(), "AES");
            Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5PADDING");
            cipher.init(Cipher.DECRYPT_MODE, secretKeySpec);

            InputStream assetInputStream = assetManager.open(assetName);

            byte[] decryptedContent = cipher.doFinal(readBytes(assetInputStream));
            File tempFile = File.createTempFile("decrypted_", null);

            FileOutputStream fileOutputStream = new FileOutputStream(tempFile);
            fileOutputStream.write(decryptedContent);
            fileOutputStream.close();
            return tempFile;

        } catch (Exception ignored) { }

        return null;
    }

    private static File decryptAssetFileUsingClassLoader(Class invokingClass, String assetName) {
        try {
            SecretKeySpec secretKeySpec = new SecretKeySpec(
                    "This-key-need-to-be-32-character".getBytes(), "AES");
            Cipher cipher = Cipher.getInstance("AES/ECB/PKCS5PADDING");
            cipher.init(Cipher.DECRYPT_MODE, secretKeySpec);

            InputStream assetInputStream = invokingClass.getClassLoader()
                    .getResourceAsStream(String.format("assets/%s", assetName));

            byte[] decryptedContent = cipher.doFinal(readBytes(assetInputStream));
            File tempFile = File.createTempFile("decrypted_", null);

            FileOutputStream fileOutputStream = new FileOutputStream(tempFile);
            fileOutputStream.write(decryptedContent);
            fileOutputStream.close();
            return tempFile;

        } catch (Exception ignored) { }

        return null;
    }
}
