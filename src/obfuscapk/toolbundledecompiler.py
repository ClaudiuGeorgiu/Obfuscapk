#!/usr/bin/env python3

import logging
import os
import platform
import shutil
import subprocess
from typing import List


class BundleDecompiler(object):
    def __init__(self):
        self.logger = logging.getLogger(
            "{0}.{1}".format(__name__, self.__class__.__name__)
        )

        if platform.system() == "Windows":
            self.logger.warning(
                "BundleDecompiler is not yet available on Windows platform"
            )
            return

        if "BUNDLE_DECOMPILER_PATH" in os.environ:
            self.bundledecompiler_path: str = os.environ["BUNDLE_DECOMPILER_PATH"]
        else:
            self.bundledecompiler_path: str = "BundleDecompiler.jar"

        full_bundledecompiler_path = shutil.which(self.bundledecompiler_path)

        # Make sure bundle decompiler is available
        if not os.path.isfile(full_bundledecompiler_path):
            raise RuntimeError(
                'Cannot find BundleDecompiler with executable "{0}"'.format(
                    full_bundledecompiler_path
                )
            )

        # Make sure to use the full path of the executable (needed for cross-platform
        # compatibility).
        if full_bundledecompiler_path is None:
            raise RuntimeError(
                'Something is wrong with executable "{0}"'.format(
                    self.bundledecompiler_path
                )
            )
        else:
            self.bundledecompiler_path = full_bundledecompiler_path

    def decode(
        self, aab_path: str, output_dir_path: str = None, force: bool = False
    ) -> str:
        if platform.system() == "Windows":
            raise NotImplementedError(
                "BundleDecompiler is not yet available on Windows platform"
            )

        # Check if the aab file to decode is a valid file.
        if not os.path.isfile(aab_path):
            self.logger.error('Unable to find file "{0}"'.format(aab_path))
            raise FileNotFoundError('Unable to find file "{0}"'.format(aab_path))

        # If no output directory is specified, use a new directory in the same
        # directory as the aab file to decode.
        if not output_dir_path:
            output_dir_path = os.path.join(
                os.path.dirname(aab_path),
                os.path.splitext(os.path.basename(aab_path))[0],
            )
            self.logger.debug(
                "No output directory provided, the result will be saved in the "
                "same directory as the input file, in a directory with the same "
                'name as the input file: "{0}"'.format(output_dir_path)
            )

        # If an output directory is provided, make sure that the path to that
        # directory exists (the final directory will be created by aabtool).
        elif not os.path.isdir(os.path.dirname(output_dir_path)):
            self.logger.error(
                'Unable to find output directory "{0}", aabtool won\'t be able to '
                'create the directory "{1}"'.format(
                    os.path.dirname(output_dir_path), output_dir_path
                )
            )
            raise NotADirectoryError(
                'Unable to find output directory "{0}", aabtool won\'t be able to '
                'create the directory "{1}"'.format(
                    os.path.dirname(output_dir_path), output_dir_path
                )
            )

        # Inform the user if an existing output directory is provided without the
        # "force" flag.
        if os.path.isdir(output_dir_path) and not force:
            self.logger.error(
                'Output directory "{0}" already exists, use the "force" flag '
                "to overwrite".format(output_dir_path)
            )
            raise FileExistsError(
                'Output directory "{0}" already exists, use the "force" flag '
                "to overwrite".format(output_dir_path)
            )

        decode_cmd: List[str] = [
            "java",
            "-jar",
            self.bundledecompiler_path,
            "d",
            "--in=" + aab_path,
            "--out=" + output_dir_path,
        ]

        if force:
            self.logger.warning("Bundle Decompiler does not support force")

        try:
            self.logger.info(
                'Running decode command "{0}"'.format(" ".join(decode_cmd))
            )
            # A new line character is sent as input since newer versions of aabtool
            # have an interactive prompt on Windows where the user should press a key.
            output = subprocess.check_output(
                decode_cmd, stderr=subprocess.STDOUT, input=b"\n"
            ).strip()
            if b"Exception in thread " in output:
                # Report exception raised in aabtool.
                raise subprocess.CalledProcessError(1, decode_cmd, output)
            return output.decode(errors="replace")
        except subprocess.CalledProcessError as e:
            self.logger.error(
                "Error during decode command: {0}".format(
                    e.output.decode(errors="replace") if e.output else e
                )
            )
            raise
        except Exception as e:
            self.logger.error("Error during decoding: {0}".format(e))
            raise

    def build(self, source_dir_path: str, output_aab_path: str = None) -> str:
        if platform.system() == "Windows":
            raise NotImplementedError(
                "BundleDecompiler is not yet available on Windows platform"
            )

        # Check if the input directory exists.
        if not os.path.isdir(source_dir_path):
            self.logger.error(
                'Unable to find source directory "{0}"'.format(source_dir_path)
            )
            raise NotADirectoryError(
                'Unable to find source directory "{0}"'.format(source_dir_path)
            )

        # If no output aab path is specified, the new aab will be saved in the
        # default path: <source_dir_path>/dist/<source_dir_name>.aab
        if not output_aab_path:
            output_aab_path = os.path.join(
                source_dir_path,
                "output",
                "{0}.aab".format(os.path.basename(source_dir_path)),
            )
            self.logger.debug(
                "No output aab path provided, the new aab will be saved in the "
                'default path: "{0}"'.format(output_aab_path)
            )

        build_cmd: List[str] = [
            "java",
            "-jar",
            self.bundledecompiler_path,
            "b",
            "--in=" + source_dir_path,
            "--out=" + output_aab_path,
        ]

        try:
            self.logger.info('Running build command "{0}"'.format(" ".join(build_cmd)))
            # A new line character is sent as input since newer versions of aabtool
            # have an interactive prompt on Windows where the user should press a key.
            output = subprocess.check_output(
                build_cmd, stderr=subprocess.STDOUT, input=b"\n"
            ).strip()
            if (
                b"brut.directory.PathNotExist: " in output
                or b"Exception in thread " in output
            ):
                # Report exception raised in aabtool.
                raise subprocess.CalledProcessError(1, build_cmd, output)

            if not os.path.isfile(output_aab_path):
                raise FileNotFoundError(
                    '"{0}" was not built correctly. aabtool output:\n{1}'.format(
                        output_aab_path, output.decode(errors="replace")
                    )
                )

            return output.decode(errors="replace")
        except subprocess.CalledProcessError as e:
            self.logger.error(
                "Error during build command: {0}".format(
                    e.output.decode(errors="replace") if e.output else e
                )
            )
            raise
        except Exception as e:
            self.logger.error("Error during building: {0}".format(e))
            raise


