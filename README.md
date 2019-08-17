<h1 align="center">
    <br>
    <a href="https://github.com/ClaudiuGeorgiu/Obfuscapk">
        <img alt="Logo" src="./docs/logo/logo.png" width="700">
    </a>
    <br>
    <br>
</h1>

> A black-box obfuscation tool for Android apps.

[![Python Version](http://img.shields.io/badge/Python-3.7-green.svg)](https://www.python.org/downloads/release/python-374/)

**Obfuscapk** is a modular Python tool for obfuscating Android apps without needing their source code, since [`apktool`](https://ibotpeaches.github.io/Apktool/) is used to decompile the original apk file and to build a new application, after applying some obfuscation techniques on the decompiled smali code, resources and manifest. The obfuscated app retains the same functionality as the original one, but the differences under the hood sometimes make the new application very different from the original (e.g., to signature based antivirus software).

***More details coming soon***



## Contributing

Questions, bug reports and pull requests are welcome on GitHub at [https://github.com/ClaudiuGeorgiu/Obfuscapk](https://github.com/ClaudiuGeorgiu/Obfuscapk).
