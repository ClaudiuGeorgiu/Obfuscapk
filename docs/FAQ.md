## ❱ FAQ

Here you can find the answers to the most common questions about Obfuscapk. If you're
having technical issues when running the tool, visit the
[troubleshooting](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/docs/TROUBLESHOOTING.md)
page.

----------------------------------------------------------------------------------------

#### :speech_balloon: Can I use this tool to bypass antivirus software?

**:white_check_mark:** You can try, no one is going to stop you. However, since
Obfuscapk is public and open-source, probably most antivirus engines will detect it by
now (the first release dates back to September 2019), or at least will mark your
obfuscated application as suspicious. This is a research project that aims at showing
different obfuscation techniques, if you really want to bypass an antivirus you will
have to implement these (and other) techniques in a new and different way, by still
maintaining the core functionality. Here you can find a few suggestions:

* use a different keystore to sign the obfuscated applications;

* use another seed/technique to generate the random strings;

* change the hardcoded package names used by Obfuscapk (e.g.,
`Lcom/decryptstringmanager/DecryptString;` and
`Lcom/apireflectionmanager/AdvancedApiReflection;`);

* use different encryption functions/keys.

----------------------------------------------------------------------------------------

#### :speech_balloon: Is Obfuscapk production ready? How does it compare to other (commercial) products?

**:white_check_mark:** Obfuscapk is a research project and *should* work most of the
time, however, it has some limitations and might break your application in unexpected
ways. Our empirical assessment indicates a success rate of nearly 80% on real apps
downloaded from the Google Play Store (see the
[official publication](https://doi.org/10.1016/j.softx.2020.100403) for more details).
Unfortunately, it is hard to compare Obfuscapk to other commercial obfuscators, since
they typically do not offer an evaluation version, some of them require the
application's source code to work, and they are closed source. Still, Obfuscapk tries
to implement all the advanced obfuscation techniques declared by such proprietary
obfuscators.

----------------------------------------------------------------------------------------

#### :speech_balloon: I'm interested in this topic, where can I find more information about Obfuscapk and Android obfuscation in general?

**:white_check_mark:** You can find further details about Obfuscapk in the paper
"[Obfuscapk: An *open-source* black-box obfuscation tool for Android apps](https://doi.org/10.1016/j.softx.2020.100403)".
The references section of the paper contains many useful resources to learn more about
Android obfuscation. For more information, you can also check the following links
(in no particular order):

* [Obfuscation in Android malware, and how to fight back](https://www.virusbulletin.com/virusbulletin/2014/07/obfuscation-android-malware-and-how-fight-back)

* [A study on obfuscation techniques for Android malware](http://midlab.diag.uniroma1.it/articoli/matteo_pomilia_master_thesis.pdf)

* [How I Defeated an Obfuscated and Anti-Tamper APK](https://www.evilsocket.net/2016/04/18/How-I-defeated-an-obfuscated-and-anti-tamper-APK-with-some-Python-and-a-home-made-Smali-emulator/)

* [Android Deobfuscation Tools and Techniques](https://www.slideshare.net/tekproxy/tetcon-2016)

* [Obfuscated No More - Practical Steps for Defeating Android Obfuscation](https://www.youtube.com/watch?v=rvtmVApVS8c)

* [Simplify: Android virtual machine and deobfuscator](https://github.com/CalebFenton/simplify)

----------------------------------------------------------------------------------------

#### :speech_balloon: What are the prerequisites for using this tool?

**:white_check_mark:** The main target of Obfuscapk are developers and researchers, so
basic knowledge of Android and Python is expected, though not mandatory. However, as
long as you are able to follow the instructions in the
[readme](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/README.md), you should
be able to install and use Obfuscapk without any specific prerequisite.

----------------------------------------------------------------------------------------

#### :speech_balloon: The tool seems to run but nothing is printed in the terminal.

**:white_check_mark:** By default Obfuscapk shows only error messages, if you only want
to see progress bars during the obfuscation operations, use `-p/--show-progress` flag.
You can also
[enable verbose logging](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/docs/TROUBLESHOOTING.md#enable-verbose-logging).

----------------------------------------------------------------------------------------

#### :speech_balloon: Is the order of the obfuscators passed as parameters important?

**:white_check_mark:** The order of the obfuscators matters, since they are executed
sequentially. E.g., if the first obfuscator is encrypting the strings, all the remaining
obfuscators will see the encrypted strings instead of the original ones, so you can
obtain different results by just changing the order of the used obfuscators. However,
remember to preserve the order of `Rebuild`, `NewAlignment` and `NewSignature` and
always use them *after* the other obfuscators.

----------------------------------------------------------------------------------------

#### :speech_balloon: The obfuscation process seems to finish without errors, but the resulting application does not install or does not work as expected.

**:white_check_mark:** It happens, Obfuscapk is not perfect. If the tool finishes
without errors, the obfuscated application is ***NOT*** guaranteed to work exactly like
the original one, for a few reasons:

* the application is using some anti-tampering protection;

* the obfuscation broke something in the app (it's easy to mess up when dealing with
obfuscation, encryption and reflection at the same time);

* some operations (like encryption and reflection) can make the obfuscated application
slower than the original.

For more information, see also
[troubleshooting](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/docs/TROUBLESHOOTING.md).

----------------------------------------------------------------------------------------

#### :speech_balloon: I've used obfuscator *X* but nothing seems to have changed compared to the original application.

**:white_check_mark:** Some obfuscators work only under specific assumptions, so they
may not work for all the applications. E.g., `LibEncryption` obfuscator only encrypts
the native libraries that are loaded inside static constructors, so if the application
is loading the native libraries differently, `LibEncryption` will not work. Moreover,
if you are using `-i/--ignore-libs` flag, Obfuscapk will ignore all code where the
package name matches a
[known third party library](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/src/obfuscapk/resources/libs_to_ignore.txt).

For more information, inspect the source code of the obfuscator that is not working
as expected.

----------------------------------------------------------------------------------------

#### :speech_balloon: What can I do if I have any questions that are not covered here?

**:white_check_mark:** Open a new issue on GitHub and ask your question(s) in
understandable language.