class AABSigner(object):
    def __init__(self):
        self.logger = logging.getLogger(
            "{0}.{1}".format(__name__, self.__class__.__name__)
        )

        if platform.system() == "Windows":
            self.logger.warning(
                "BundleDecompiler is not yet available on Windows platform"
            )
            return

        if "BUNDLE_DECOMPILER_PATH" in os.environ:
            self.aabsigner_path: str = os.environ["BUNDLE_DECOMPILER_PATH"]
        else:
            self.aabsigner_path: str = "BundleDecompiler.jar"

        full_aabsigner_path = shutil.which(self.aabsigner_path)

        # Make sure to use the full path of the executable (needed for cross-platform
        # compatibility).
        if full_aabsigner_path is None:
            raise RuntimeError(
                'Something is wrong with executable "{0}"'.format(self.aabsigner_path)
            )
        else:
            self.aabsigner_path = full_aabsigner_path

    def sign(
        self,
        aab_path: str,
    ) -> str:
        if platform.system() == "Windows":
            raise NotImplementedError(
                "BundleDecompiler is not yet available on Windows platform"
            )

        # Check if the aab file to sign is a valid file.
        if not os.path.isfile(aab_path):
            self.logger.error('Unable to find file "{0}"'.format(aab_path))
            raise FileNotFoundError('Unable to find file "{0}"'.format(aab_path))

        sign_cmd: List[str] = [
            "java",
            "-jar",
            self.aabsigner_path,
            "sign-bundle",
            "--in=" + aab_path,
            "--out=" + aab_path.replace(".aab", "_signed.aab"),
        ]

        try:
            self.logger.info('Running sign command "{0}"'.format(" ".join(sign_cmd)))
            output = subprocess.check_output(sign_cmd, stderr=subprocess.STDOUT).strip()
            return output.decode(errors="replace")
        except subprocess.CalledProcessError as e:
            self.logger.error(
                "Error during sign command: {0}".format(
                    e.output.decode(errors="replace") if e.output else e
                )
            )
            raise
        except Exception as e:
            self.logger.error("Error during signing: {0}".format(e))
            raise
