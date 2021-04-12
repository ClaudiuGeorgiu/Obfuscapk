#!/usr/bin/env python3

import os

import pytest

from obfuscapk.main import check_external_tool_dependencies, perform_obfuscation
from obfuscapk.obfuscation import Obfuscation
from obfuscapk.tool import Apktool

# noinspection PyUnresolvedReferences
from test.test_fixtures import (
    tmp_working_directory_path,
    tmp_demo_apk_v10_original_path,
    tmp_demo_apk_v10_rebuild_path,
)


# noinspection PyProtectedMember
class TestObfuscation(object):
    def test_valid_external_tools(self):
        # If something is wrong an exception will be thrown and the test will fail.
        check_external_tool_dependencies()

    def test_perform_full_obfuscation_valid_apk(
        self,
        tmp_working_directory_path: str,
        tmp_demo_apk_v10_original_path: str,
    ):
        obfuscated_apk_path = os.path.join(tmp_working_directory_path, "obfuscated.apk")
        perform_obfuscation(
            tmp_demo_apk_v10_original_path,
            [
                "DebugRemoval",
                "LibEncryption",
                "CallIndirection",
                "MethodRename",
                "AssetEncryption",
                "MethodOverload",
                "ConstStringEncryption",
                "ResStringEncryption",
                "ArithmeticBranch",
                "FieldRename",
                "Nop",
                "Goto",
                "ClassRename",
                "Reflection",
                "AdvancedReflection",
                "Reorder",
                "RandomManifest",
                "Rebuild",
                "NewAlignment",
                "NewSignature",
            ],
            tmp_working_directory_path,
            obfuscated_apk_path,
            interactive=True,
            ignore_libs=True,
        )
        assert os.path.isfile(obfuscated_apk_path)

    def test_perform_obfuscation_error_missing_external_tool(self, monkeypatch):
        monkeypatch.setenv("APKTOOL_PATH", "invalid.apktool.path")
        with pytest.raises(RuntimeError) as e:
            perform_obfuscation("ignore.apk", [])
        assert "Something is wrong with executable" in str(e.value)

    def test_perform_obfuscation_error_invalid_apk_path(self):
        with pytest.raises(FileNotFoundError):
            perform_obfuscation("invalid.apk.path", [])

    def test_perform_obfuscation_error_invalid_obfuscator_name(
        self,
        tmp_demo_apk_v10_original_path: str,
    ):
        with pytest.raises(ValueError):
            perform_obfuscation(
                tmp_demo_apk_v10_original_path,
                ["invalid.obfuscator.name"],
            )

    def test_perform_obfuscation_error_generic_obfuscator_error(
        self, tmp_working_directory_path: str
    ):
        # The Rebuild obfuscator will fail with an invalid input file.
        invalid_file_path = os.path.join(tmp_working_directory_path, "invalid.apk")

        with open(invalid_file_path, "w") as invalid_file:
            invalid_file.write("This is not an apk file\n")

        with pytest.raises(Exception):
            perform_obfuscation(invalid_file_path, ["Rebuild"])

    def test_obfuscation_error_invalid_apk_path(self):
        with pytest.raises(FileNotFoundError):
            Obfuscation("invalid.apk.path")

    def test_obfuscation_error_working_dir_creation(
        self, tmp_demo_apk_v10_original_path: str, monkeypatch
    ):
        def mock(*args, **kwargs):
            raise Exception

        monkeypatch.setattr("os.makedirs", mock)

        with pytest.raises(Exception):
            Obfuscation(tmp_demo_apk_v10_original_path)

    def test_obfuscation_get_total_fields(self, tmp_demo_apk_v10_original_path: str):
        obfuscation = Obfuscation(tmp_demo_apk_v10_original_path)
        total_fields = obfuscation._get_total_fields()
        assert isinstance(total_fields, int)
        assert total_fields > 10

    def test_obfuscation_get_total_methods(self, tmp_demo_apk_v10_original_path: str):
        obfuscation = Obfuscation(tmp_demo_apk_v10_original_path)
        total_methods = obfuscation._get_total_methods()
        assert isinstance(total_methods, int)
        assert total_methods > 10

    def test_obfuscation_get_remaining_fields(
        self, tmp_demo_apk_v10_original_path: str
    ):
        obfuscation = Obfuscation(tmp_demo_apk_v10_original_path)
        remaining_fields = obfuscation._get_remaining_fields()
        assert isinstance(remaining_fields, int)
        assert remaining_fields > 63500

    def test_obfuscation_get_remaining_methods(
        self, tmp_demo_apk_v10_original_path: str
    ):
        obfuscation = Obfuscation(tmp_demo_apk_v10_original_path)
        remaining_methods = obfuscation._get_remaining_methods()
        assert isinstance(remaining_methods, int)
        assert remaining_methods > 63500

    def test_obfuscation_decode_apk_success(self, tmp_demo_apk_v10_original_path: str):
        obfuscation = Obfuscation(
            tmp_demo_apk_v10_original_path, ignore_libs=True, interactive=True
        )

        assert not obfuscation._decoded_apk_path

        obfuscation.decode_apk()

        assert os.path.isdir(obfuscation._decoded_apk_path)

    def test_obfuscation_decode_apk_error(
        self, tmp_demo_apk_v10_original_path: str, monkeypatch
    ):
        def mock(*args, **kwargs):
            raise Exception

        monkeypatch.setattr(Apktool, "decode", mock)

        obfuscation = Obfuscation(
            tmp_demo_apk_v10_original_path, ignore_libs=True, interactive=True
        )

        with pytest.raises(Exception):
            obfuscation.decode_apk()

    def test_obfuscation_remaining_fields_per_obfuscator(
        self, tmp_demo_apk_v10_original_path: str
    ):
        obfuscation = Obfuscation(tmp_demo_apk_v10_original_path)
        obfuscators_adding_fields = 3
        obfuscation.obfuscators_adding_fields = obfuscators_adding_fields
        result = obfuscation.get_remaining_fields_per_obfuscator()
        assert isinstance(result, int)
        assert (
            result == obfuscation._get_remaining_fields() // obfuscators_adding_fields
        )

    def test_obfuscation_remaining_methods_per_obfuscator(
        self, tmp_demo_apk_v10_original_path: str
    ):
        obfuscation = Obfuscation(tmp_demo_apk_v10_original_path)
        obfuscators_adding_methods = 3
        obfuscation.obfuscators_adding_methods = obfuscators_adding_methods
        result = obfuscation.get_remaining_methods_per_obfuscator()
        assert isinstance(result, int)
        assert (
            result == obfuscation._get_remaining_methods() // obfuscators_adding_methods
        )

    def test_obfuscation_build_obfuscated_apk_success(
        self,
        tmp_working_directory_path: str,
        tmp_demo_apk_v10_original_path: str,
    ):
        obfuscated_apk_path = os.path.join(tmp_working_directory_path, "obfuscated.apk")
        obfuscation = Obfuscation(
            tmp_demo_apk_v10_original_path,
            tmp_working_directory_path,
            obfuscated_apk_path,
        )

        assert not os.path.isfile(obfuscated_apk_path)

        obfuscation.build_obfuscated_apk()

        assert os.path.isfile(obfuscated_apk_path)

    def test_obfuscation_build_obfuscated_apk_error(
        self, tmp_demo_apk_v10_original_path: str
    ):
        obfuscation = Obfuscation(tmp_demo_apk_v10_original_path)
        obfuscation._is_decoded = True
        obfuscation._decoded_apk_path = "invalid.decoded.apk.path"

        with pytest.raises(Exception):
            obfuscation.build_obfuscated_apk()

    def test_obfuscation_sign_obfuscated_apk_success(
        self,
        tmp_working_directory_path: str,
        tmp_demo_apk_v10_original_path: str,
        tmp_demo_apk_v10_rebuild_path: str,
    ):
        obfuscated_apk_path = os.path.join(tmp_working_directory_path, "obfuscated.apk")
        obfuscation = Obfuscation(
            tmp_demo_apk_v10_original_path,
            tmp_working_directory_path,
            obfuscated_apk_path,
        )
        obfuscation.obfuscated_apk_path = tmp_demo_apk_v10_rebuild_path

        # In case of errors an exception would be thrown and the test would fail.
        obfuscation.sign_obfuscated_apk()

    def test_obfuscation_sign_obfuscated_apk_error_invalid_apk(
        self, tmp_demo_apk_v10_original_path: str
    ):
        obfuscation = Obfuscation(tmp_demo_apk_v10_original_path)
        obfuscation.obfuscated_apk_path = "invalid.apk.path"

        with pytest.raises(Exception):
            obfuscation.sign_obfuscated_apk()

    def test_obfuscation_sign_obfuscated_apk_error_missing_keystore_file(
        self,
        tmp_working_directory_path: str,
        tmp_demo_apk_v10_original_path: str,
        tmp_demo_apk_v10_rebuild_path: str,
    ):
        obfuscated_apk_path = os.path.join(tmp_working_directory_path, "obfuscated.apk")
        obfuscation = Obfuscation(
            tmp_demo_apk_v10_original_path,
            tmp_working_directory_path,
            obfuscated_apk_path,
            keystore_file="invalid.keystore.path",
        )
        obfuscation.obfuscated_apk_path = tmp_demo_apk_v10_rebuild_path

        with pytest.raises(FileNotFoundError):
            obfuscation.sign_obfuscated_apk()

    def test_obfuscation_sign_obfuscated_apk_error_missing_keystore_password(
        self,
        tmp_working_directory_path: str,
        tmp_demo_apk_v10_original_path: str,
        tmp_demo_apk_v10_rebuild_path: str,
    ):
        obfuscated_apk_path = os.path.join(tmp_working_directory_path, "obfuscated.apk")
        obfuscation = Obfuscation(
            tmp_demo_apk_v10_original_path,
            tmp_working_directory_path,
            obfuscated_apk_path,
            keystore_file=os.path.join(
                os.path.dirname(__file__),
                os.path.pardir,
                "obfuscapk",
                "resources",
                "obfuscation_keystore.jks",
            ),
            key_password=None,
        )
        obfuscation.obfuscated_apk_path = tmp_demo_apk_v10_rebuild_path

        with pytest.raises(ValueError):
            obfuscation.sign_obfuscated_apk()

    def test_obfuscation_align_obfuscated_apk_success(
        self,
        tmp_working_directory_path: str,
        tmp_demo_apk_v10_original_path: str,
        tmp_demo_apk_v10_rebuild_path: str,
    ):
        obfuscated_apk_path = os.path.join(tmp_working_directory_path, "obfuscated.apk")
        obfuscation = Obfuscation(
            tmp_demo_apk_v10_original_path,
            tmp_working_directory_path,
            obfuscated_apk_path,
        )
        obfuscation.obfuscated_apk_path = tmp_demo_apk_v10_rebuild_path

        # In case of errors an exception would be thrown.
        obfuscation.align_obfuscated_apk()

    def test_obfuscation_align_obfuscated_apk_error(
        self, tmp_demo_apk_v10_original_path: str
    ):
        obfuscation = Obfuscation(tmp_demo_apk_v10_original_path)
        obfuscation.obfuscated_apk_path = "invalid.apk.path"

        with pytest.raises(Exception):
            obfuscation.align_obfuscated_apk()

    def test_is_multidex(self, tmp_demo_apk_v10_original_path: str):
        obfuscation = Obfuscation(tmp_demo_apk_v10_original_path)
        is_multidex = obfuscation.is_multidex()
        assert is_multidex is False

    def test_get_manifest_file(self, tmp_demo_apk_v10_original_path: str):
        obfuscation = Obfuscation(tmp_demo_apk_v10_original_path)
        manifest = obfuscation.get_manifest_file()
        assert os.path.isfile(manifest)

    def test_get_smali_files(self, tmp_demo_apk_v10_original_path: str):
        obfuscation = Obfuscation(tmp_demo_apk_v10_original_path)
        smali_files = obfuscation.get_smali_files()
        assert len(smali_files) > 5
        assert all(os.path.isfile(smali_file) for smali_file in smali_files)

    def test_get_multidex_smali_files(self, tmp_demo_apk_v10_original_path: str):
        obfuscation = Obfuscation(tmp_demo_apk_v10_original_path)
        smali_files = obfuscation.get_multidex_smali_files()
        # This test application is not multidex.
        assert len(smali_files) == 0

    def test_get_native_lib_files(self, tmp_demo_apk_v10_original_path: str):
        obfuscation = Obfuscation(tmp_demo_apk_v10_original_path)
        native_libs = obfuscation.get_native_lib_files()
        assert len(native_libs) > 0
        assert all(os.path.isfile(native_lib) for native_lib in native_libs)

    def test_get_assets_directory(self, tmp_demo_apk_v10_original_path: str):
        obfuscation = Obfuscation(tmp_demo_apk_v10_original_path)
        assets_dir = obfuscation.get_assets_directory()
        assert os.path.isdir(assets_dir)
        assert "message.txt" in os.listdir(assets_dir)

    def test_get_resource_directory(self, tmp_demo_apk_v10_original_path: str):
        obfuscation = Obfuscation(tmp_demo_apk_v10_original_path)
        resource_dir = obfuscation.get_resource_directory()
        assert os.path.isdir(resource_dir)
        assert "drawable" in os.listdir(resource_dir)
