#!/usr/bin/env python3

import itertools
import logging
import os
import random
import re
import string
from contextlib import contextmanager
from hashlib import md5, sha256
from typing import List

from tqdm import tqdm

logger = logging.getLogger(__name__)

# A seed to be used for random operations.
random_seed = 42
random.seed(random_seed)

########################################################################################
#                                Common regex patterns.                                #
########################################################################################

# L<class_name>;  # Every class name starts with L and ends with ;
class_name_pattern = re.compile(r"L[^():\s]+?;", re.UNICODE)

# .class <other_optional_stuff> <class_name;>  # Every class name ends with ;
class_pattern = re.compile(r"\.class.+?(?P<class_name>\S+?;)", re.UNICODE)

# .super <class_name;>  # Every class name ends with ;
super_class_pattern = re.compile(r"\.super\s(?P<class_name>\S+?;)", re.UNICODE)

# .locals <number>
locals_pattern = re.compile(r"\s+\.locals\s(?P<local_count>\d+)")

# .field <other_optional_stuff> <field_name>:<field_type> <optional_initialization>
field_pattern = re.compile(
    r"\.field.+?(?P<field_name>\S+?):" r"(?P<field_type>\S+)", re.UNICODE
)

# .method <other_optional_stuff> <method_name>(<param>)<return_type>
method_pattern = re.compile(
    r"\.method.+?(?P<method_name>\S+?)"
    r"\((?P<method_param>\S*?)\)"
    r"(?P<method_return>\S+)",
    re.UNICODE,
)

# <spaces> value = <class_name>-><method>(<param>)<return_type>
annotation_method_pattern = re.compile(
    r"\s+value\s=\s(?P<method_object>\S+?)"
    r"->(?P<method_name>\S+?)"
    r"\((?P<method_param>\S*?)\)"
    r"(?P<method_return>\S+)",
    re.UNICODE,
)

# <spaces> <usage_type> <param>, <field_object>-><field_name>:<field_type>
field_usage_pattern = re.compile(
    r"\s+(?P<usage_type>[is](get|put)\S*)\s"
    r"(?P<field_param>[vp0-9,\s]+),\s"
    r"(?P<field_object>\S+?)"
    r"->(?P<field_name>\S+?):"
    r"(?P<field_type>\S+)",
    re.UNICODE,
)

# <spaces> invoke-<type> {<passed_param>}, <class_name>-><method>(<param>)<return_type>
invoke_pattern = re.compile(
    r"\s+(?P<invoke_type>invoke-\S+)\s"
    r"{(?P<invoke_pass>[vp0-9,.\s]*)},\s"
    r"(?P<invoke_object>\S+?)"
    r"->(?P<invoke_method>\S+?)"
    r"\((?P<invoke_param>\S*?)\)"
    r"(?P<invoke_return>\S+)",
    re.UNICODE,
)

# <spaces> const-string <register>, "<string>"  # This also matches const-string/jumbo
const_string_pattern = re.compile(
    r"\s+const-string(/jumbo)?\s(?P<register>[vp0-9]+),\s" r'"(?P<string>.+)"',
    re.UNICODE,
)


########################################################################################


# When iterating over list L, "for element in show_list_progress(L, interactive=True)"
# will show a progress bar. When setting "interactive=False", no progress bar will be
# shown. While using this method, no other code should write to standard output.
def show_list_progress(
    the_list: list,
    interactive: bool = False,
    unit: str = "file",
    description: str = None,
):
    if not interactive:
        return the_list
    else:
        return tqdm(
            the_list,
            dynamic_ncols=True,
            unit=unit,
            desc=description,
            bar_format="{l_bar}{bar}|[{elapsed}<{remaining}, {rate_fmt}]",
        )


def get_random_int(min_int: int, max_int: int) -> int:
    return random.randint(min_int, max_int)


def get_random_string(length: int) -> str:
    return "".join(random.choices(string.ascii_letters, k=length))


def get_random_list_permutations(input_list: list) -> list:
    permuted_list = list(itertools.permutations(input_list))
    random.shuffle(permuted_list)
    return permuted_list


def get_file_hash(file_path: str, hash_function, block_size=65536) -> str:
    with open(file_path, "rb", buffering=0) as f:
        for chunk in iter(lambda: f.read(block_size), b""):
            hash_function.update(chunk)
    return hash_function.hexdigest()


def md5sum(file_path: str) -> str:
    return get_file_hash(file_path, md5())


def sha256sum(file_path: str) -> str:
    return get_file_hash(file_path, sha256())


