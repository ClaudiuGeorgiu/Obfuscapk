#!/usr/bin/env python3

import os

import pytest

from obfuscapk import cli

# noinspection PyUnresolvedReferences
from test.test_fixtures import (
    tmp_working_directory_path,
    tmp_demo_apk_v10_original_path,
)


class TestCommandLine(object):
    def test_valid_basic_command_without_quotes(
        self,
        tmp_working_directory_path: str,
        tmp_demo_apk_v10_original_path: str,
        monkeypatch,
    ):
        obfuscated_apk_path = os.path.join(tmp_working_directory_path, "obfuscated.apk")

        # Mock the command line parser.
        arguments = cli.get_cmd_args(
            "-w {working_dir} -d {destination} "
            "-o Rebuild -o NewAlignment -o NewSignature {apk_file}".format(
                working_dir=tmp_working_directory_path,
                destination=obfuscated_apk_path,
                apk_file=tmp_demo_apk_v10_original_path,
            ).split()
        )
        monkeypatch.setattr(cli, "get_cmd_args", lambda: arguments)

        cli.main()

        assert os.path.isfile(obfuscated_apk_path)

    def test_valid_basic_command_with_quotes(
        self,
        tmp_working_directory_path: str,
        tmp_demo_apk_v10_original_path: str,
        monkeypatch,
    ):
        obfuscated_apk_path = os.path.join(tmp_working_directory_path, "obfuscated.apk")

        # Mock the command line parser.
        arguments = cli.get_cmd_args(
            "-w '{working_dir}' -d \"{destination}\" "
            "-o Rebuild -k \"key1\" -k 'key2' '{apk_file}'".format(
                working_dir=tmp_working_directory_path,
                destination=obfuscated_apk_path,
                apk_file=tmp_demo_apk_v10_original_path,
            ).split()
        )
        monkeypatch.setattr(cli, "get_cmd_args", lambda: arguments)

        cli.main()

        assert os.path.isfile(obfuscated_apk_path)

    def test_valid_basic_command_with_custom_keystore(
        self,
        tmp_working_directory_path: str,
        tmp_demo_apk_v10_original_path: str,
        monkeypatch,
    ):
        obfuscated_apk_path = os.path.join(tmp_working_directory_path, "obfuscated.apk")

        # Mock the command line parser.
        arguments = cli.get_cmd_args(
            "-w {working_dir} -d {destination} "
            "-o Rebuild -o NewAlignment -o NewSignature "
            "--keystore-file {keystore_file} --keystore-password {keystore_password} "
            "--key-alias {key_alias} --key-password {key_password} {apk_file}".format(
                working_dir=tmp_working_directory_path,
                destination=obfuscated_apk_path,
                apk_file=tmp_demo_apk_v10_original_path,
                keystore_file=os.path.join(
                    os.path.dirname(__file__),
                    os.path.pardir,
                    "obfuscapk",
                    "resources",
                    "obfuscation_keystore.jks",
                ),
                keystore_password="obfuscation_password",
                key_alias="obfuscation_key",
                key_password="obfuscation_password",
            ).split()
        )
        monkeypatch.setattr(cli, "get_cmd_args", lambda: arguments)

        cli.main()

        assert os.path.isfile(obfuscated_apk_path)

    def test_missing_required_parameters(self, monkeypatch):
        # Mock the command line parser.
        original = cli.get_cmd_args
        monkeypatch.setattr(cli, "get_cmd_args", lambda: original([]))

        with pytest.raises(SystemExit) as e:
            cli.main()
        assert e.value.code == 2

    def test_missing_external_tool(self, monkeypatch):
        monkeypatch.setenv("APKTOOL_PATH", "invalid.apktool.path")

        # Mock the command line parser.
        arguments = cli.get_cmd_args("-o Rebuild ignore.apk".split())
        monkeypatch.setattr(cli, "get_cmd_args", lambda: arguments)

        with pytest.raises(RuntimeError) as e:
            cli.main()
        assert "Something is wrong with executable" in str(e.value)
