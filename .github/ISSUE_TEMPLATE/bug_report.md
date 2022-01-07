---
name: "\U0001F41E Bug report"
about: "Create a bug report to help us improve Obfuscapk"
title: ""
labels: "bug"
assignees: ""
---

<!--
Thank you for reporting a problem with Obfuscapk.

Please fill in as much of the template below as you can and, if possible, please provide code and apk file(s) needed to replicate the issue. If you leave out information, we can't help you as well.

NOTE:
    * if you're including code snippets/logs, please format them properly (see https://help.github.com/github/writing-on-github/basic-writing-and-formatting-syntax#quoting-code);
    * blocks starting with `< !--` and ending with `-- >` (without spaces) are treated as comments and won't be rendered, so please don't edit the text inside these blocks since your modifications won't be visible. If you want the text to be visible, remove `< !--` and `-- >` tags.
-->



### Prerequisites

Before opening this issue, I tried the following steps:

<!-- Please put an x between the brackets of each line that applies below, so that [ ] becomes [x] (without leaving spaces around the x) -->

* [ ] Installed the tool in a way [described in the readme](https://github.com/ClaudiuGeorgiu/Obfuscapk#-installation) and ran `python3 -m obfuscapk.cli --help` without any errors

* [ ] Ran the tool using: `python3 -m obfuscapk.cli -o Rebuild -o NewAlignment -o NewSignature <YOUR_APP.APK>` to verify that the app is not using anti-repackaging techniques

* [ ] Ran the tool using `--ignore-libs` flag to exclude third party libraries from the obfuscation

* [ ] Checked [FAQ](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/docs/FAQ.md) and [troubleshooting](https://github.com/ClaudiuGeorgiu/Obfuscapk/blob/master/docs/TROUBLESHOOTING.md)

* [ ] Checked for [existing similar issues on GitHub](https://github.com/issues?utf8=✓&q=is%3Aissue+repo%3AClaudiuGeorgiu/Obfuscapk)



### Description

<!-- A clear and concise description of what the issue is (insert text below this line) -->



### Steps to reproduce

1. <!-- First Step -->
2. <!-- Second Step -->
3. <!-- And so on… -->


**Expected behavior:**

<!-- A clear and concise description of what you expected to happen, e.g., the obfuscation should complete without any error message and the obfuscated apk should... (insert text below this line) -->


**Actual behavior:**

<!-- What actually happens, e.g., the obfuscation completes without errors, but when I install the obfuscated apk into a device, it crashes when... (insert text below this line) -->

```
paste here the complete error message, including the command that generated the error
```



### Versions

<!-- Please fill all the applicable fields below to help us replicate the problem -->

* **Installation mode** (e.g., from source or with Docker):
* **Obufscapk version** (e.g., commit 0676488):
* **OS** (e.g., Ubuntu 16.04):
* **Python version** (e.g., 3.7.4):
* **Apktool version** (e.g., v2.4.0):



### Additional information

<!-- Any additional information, configuration or data that might be necessary to reproduce the issue (insert text below this line) -->


**Apk file(s):**

<!-- If applicable, please provide the apk file(s) needed to replicate the problem. Without the file(s) we may not be able to replicate the issue (insert text below this line) -->
