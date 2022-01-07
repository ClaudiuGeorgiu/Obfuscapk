## ❱ Troubleshooting

In case of problems when running Obfuscapk, here's a list of steps you can try to solve
the most common errors. For more general questions, see the
[FAQ](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/docs/FAQ.md).



### RTFM

Really. The [readme](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/README.md)
contains everything you need to get started with Obfuscapk. If something is not clear,
the source code is your friend :wink:.



### Always use the latest version

It might seem obvious, but unless you just cloned the repository, make sure to be using
the latest version of Obfuscapk from the
[master branch](https://github.com/ClaudiuGeorgiu/Obfuscapk/tree/master). If you are
using Docker, make sure to pull the latest
[official Obfuscapk Docker image](https://hub.docker.com/r/claudiugeorgiu/obfuscapk)
from Docker Hub.



### Install the additional tools correctly

If you are not using the Docker image, make sure to install and setup properly the
additional tools needed for Obfuscapk to work:
[`apktool`](https://ibotpeaches.github.io/Apktool/),
[`apksigner`](https://developer.android.com/studio/command-line/apksigner)
and [`zipalign`](https://developer.android.com/studio/command-line/zipalign). Please
ensure to be using a recent release of
[`apktool`](https://ibotpeaches.github.io/Apktool/) (some systems, like Kali Linux,
have an old version of `apktool` pre-installed by default). Check the
[readme](https://github.com/ClaudiuGeorgiu/Obfuscapk#from-source) for more information.



### Run the help command

Run Obfuscapk by passing only the `--help` flag to display the help message (the exact
command depends on
[how Obfuscapk was installed](https://github.com/ClaudiuGeorgiu/Obfuscapk#-usage)).
Besides showing how to use Obfuscapk, this command also checks that the additional tools
are available and correctly installed. If you aren't getting any error at this point, it
means that Obfuscapk is configured properly and ready to be used.



### Enable verbose logging

By default Obfuscapk shows only error messages. To better understand the cause of an
issue, you can enable debug log messages by setting `LOG_LEVEL` environment variable
to `DEBUG` or by modifying
[src/obfuscapk/main.py](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/src/obfuscapk/main.py)
file as follows:

```Diff
-    log_level = logging.ERROR
+    log_level = logging.DEBUG
```

If you only want to see progress bars during the obfuscation operations, use
`-p/--show-progress` flag instead.



### Try running with minimal configuration

Some applications use anti-repackaging techniques and/or `apktool` is not able to
decompile/build the application and in such cases Obfuscapk won't work. To check if an
application can be repackaged (and thus obfuscated) run Obfuscapk using only `Rebuild`,
`NewAlignment` and `NewSignature` obfuscators. If this operation works without errors,
then you can continue adding more obfuscators, otherwise, there's an issue that can't
be solved by just patching Obfuscapk.



### Find the problematic obfuscator

If Obfuscapk works with the minimal configuration but fails in more complex scenarios,
you can try to find if a specific obfuscator is causing the problem:

* run the obfuscation again by adding `-i/--ignore-libs` flag to ignore known third
party libraries (the code belonging to such libraries won't be modified);

* the order of the obfuscators matters, so if something is not working as expected, try
changing the order in which the obfuscators are passed as parameters with
`-o/--obfuscator` (but preserve the order of `Rebuild`, `NewAlignment` and
`NewSignature` and always put them at the end of the list);

* if the error persists, try adding the obfuscators one by one until you find which is
causing the error(s): e.g., instead of running
`-o ConstStringEncryption -o ResStringEncryption -o LibEncryption` all at once, try
only `-o ConstStringEncryption` and check if the resulting application still works as
expected, then continue with `-o ConstStringEncryption -o ResStringEncryption` an so
on (`Rebuild`, `NewAlignment` and `NewSignature` were omitted in this example).

After you found which obfuscator is causing the problem, you have three choices: ignore
it and use other obfuscators that work, open a
[bug report issue on GitHub](https://github.com/ClaudiuGeorgiu/Obfuscapk/issues/new?template=bug_report.md)
or try to find a solution by modifying the obfuscator's source code.



### Check FAQ and existing issues

If you couldn't solve the errors with the above steps, or if you have a different
problem not covered here, then check the
[FAQ](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/docs/FAQ.md) and the
[existing issues on GitHub](https://github.com/issues?utf8=✓&q=is%3Aissue+repo%3AClaudiuGeorgiu/Obfuscapk).
If you still can't find an answer then
[submit a new issue](https://github.com/ClaudiuGeorgiu/Obfuscapk/issues/new/choose)
on GitHub.