def get_string_md5(input_string: str) -> str:
    return md5(input_string.encode()).hexdigest()


# Adapted from https://www.zopatista.com/python/2013/11/26/inplace-file-rewriting/
@contextmanager
def inplace_edit_file(file_name: str):
    """
    Allow for a file to be replaced with new content.

    Yield a tuple of (readable, writable) file objects, where writable replaces
    readable. If an exception occurs, the old file is restored, removing the
    written data.
    """

    backup_file_name = "{0}{1}{2}".format(file_name, os.extsep, "bak")

    try:
        os.unlink(backup_file_name)
    except OSError:
        pass
    os.rename(file_name, backup_file_name)

    readable = open(backup_file_name, "r", encoding="utf-8")
    try:
        perm = os.fstat(readable.fileno()).st_mode
    except OSError:
        writable = open(file_name, "w", encoding="utf-8", newline="")
    else:
        os_mode = os.O_CREAT | os.O_WRONLY | os.O_TRUNC
        if hasattr(os, "O_BINARY"):
            os_mode |= os.O_BINARY
        fd = os.open(file_name, os_mode, perm)
        writable = open(fd, "w", encoding="utf-8", newline="")
        try:
            if hasattr(os, "chmod"):
                os.chmod(file_name, perm)
        except OSError:
            pass
    try:
        yield readable, writable
    except Exception as e:
        try:
            os.unlink(file_name)
        except OSError:
            pass
        os.rename(backup_file_name, file_name)

        logger.error(
            'Error during inplace editing file "{0}": {1}'.format(file_name, e)
        )
        raise
    finally:
        readable.close()
        writable.close()
        try:
            os.unlink(backup_file_name)
        except OSError:
            pass


def get_text_from_file(file_name: str) -> str:
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        logger.error('Error during reading file "{0}": {1}'.format(file_name, e))
        raise


def get_non_empty_lines_from_file(file_name: str) -> List[str]:
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            # Return a list with the non blank lines contained in the file.
            return list(filter(None, (line.rstrip() for line in file)))
    except Exception as e:
        logger.error('Error during reading file "{0}": {1}'.format(file_name, e))
        raise


# Adapted from https://github.com/pkumza/LiteRadar
def get_libs_to_ignore() -> List[str]:
    return get_non_empty_lines_from_file(
        os.path.join(os.path.dirname(__file__), "resources", "libs_to_ignore.txt")
    )


# Adapted from https://github.com/reddr/axplorer
def get_dangerous_api() -> List[str]:
    return get_non_empty_lines_from_file(
        os.path.join(os.path.dirname(__file__), "resources", "dangerous_api.txt")
    )


def get_nop_valid_op_codes() -> List[str]:
    return get_non_empty_lines_from_file(
        os.path.join(os.path.dirname(__file__), "resources", "nop_valid_op_codes.txt")
    )


def get_code_block_valid_op_codes() -> List[str]:
    return get_non_empty_lines_from_file(
        os.path.join(
            os.path.dirname(__file__), "resources", "code_block_valid_op_codes.txt"
        )
    )


def get_android_class_names() -> List[str]:
    return get_non_empty_lines_from_file(
        os.path.join(
            os.path.dirname(__file__), "resources", "android_class_names_api_27.txt"
        )
    )


def get_smali_method_overload() -> str:
    return get_text_from_file(
        os.path.join(
            os.path.dirname(__file__),
            "resources",
            "smali",
            "overloaded_method_body.smali",
        )
    )


def get_decrypt_asset_smali_code(encryption_secret: str) -> str:
    text = get_text_from_file(
        os.path.join(
            os.path.dirname(__file__), "resources", "smali", "DecryptAsset.smali"
        )
    )
    return replace_default_secret_key(text, encryption_secret)


def get_decrypt_string_smali_code(encryption_secret: str) -> str:
    text = get_text_from_file(
        os.path.join(
            os.path.dirname(__file__), "resources", "smali", "DecryptString.smali"
        )
    )
    return replace_default_secret_key(text, encryption_secret)


def replace_default_secret_key(text: str, encryption_secret: str) -> str:
    return text.replace("This-key-need-to-be-32-character", encryption_secret)


def get_api_reflection_smali_code() -> str:
    return get_text_from_file(
        os.path.join(
            os.path.dirname(__file__), "resources", "smali", "ApiReflection.smali"
        )
    )


def get_advanced_api_reflection_smali_code() -> str:
    return get_text_from_file(
        os.path.join(
            os.path.dirname(__file__),
            "resources",
            "smali",
            "AdvancedApiReflection.smali",
        )
    )
