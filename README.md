![Logo](https://raw.githubusercontent.com/ClaudiuGeorgiu/Obfuscapk/master/docs/logo/logo.png)

> A black-box obfuscation tool for Android apps.

[![Codacy](https://app.codacy.com/project/badge/Grade/076af5e6284541d39679c96d16d83772)](https://www.codacy.com/gh/ClaudiuGeorgiu/Obfuscapk)
[![Ubuntu Build Status](https://github.com/ClaudiuGeorgiu/Obfuscapk/workflows/Ubuntu/badge.svg)](https://github.com/ClaudiuGeorgiu/Obfuscapk/actions?query=workflow%3AUbuntu)
[![Windows Build Status](https://github.com/ClaudiuGeorgiu/Obfuscapk/workflows/Windows/badge.svg)](https://github.com/ClaudiuGeorgiu/Obfuscapk/actions?query=workflow%3AWindows)
[![MacOS Build Status](https://github.com/ClaudiuGeorgiu/Obfuscapk/workflows/MacOS/badge.svg)](https://github.com/ClaudiuGeorgiu/Obfuscapk/actions?query=workflow%3AMacOS)
[![Code Coverage](https://codecov.io/gh/ClaudiuGeorgiu/Obfuscapk/badge.svg)](https://codecov.io/gh/ClaudiuGeorgiu/Obfuscapk)
[![Python Version](https://img.shields.io/badge/Python-3.7%2B-green.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/LICENSE)



**Obfuscapk** is a modular Python tool for obfuscating Android apps without needing
their source code, since [`apktool`](https://ibotpeaches.github.io/Apktool/) is used
to decompile the original apk file and to build a new application, after applying some
obfuscation techniques on the decompiled `smali` code, resources and manifest. The
obfuscated app retains the same functionality as the original one, but the differences
under the hood sometimes make the new application very different from the original
(e.g., to signature-based antivirus software).

### :new: Android App Bundle support :new:

Obfuscapk is adding support for
[Android App Bundles](https://developer.android.com/guide/app-bundle) (aab files) by
using [BundleDecompiler](https://github.com/TamilanPeriyasamy/BundleDecompiler) (see
[#121](https://github.com/ClaudiuGeorgiu/Obfuscapk/pull/121)). In order to use this new
feature, download the latest version of BundleDecompiler available from
[here](https://github.com/TamilanPeriyasamy/BundleDecompiler/tree/master/build/libs),
save it as `BundleDecompiler.jar` in a directory included in `PATH` (e.g., in Ubuntu,
`/usr/local/bin` or `/usr/bin`) and make sure it has the executable flag set.

`NOTE:` BundleDecompiler doesn't work on Windows yet, so app bundle obfuscation is not
supported by Obfuscapk on Windows platform. Also, app bundle support is still in early
development, so if you faced any problems or if you want to help us improve, please see
[contributing](#-contributing).



## ❱ Publication

More details about **Obfuscapk** can be found in the paper
"[Obfuscapk: An *open-source* black-box obfuscation tool for Android apps](https://doi.org/10.1016/j.softx.2020.100403)".
You can cite the paper as follows:

```BibTeX
@article{aonzo2020obfuscapk,
    title = "Obfuscapk: An open-source black-box obfuscation tool for Android apps",
    journal = "SoftwareX",
    volume = "11",
    pages = "100403",
    year = "2020",
    issn = "2352-7110",
    doi = "https://doi.org/10.1016/j.softx.2020.100403",
    url = "https://www.sciencedirect.com/science/article/pii/S2352711019302791",
    author = "Simone Aonzo and Gabriel Claudiu Georgiu and Luca Verderame and Alessio Merlo",
    keywords = "Android, Obfuscation, Program analysis"
}
```



## ❱ Demo

![Demo](https://raw.githubusercontent.com/ClaudiuGeorgiu/Obfuscapk/master/docs/demo/cli.gif)



## ❱ Architecture

![Architecture](https://raw.githubusercontent.com/ClaudiuGeorgiu/Obfuscapk/master/docs/architecture/architecture.png)

Obfuscapk is designed to be modular and easy to extend, so it's built using a
[plugin system](https://github.com/tibonihoo/yapsy). Consequently, every obfuscator is
a plugin that inherits from an abstract
[base class](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/src/obfuscapk/obfuscator_category.py)
and needs to implement the method `obfuscate`. When the tool starts processing a new
Android application file, it creates an
[obfuscation object](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/src/obfuscapk/obfuscation.py)
to store all the needed information (e.g., the location of the decompiled `smali` code)
and the internal state of the operations (e.g., the list of already used obfuscators).
Then the obfuscation object is passed, as a parameter to the `obfuscate` method, to all
the active plugins/obfuscators (in sequence) to be processed and modified. The list and
the order of the active plugins is specified through [command line options](#-usage).

The tool is easily extensible with new obfuscators: it's enough to add the source code
implementing the obfuscation technique and the plugin metadata (a
`<obfuscator-name>.obfuscator` file) in the
[`src/obfuscapk/obfuscators`](https://github.com/ClaudiuGeorgiu/Obfuscapk/tree/master/src/obfuscapk/obfuscators)
directory (take a simple existing obfuscator like
[`Nop`](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/src/obfuscapk/obfuscators/nop/nop.py)
as a starting example). The tool will detect automatically the new plugin, so no
further configuration is needed (the new plugin will be treated like all the other
plugins bundled with the tool).



## ❱ Installation

There are two ways of getting a working copy of Obfuscapk on your own computer: either
by [using Docker](#docker-image) or by [using directly the source code](#from-source)
in a `Python 3` environment. In both cases, the first thing to do is to get a local
copy of this repository, so open up a terminal in the directory where you want to save
the project and clone the repository:

```Shell
$ git clone https://github.com/ClaudiuGeorgiu/Obfuscapk.git
```

### Docker image

----------------------------------------------------------------------------------------

#### Prerequisites

This is the suggested way of installing Obfuscapk, since the only requirement is to
have a recent version of Docker installed:

```Shell
$ docker --version
Docker version 20.10.21, build baeda1f
```

#### Official Docker Hub image

The [official Obfuscapk Docker image](https://hub.docker.com/r/claudiugeorgiu/obfuscapk)
is available on Docker Hub (automatically built from this repository):

```Shell
$ # Download the Docker image.
$ docker pull claudiugeorgiu/obfuscapk
$ # Give it a shorter name.
$ docker tag claudiugeorgiu/obfuscapk obfuscapk
```

#### Install

If you downloaded the official image from Docker Hub, you are ready to use the tool so
go ahead and check the [usage instructions](#-usage), otherwise execute the following
command in the previously created `Obfuscapk/src/` directory (the folder containing the
`Dockerfile`) to build the Docker image:

```Shell
$ # Make sure to run the command in Obfuscapk/src/ directory.
$ # It will take some time to download and install all the dependencies.
$ docker build -t obfuscapk .
```

When the Docker image is ready, make a quick test to check that everything was
installed correctly:

```Shell
$ docker run --rm -it obfuscapk --help
usage: python3 -m obfuscapk.cli [-h] -o OBFUSCATOR [-w DIR] [-d OUT_APK_OR_AAB]
...
```

Obfuscapk is now ready to be used, see the [usage instructions](#-usage) for more
information.

### From source

----------------------------------------------------------------------------------------

#### Prerequisites

Make sure to have a recent version of
[`apktool`](https://ibotpeaches.github.io/Apktool/),
[`apksigner`](https://developer.android.com/studio/command-line/apksigner)
and [`zipalign`](https://developer.android.com/studio/command-line/zipalign) installed
and available from the command line:

```Shell
$ apktool
Apktool v2.7.0 - a tool for reengineering Android apk files
...
```
```Shell
$ apksigner
Usage:  apksigner <command> [options]
        apksigner --version
        apksigner --help
...
```
```Shell
$ zipalign
Zip alignment utility
Copyright (C) 2009 The Android Open Source Project
...
```

To support app bundles obfuscation you also need
[BundleDecompiler](https://github.com/TamilanPeriyasamy/BundleDecompiler), so download
the latest available version from
[here](https://github.com/TamilanPeriyasamy/BundleDecompiler/tree/master/build/libs),
save it as `BundleDecompiler.jar` in a directory included in `PATH` (e.g., in Ubuntu,
`/usr/local/bin` or `/usr/bin`) and make sure it has the executable flag set.

To use BundleDecompiler and `apktool` you also need a recent version of Java. 
`zipalign` and `apksigner` are included in the Android SDK. The location of the
executables can also be specified through the following environment variables:
`APKTOOL_PATH`, `BUNDLE_DECOMPILER_PATH`, `APKSIGNER_PATH` and `ZIPALIGN_PATH` (e.g.,
in Ubuntu, run `export APKTOOL_PATH=/custom/location/apktool` before running Obfuscapk
in the same terminal).

Apart from the above tools, the only requirement of this project is a working
`Python 3` (at least `3.7`) installation (along with its package manager `pip`).

#### Install

Run the following commands in the main directory of the project (`Obfuscapk/`) to
install the needed dependencies:

```Shell
$ # Make sure to run the commands in Obfuscapk/ directory.

$ # The usage of a virtual environment is highly recommended.
$ python3 -m venv venv
$ source venv/bin/activate

$ # Install Obfuscapk's requirements.
$ python3 -m pip install -r src/requirements.txt
```

After the requirements are installed, make a quick test to check that everything works
correctly:

```Shell
$ cd src/
$ # The following command has to be executed always from Obfuscapk/src/ directory
$ # or by adding Obfuscapk/src/ directory to PYTHONPATH environment variable.
$ python3 -m obfuscapk.cli --help
usage: python3 -m obfuscapk.cli [-h] -o OBFUSCATOR [-w DIR] [-d OUT_APK_OR_AAB]
...
```

Obfuscapk is now ready to be used, see the [usage instructions](#-usage) for more
information.



## ❱ Usage

From now on, Obfuscapk will be considered as an executable available as `obfuscapk`,
so you need to adapt the commands according to how you installed the tool:

* **Docker image**: a local directory containing the application to obfuscate has to be
mounted to `/workdir` in the container (e.g., the current directory `"${PWD}"`), so the
command:
    ```Shell
    $ obfuscapk [params...]
    ```
    becomes:
    ```Shell
    $ docker run --rm -it -u $(id -u):$(id -g) -v "${PWD}":"/workdir" obfuscapk [params...]
    ```

* **From source**: every instruction has to be executed from the `Obfuscapk/src/`
directory (or by adding `Obfuscapk/src/` directory to `PYTHONPATH` environment
variable) and the command:
    ```Shell
    $ obfuscapk [params...]
    ```
    becomes:
    ```Shell
    $ python3 -m obfuscapk.cli [params...]
    ```

Let's start by looking at the help message:

```Shell
$ obfuscapk --help
obfuscapk [-h] -o OBFUSCATOR [-w DIR] [-d OUT_APK_OR_AAB] [-i] [-p] [-k VT_API_KEY]
          [--keystore-file KEYSTORE_FILE] [--keystore-password KEYSTORE_PASSWORD]
          [--key-alias KEY_ALIAS] [--key-password KEY_PASSWORD] [--use-aapt2]
          <APK_OR_BUNDLE_FILE>
```

There are two mandatory parameters: `<APK_OR_BUNDLE_FILE>`, the path (relative or
absolute) to the apk or app bundle file to obfuscate and the list with the names of the
obfuscation techniques to apply (specified with a `-o` option that can be used multiple
times, e.g., `-o Rebuild -o NewAlignment -o NewSignature`). The other optional arguments
are as follows:

* `-w DIR` is used to set the working directory where to save the intermediate files
(generated by `apktool`). If not specified, a directory named `obfuscation_working_dir`
is created in the same directory as the input application. This can be useful for
debugging purposes, but if it's not needed it can be set to a temporary directory
(e.g., `-w /tmp/`).

* `-d OUT_APK_OR_AAB` is used to set the path of the destination file: the apk file
generated by the obfuscation process (e.g., `-d /home/user/Desktop/obfuscated.apk` or
`-d /home/user/Desktop/obfuscated.aab`). If not specified, the final obfuscated file
will be saved inside the working directory. Note: existing files will be overwritten
without any warning.

* `-i` is a flag for ignoring known third party libraries during the obfuscation
process, to use fewer resources, to increase performances and to reduce the risk of
errors. The
[list of libraries](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/src/obfuscapk/resources/libs_to_ignore.txt)
to ignore is adapted from [LiteRadar](https://github.com/pkumza/LiteRadar) project.

* `-p` is a flag for showing progress bars during the obfuscation operations. When
using the tool in batch operations/automatic builds it's convenient to have progress
bars disabled, otherwise this flag should be enabled to see the obfuscation progress.

* `-k VT_API_KEY` is needed only when using `VirusTotal` obfuscator, to set the API
key to be used when communicating with Virus Total.

* `--keystore-file KEYSTORE_FILE`, `--keystore-password KEYSTORE_PASSWORD`,
`--key-alias KEY_ALIAS` and `--key-password KEY_PASSWORD` can be used to specify a
custom keystore (needed for the apk signing). If `--keystore-file` is used,
`--keystore-password` and `--key-alias` must be specified too, while `--key-password`
is needed only if the chosen key has a different password from the keystore password.
By default (when `--keystore-file` is not specified), a
[keystore bundled with Obfuscapk](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/src/obfuscapk/resources/obfuscation_keystore.jks)
is used for the signing operations.

* `--ignore-packages-file IGNORE_PACKAGES_FILE` is a path to a file which includes
package names to be ignored. All the classes inside those packages will not be
obfuscated when this option is used. The file should have one package name per line as
shown in the example below:
    ```
    com.mycompany.dontobfuscate
    com.mycompany.ignore
    ...
    ```
* `--use-aapt2` is a flag for using aapt2 option when rebuilding an app with `apktool`.

Let's consider now a simple working example to see how Obfuscapk works:

```Shell
$ # original.apk is a valid Android apk file.
$ obfuscapk -o RandomManifest -o Rebuild -o NewAlignment -o NewSignature original.apk
```

When running the above command, this is what happens behind the scenes:

* since no working directory was specified, a new working directory
(`obfuscation_working_dir`) is created in the same location as `original.apk` (this can
be useful to inspect the `smali` files/manifest/resources in case of errors)

* some checks are performed to make sure that all the needed files/executables are
available and ready to be used

* the actual obfuscation process begins: the specified obfuscators are executed
(in order) one by one until there's no obfuscator left or until an error is encountered

    - when running the first obfuscator, `original.apk` is decompiled with `apktool`
    and the results are stored into the working directory

    - since the first obfuscator is `RandomManifest`, the entries in the decompiled
    Android manifest are reordered randomly (without breaking the `xml` structures)

    - `Rebuild` obfuscator simply rebuilds the application (now with the modified
    manifest) using `apktool`, and since no output file was specified, the resulting
    apk file is saved in the working directory created before

    - `NewAlignment` obfuscator uses `zipalign` tool to align the resulting apk file
      
    - `NewSignature` obfuscator signs the newly created apk file with a custom 
      certificate contained in a
      [keystore bundled with Obfuscapk](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/src/obfuscapk/resources/obfuscation_keystore.jks)
      (though a different keystore can be specified with the `--keystore-file` parameter)

* when all the obfuscators have been executed without errors, the resulting obfuscated
apk file can be found in `obfuscation_working_dir/original_obfuscated.apk`, signed,
aligned and ready to be installed into a device/emulator

As seen in the previous example, `Rebuild`, `NewAlignment` and `NewSignature` 
obfuscators are always needed to complete an obfuscation operation, to build the final
obfuscated apk. They are not actual obfuscation techniques, but they are needed in the
build process and so they are included in the list of obfuscators to keep the overall
architecture modular.

Not working as expected? See
[FAQ](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/docs/FAQ.md) and
[troubleshooting](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/docs/TROUBLESHOOTING.md).



## ❱ Obfuscators

The obfuscators included in Obfuscapk can be divided into different categories,
depending on the operations they perform:

* **Trivial**: as the name suggests, this category includes simple operations (that
do not modify much the original application), like signing the apk file with a new
signature.

* **Rename**: operations that change the names of the used identifiers (classes, fields,
methods).

* **Encryption**: packaging encrypted code/resources and decrypting them during the app
execution. When Obfuscapk starts, it automatically generates a random secret key (32
characters long, using ASCII letters and digits) that will be used for encryption.

* **Code**: all the operations that involve the modification of the decompiled source
code.

* **Resources**: operations on the resource files (like modifying the manifest).

* **Other**

The obfuscators currently bundled with Obfuscapk are briefly presented below (in
alphabetical order). Please refer to the source code of the project for more details.

`NOTE:` not all the obfuscators below correspond to real obfuscation techniques (e.g.,
`Rebuild`, `NewAlignment`, `NewSignature` and `VirusTotal`), but they are implemented
as obfuscators to keep the architecture modular and easy to extend with new
functionality.


<details><summary><b>AdvancedReflection</b> [Code]</summary>

> Uses reflection to invoke dangerous APIs of the Android Framework. To find out if a
> method belongs to the Android Framework, Obfuscapk refers to the mapping discovered by
> [Backes et al](https://www.usenix.org/system/files/conference/usenixsecurity16/sec16_paper_backes-android.pdf).  
> [:page_facing_up: AdvancedReflection source code](https://github.com/ClaudiuGeorgiu/Obfuscapk/tree/master/src/obfuscapk/obfuscators/advanced_reflection)
</details>


<details><summary><b>ArithmeticBranch</b> [Code]</summary>

> Insert junk code. In this case, the junk code is composed by arithmetic computations
> and a branch instruction depending on the result of these computations, crafted in
> such a way that the branch is never taken.  
> [:page_facing_up: ArithmeticBranch source code](https://github.com/ClaudiuGeorgiu/Obfuscapk/tree/master/src/obfuscapk/obfuscators/arithmetic_branch)
</details>


<details><summary><b>AssetEncryption</b> [Encryption]</summary>

> Encrypt asset files.  
> [:page_facing_up: AssetEncryption source code](https://github.com/ClaudiuGeorgiu/Obfuscapk/tree/master/src/obfuscapk/obfuscators/asset_encryption)
</details>


<details><summary><b>CallIndirection</b> [Code]</summary>

> This technique modifies the control-flow graph without impacting the code semantics:
> it adds new methods that invoke the original ones. For example, an invocation to the
> method *m1* will be substituted by a new wrapper method *m2*, that, when invoked, it
> calls the original method *m1*.  
> [:page_facing_up: CallIndirection source code](https://github.com/ClaudiuGeorgiu/Obfuscapk/tree/master/src/obfuscapk/obfuscators/call_indirection)
</details>


<details><summary><b>ClassRename</b> [Rename]</summary>

> Change the package name and rename classes (even in the manifest file).  
> [:page_facing_up: ClassRename source code](https://github.com/ClaudiuGeorgiu/Obfuscapk/tree/master/src/obfuscapk/obfuscators/class_rename)
</details>


<details><summary><b>ConstStringEncryption</b> [Encryption]</summary>

> Encrypt constant strings in code.  
> [:page_facing_up: ConstStringEncryption source code](https://github.com/ClaudiuGeorgiu/Obfuscapk/tree/master/src/obfuscapk/obfuscators/const_string_encryption)
</details>


<details><summary><b>DebugRemoval</b> [Code]</summary>

> Remove debug information.  
> [:page_facing_up: DebugRemoval source code](https://github.com/ClaudiuGeorgiu/Obfuscapk/tree/master/src/obfuscapk/obfuscators/debug_removal)
</details>


<details><summary><b>FieldRename</b> [Rename]</summary>

> Rename fields.  
> [:page_facing_up: FieldRename source code](https://github.com/ClaudiuGeorgiu/Obfuscapk/tree/master/src/obfuscapk/obfuscators/field_rename)
</details>


<details><summary><b>Goto</b> [Code]</summary>

> Given a method, it inserts a `goto` instruction pointing to the end of the method and
> another `goto` pointing to the instruction after the first `goto`; it modifies the
> control-flow graph by adding two new nodes.  
> [:page_facing_up: Goto source code](https://github.com/ClaudiuGeorgiu/Obfuscapk/tree/master/src/obfuscapk/obfuscators/goto)
</details>


<details><summary><b>LibEncryption</b> [Encryption]</summary>

> Encrypt native libs.  
> [:page_facing_up: LibEncryption source code](https://github.com/ClaudiuGeorgiu/Obfuscapk/tree/master/src/obfuscapk/obfuscators/lib_encryption)
</details>


<details><summary><b>MethodOverload</b> [Code]</summary>

> It exploits the overloading feature of the Java programming language to assign the
> same name to different methods but using different arguments. Given an already
> existing method, this technique creates a new void method with the same name and
> arguments, but it also adds new random arguments. Then, the body of the new method
> is filled with random arithmetic instructions.  
> [:page_facing_up: MethodOverload source code](https://github.com/ClaudiuGeorgiu/Obfuscapk/tree/master/src/obfuscapk/obfuscators/method_overload)
</details>


<details><summary><b>MethodRename</b> [Rename]</summary>

> Rename methods.  
> [:page_facing_up: MethodRename source code](https://github.com/ClaudiuGeorgiu/Obfuscapk/tree/master/src/obfuscapk/obfuscators/method_rename)
</details>


<details><summary><b>NewAlignment</b> [Trivial]</summary>

> Realign the application.  
> [:page_facing_up: NewAlignment source code](https://github.com/ClaudiuGeorgiu/Obfuscapk/tree/master/src/obfuscapk/obfuscators/new_alignment)
</details>


<details><summary><b>NewSignature</b> [Trivial]</summary>

> Re-sign the application with a new custom signature.  
> [:page_facing_up: NewSignature source code](https://github.com/ClaudiuGeorgiu/Obfuscapk/tree/master/src/obfuscapk/obfuscators/new_signature)
</details>


<details><summary><b>Nop</b> [Code]</summary>

> Insert junk code. Nop, short for *no-operation*, is a dedicated instruction that does
> nothing. This technique just inserts random `nop` instructions within every method
> implementation.  
> [:page_facing_up: Nop source code](https://github.com/ClaudiuGeorgiu/Obfuscapk/tree/master/src/obfuscapk/obfuscators/nop)
</details>


<details><summary><b>RandomManifest</b> [Resource]</summary>

> Randomly reorder entries in the manifest file.  
> [:page_facing_up: RandomManifest source code](https://github.com/ClaudiuGeorgiu/Obfuscapk/tree/master/src/obfuscapk/obfuscators/random_manifest)
</details>


<details><summary><b>Rebuild</b> [Trivial]</summary>

> Rebuild the application.  
> [:page_facing_up: Rebuild source code](https://github.com/ClaudiuGeorgiu/Obfuscapk/tree/master/src/obfuscapk/obfuscators/rebuild)
</details>


<details><summary><b>Reflection</b> [Code]</summary>

> This technique analyzes the existing code looking for method invocations of the app,
> ignoring the calls to the Android framework (see `AdvancedReflection`). If it finds
> an instruction with a suitable method invocation (i.e., no constructor methods,
> public visibility, enough free registers etc.) such invocation is redirected to a
> custom method that will invoke the original method using the Reflection APIs.  
> [:page_facing_up: Reflection source code](https://github.com/ClaudiuGeorgiu/Obfuscapk/tree/master/src/obfuscapk/obfuscators/reflection)
</details>


<details><summary><b>Reorder</b> [Code]</summary>

> This technique consists of changing the order of basic blocks in the code. When a
> branch instruction is found, the condition is inverted (e.g., *branch if lower than*,
> becomes *branch if greater or equal than*) and the target basic blocks are reordered
> accordingly. Furthermore, it also randomly re-arranges the code abusing `goto`
> instructions.  
> [:page_facing_up: Reorder source code](https://github.com/ClaudiuGeorgiu/Obfuscapk/tree/master/src/obfuscapk/obfuscators/reorder)
</details>


<details><summary><b>ResStringEncryption</b> [Encryption]</summary>

> Encrypt strings in resources (only those called inside code).  
> [:page_facing_up: ResStringEncryption source code](https://github.com/ClaudiuGeorgiu/Obfuscapk/tree/master/src/obfuscapk/obfuscators/res_string_encryption)
</details>


<details><summary><b>VirusTotal</b> [Other]</summary>

> Send the original and the obfuscated application to Virus Total. You must provide
> the VT API key (see `-k` option).  
> [:page_facing_up: VirusTotal source code](https://github.com/ClaudiuGeorgiu/Obfuscapk/tree/master/src/obfuscapk/obfuscators/virus_total)
</details>



## ❱ Contributing

Questions, bug reports and pull requests are welcome on GitHub at
[https://github.com/ClaudiuGeorgiu/Obfuscapk](https://github.com/ClaudiuGeorgiu/Obfuscapk)
(see [contributing](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/docs/CONTRIBUTING.md)).
Make sure to also check
[FAQ](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/docs/FAQ.md) and
[troubleshooting](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/docs/TROUBLESHOOTING.md),
since some of the most common questions are already answered there.



## ❱ License

You are free to use this code under the
[MIT License](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/LICENSE).



## ❱ Credits

[![Unige](https://intranet.dibris.unige.it/img/logo_unige.gif)](https://unige.it/en/)
[![Dibris](https://intranet.dibris.unige.it/img/logo_dibris.gif)](https://www.dibris.unige.it/en/)

This software was developed for research purposes at the Computer Security Lab
([CSecLab](https://csec.it/)), hosted at DIBRIS, University of Genoa.



## ❱ Team

* [Simone Aonzo](https://simoneaonzo.it/) - Research Assistant
* [Gabriel Claudiu Georgiu](https://github.com/ClaudiuGeorgiu) - Core Developer
* [Luca Verderame](https://csec.it/people/luca_verderame/) - Postdoctoral Researcher
* [Alessio Merlo](https://csec.it/people/alessio_merlo/) - Faculty Member
