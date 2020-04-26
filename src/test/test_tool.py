#!/usr/bin/env python3

import os
import subprocess

import pytest

from obfuscapk.tool import Apktool, Jarsigner, Zipalign

from test.test_fixtures import (
    tmp_working_directory_path,
    tmp_demo_apk_v10_original_path,
    tmp_demo_apk_v10_rebuild_path,
)


class TestApktool(object):
    def test_apktool_valid_path(self):
        apktool = Apktool()
        assert os.path.isfile(apktool.apktool_path)

        output = subprocess.check_output(
            apktool.apktool_path, stderr=subprocess.STDOUT, input=b"\n"
        ).decode()
        assert "usage: apktool" in output.lower()

    def test_apktool_wrong_path(self, monkeypatch):
        monkeypatch.setenv("APKTOOL_PATH", "wrong.apktool.path")
        with pytest.raises(RuntimeError):
            Apktool()

    def test_decode_valid_apk(self, tmp_demo_apk_v10_original_path: str):
        apktool = Apktool()
        output = apktool.decode(tmp_demo_apk_v10_original_path)
        assert "using apktool" in output.lower()

    def test_decode_wrong_apk(self):
        with pytest.raises(FileNotFoundError):
            Apktool().decode("wrong.apk.path")


class TestJarsigner(object):
    def test_jarsigner_valid_path(self):
        jarsigner = Jarsigner()
        assert os.path.isfile(jarsigner.jarsigner_path)

        output = subprocess.check_output(
            jarsigner.jarsigner_path, stderr=subprocess.STDOUT
        ).decode()
        assert "usage: jarsigner" in output.lower()

    def test_jarsigner_wrong_path(self, monkeypatch):
        monkeypatch.setenv("JARSIGNER_PATH", "wrong.jarsigner.path")
        with pytest.raises(RuntimeError):
            Jarsigner()

    def test_resign_valid_apk(self, tmp_demo_apk_v10_rebuild_path: str):
        jarsigner = Jarsigner()
        output = jarsigner.resign(
            tmp_demo_apk_v10_rebuild_path,
            os.path.join(
                os.path.dirname(__file__),
                os.path.pardir,
                "obfuscapk",
                "resources",
                "obfuscation_keystore.jks",
            ),
            "obfuscation_password",
            "obfuscation_key",
        )
        assert "jar signed" in output.lower()

    def test_sign_wrong_apk(self):
        with pytest.raises(FileNotFoundError):
            Jarsigner().sign("wrong.apk.path", "ignore", "ignore", "ignore")


class TestZipalign(object):
    def test_zipalign_valid_path(self):
        zipalign = Zipalign()
        assert os.path.isfile(zipalign.zipalign_path)

        with pytest.raises(subprocess.CalledProcessError) as e:
            subprocess.check_output(zipalign.zipalign_path, stderr=subprocess.STDOUT)
        assert "usage: zipalign" in e.value.output.decode().lower()

    def test_zipalign_wrong_path(self, monkeypatch):
        monkeypatch.setenv("ZIPALIGN_PATH", "wrong.zipalign.path")
        with pytest.raises(RuntimeError):
            Zipalign()

    def test_align_valid_apk(self, tmp_demo_apk_v10_rebuild_path: str):
        zipalign = Zipalign()
        output = zipalign.align(tmp_demo_apk_v10_rebuild_path)
        assert "verification succes" in output.lower()

    def test_align_wrong_apk(self):
        with pytest.raises(FileNotFoundError):
            Zipalign().align("wrong.apk.path")
