#!/usr/bin/env python3

import argparse
import logging

from obfuscapk.main import perform_obfuscation, check_external_tool_dependencies
from obfuscapk.obfuscator_manager import ObfuscatorManager

logger = logging.getLogger(__name__)


def get_cmd_args(args: list = None):
    """
    Parse and return the command line parameters needed for the script execution.

    :param args: List of arguments to be parsed (by default sys.argv is used).
    :return: The command line needed parameters.
    """

    obfuscators = ObfuscatorManager().get_obfuscators_names()

    parser = argparse.ArgumentParser(
        prog="python3 -m obfuscapk.cli",
        description="Obfuscate an application (.apk) without needing its source code.",
    )
    parser.add_argument(
        "apk_file",
        type=str,
        metavar="<APK_FILE>",
        help="The path to the application (.apk) to obfuscate",
    )
    parser.add_argument(
        "-o",
        "--obfuscator",
        action="append",
        metavar="OBFUSCATOR",
        choices=obfuscators,
        help="The name of the obfuscator to use. Can be specified multiple times to "
        "use more obfuscators (in sequence). Allowed values are: {0}".format(
            ", ".join(obfuscators)
        ),
        required=True,
    )
    parser.add_argument(
        "-w",
        "--working-dir",
        type=str,
        metavar="DIR",
        help="The working directory that will contain the intermediate files. By "
        "default a directory will be created in the same directory as the input "
        "application. If the specified directory doesn't exist, it will be created",
    )
    parser.add_argument(
        "-d",
        "--destination",
        type=str,
        metavar="OUT_APK",
        help="The path where to save the obfuscated .apk file. By default the file "
        "will be saved in the working directory",
    )
    parser.add_argument(
        "-i",
        "--ignore-libs",
        action="store_true",
        help="Ignore known third party libraries during the obfuscation operations",
    )
    parser.add_argument(
        "-p",
        "--show-progress",
        action="store_true",
        dest="interactive",
        help="Show obfuscation progress (as a progress bar)",
    )
    parser.add_argument(
        "-k",
        "--virus-total-key",
        action="append",
        metavar="VT_API_KEY",
        help="When using Virus Total obfuscator, a valid API key has to be provided. "
        "Can be specified multiple times to use a different API key for each request "
        "(cycling through the API keys)",
    )
    parser.add_argument(
        "--keystore-file",
        type=str,
        metavar="KEYSTORE_FILE",
        help="The path to a custom keystore file to be used for signing the obfuscated "
        ".apk file. By default a keystore bundled with this tool will be used",
    )
    parser.add_argument(
        "--keystore-password",
        type=str,
        metavar="KEYSTORE_PASSWORD",
        help="The password of the custom keystore used for signing the obfuscated .apk "
        "file (needed only when specifying a custom keystore file)",
    )
    parser.add_argument(
        "--key-alias",
        type=str,
        metavar="KEY_ALIAS",
        help="The key alias for signing the obfuscated .apk file (needed only when "
        "specifying a custom keystore file)",
    )
    parser.add_argument(
        "--key-password",
        type=str,
        metavar="KEY_PASSWORD",
        help="The key password for signing the obfuscated .apk file (needed only when "
        "specifying a custom keystore file)",
    )
    return parser.parse_args(args)


def main():
    """
    A full command to obfuscate an application:

    python3 -m obfuscapk.cli -p -i -w /working/dir/path -d /path/to/obfuscated.apk \
    -o DebugRemoval -o LibEncryption -o CallIndirection -o MethodRename \
    -o AssetEncryption -o MethodOverload -o ConstStringEncryption \
    -o ResStringEncryption -o ArithmeticBranch -o FieldRename -o Nop -o Goto \
    -o ClassRename -o Reflection -o AdvancedReflection -o Reorder -o RandomManifest \
    -o Rebuild -o NewSignature -o NewAlignment \
    -o VirusTotal -k virus_total_key_1 -k virus_total_key_2 \
    /path/to/original.apk
    """

    # Verify that the external dependencies are available even before showing the help
    # message: this way, if the help message is displayed correctly it means that all
    # the needed external tools are available and ready to be used.
    check_external_tool_dependencies()

    arguments = get_cmd_args()

    if arguments.apk_file:
        arguments.apk_file = arguments.apk_file.strip(" '\"")

    if arguments.working_dir:
        arguments.working_dir = arguments.working_dir.strip(" '\"")

    if arguments.destination:
        arguments.destination = arguments.destination.strip(" '\"")

    if arguments.virus_total_key:
        arguments.virus_total_key = [
            key.strip(" '\"") for key in arguments.virus_total_key
        ]

    if arguments.keystore_file:
        arguments.keystore_file = arguments.keystore_file.strip(" '\"")

    if arguments.keystore_password:
        arguments.keystore_password = arguments.keystore_password.strip(" '\"")

    if arguments.key_alias:
        arguments.key_alias = arguments.key_alias.strip(" '\"")

    if arguments.key_password:
        arguments.key_password = arguments.key_password.strip(" '\"")

    perform_obfuscation(
        arguments.apk_file,
        arguments.obfuscator,
        arguments.working_dir,
        arguments.destination,
        arguments.interactive,
        arguments.ignore_libs,
        arguments.virus_total_key,
        arguments.keystore_file,
        arguments.keystore_password,
        arguments.key_alias,
        arguments.key_password,
    )


if __name__ == "__main__":
    main()
