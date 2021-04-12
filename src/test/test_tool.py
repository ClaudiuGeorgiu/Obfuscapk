#!/usr/bin/env python3

import os
import subprocess

import pytest

from obfuscapk.tool import Apktool, ApkSigner, Zipalign

# noinspection PyUnresolvedReferences
from test.test_fixtures import (
    tmp_working_directory_path,
    tmp_demo_apk_v10_original_path,
    tmp_demo_apk_v10_rebuild_path,
    tmp_demo_apk_v10_decoded_files_directory_path,
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
        monkeypatch.setenv("APKTOOL_PATH", "invalid.apktool.path")
        with pytest.raises(RuntimeError):
            Apktool()

    def test_decode_valid_apk(self, tmp_demo_apk_v10_original_path: str):
        output = Apktool().decode(tmp_demo_apk_v10_original_path)
        assert "using apktool" in output.lower()

    def test_decode_error_invalid_apk_path(self):
        with pytest.raises(FileNotFoundError):
            Apktool().decode("invalid.apk.path")

    def test_decode_error_invalid_output_directory(
        self, tmp_demo_apk_v10_original_path: str
    ):
        with pytest.raises(NotADirectoryError):
            Apktool().decode(tmp_demo_apk_v10_original_path, "invalid.directory")

    def test_decode_error_existing_directory(
        self, tmp_working_directory_path: str, tmp_demo_apk_v10_original_path: str
    ):
        with pytest.raises(FileExistsError):
            Apktool().decode(
                tmp_demo_apk_v10_original_path, tmp_working_directory_path, force=False
            )

    def test_decode_error_invalid_file(self, tmp_working_directory_path: str):
        invalid_file_path = os.path.join(tmp_working_directory_path, "invalid.apk")

        with open(invalid_file_path, "w") as invalid_file:
            invalid_file.write("This is not an apk file\n")

        with pytest.raises(subprocess.CalledProcessError):
            Apktool().decode(invalid_file_path, force=True)

    def test_decode_error_generic(
        self, tmp_demo_apk_v10_original_path: str, monkeypatch
    ):
        def mock(*args, **kwargs):
            raise Exception

        monkeypatch.setattr("subprocess.check_output", mock)

        with pytest.raises(Exception):
            Apktool().decode(tmp_demo_apk_v10_original_path, force=True)

    def test_build_valid_apk(
        self,
        tmp_working_directory_path: str,
        tmp_demo_apk_v10_decoded_files_directory_path: str,
    ):
        output_apk_path = os.path.join(tmp_working_directory_path, "output.apk")
        output = Apktool().build(
            tmp_demo_apk_v10_decoded_files_directory_path,
            output_apk_path,
        )
        assert "using apktool" in output.lower()
        assert os.path.isfile(output_apk_path)

    def test_build_error_invalid_input_directory_path(self):
        with pytest.raises(NotADirectoryError):
            Apktool().build("invalid.input.directory.path")

    def test_build_error_invalid_input_directory(self, tmp_working_directory_path: str):
        invalid_directory_path = os.path.join(tmp_working_directory_path, "empty")
        os.makedirs(invalid_directory_path)

        with pytest.raises(subprocess.CalledProcessError):
            Apktool().build(invalid_directory_path)

    def test_build_error_generic(
        self, tmp_demo_apk_v10_decoded_files_directory_path: str, monkeypatch
    ):
        def mock(*args, **kwargs):
            raise Exception

        monkeypatch.setattr("subprocess.check_output", mock)

        with pytest.raises(Exception):
            Apktool().build(tmp_demo_apk_v10_decoded_files_directory_path)


class TestApkSigner(object):
    def test_apksigner_valid_path(self):
        apksigner = ApkSigner()
        assert os.path.isfile(apksigner.apksigner_path)

        output = subprocess.check_output(
            apksigner.apksigner_path, stderr=subprocess.STDOUT
        ).decode()
        assert "usage: apksigner" in output.lower()

    def test_apksigner_wrong_path(self, monkeypatch):
        monkeypatch.setenv("APKSIGNER_PATH", "invalid.apksigner.path")
        with pytest.raises(RuntimeError):
            ApkSigner()

    def test_resign_valid_apk(self, tmp_demo_apk_v10_rebuild_path: str):
        output = ApkSigner().resign(
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
        assert "signed" in output.lower()

    def test_resign_error_generic(
        self, tmp_demo_apk_v10_original_path: str, monkeypatch
    ):
        def mock(*args, **kwargs):
            raise Exception

        monkeypatch.setattr("subprocess.check_output", mock)

        with pytest.raises(Exception):
            ApkSigner().resign(
                tmp_demo_apk_v10_original_path, "ignore", "ignore", "ignore"
            )

    def test_resign_error_signature_removal_error(
        self, tmp_demo_apk_v10_original_path: str, monkeypatch
    ):
        def mock(*args, **kwargs):
            raise Exception

        monkeypatch.setattr("zipfile.ZipFile", mock)

        with pytest.raises(Exception):
            ApkSigner().resign(
                tmp_demo_apk_v10_original_path, "ignore", "ignore", "ignore"
            )

    def test_sign_error_invalid_apk_path(self):
        with pytest.raises(FileNotFoundError):
            ApkSigner().sign("invalid.apk.path", "ignore", "ignore", "ignore")

    def test_sign_error_invalid_file(self, tmp_working_directory_path: str):
        invalid_file_path = os.path.join(tmp_working_directory_path, "invalid.apk")

        with open(invalid_file_path, "w") as invalid_file:
            invalid_file.write("This is not an apk file\n")

        with pytest.raises(subprocess.CalledProcessError):
            ApkSigner().sign(invalid_file_path, "ignore", "ignore", "ignore")

    def test_sign_error_invalid_key_password(self, tmp_demo_apk_v10_rebuild_path: str):
        with pytest.raises(subprocess.CalledProcessError):
            ApkSigner().sign(
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
                "invalid.key.password",
            )


class TestZipalign(object):
    def test_zipalign_valid_path(self):
        zipalign = Zipalign()
        assert os.path.isfile(zipalign.zipalign_path)

        with pytest.raises(subprocess.CalledProcessError) as e:
            subprocess.check_output(zipalign.zipalign_path, stderr=subprocess.STDOUT)
        assert "usage: zipalign" in e.value.output.decode().lower()

    def test_zipalign_wrong_path(self, monkeypatch):
        monkeypatch.setenv("ZIPALIGN_PATH", "invalid.zipalign.path")
        with pytest.raises(RuntimeError):
            Zipalign()

    def test_align_valid_apk(self, tmp_demo_apk_v10_rebuild_path: str):
        output = Zipalign().align(tmp_demo_apk_v10_rebuild_path)
        assert "verification succes" in output.lower()

    def test_align_error_invalid_apk_path(self):
        with pytest.raises(FileNotFoundError):
            Zipalign().align("invalid.apk.path")

    def test_align_error_invalid_file(self, tmp_working_directory_path: str):
        invalid_file_path = os.path.join(tmp_working_directory_path, "invalid.apk")

        with open(invalid_file_path, "w") as invalid_file:
            invalid_file.write("This is not an apk file\n")

        with pytest.raises(subprocess.CalledProcessError):
            Zipalign().align(invalid_file_path)

    def test_align_error_generic(self, tmp_demo_apk_v10_rebuild_path: str, monkeypatch):
        def mock(*args, **kwargs):
            raise Exception

        monkeypatch.setattr("subprocess.check_output", mock)

        with pytest.raises(Exception):
            Zipalign().align(tmp_demo_apk_v10_rebuild_path)
