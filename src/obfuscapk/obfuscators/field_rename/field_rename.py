#!/usr/bin/env python3.7

import logging
from typing import List, Set

from obfuscapk import obfuscator_category
from obfuscapk import util
from obfuscapk.obfuscation import Obfuscation


class FieldRename(obfuscator_category.IRenameObfuscator):

    def __init__(self):
        self.logger = logging.getLogger('{0}.{1}'.format(__name__, self.__class__.__name__))
        super().__init__()

        self.is_adding_fields = True

        self.max_fields_to_add = 0
        self.added_fields = 0

    def rename_field(self, field_name: str) -> str:
        field_md5 = util.get_string_md5(field_name)
        return 'f{0}'.format(field_md5.lower()[:8])

    def add_random_fields(self, original_field_declaration: str):
        if self.added_fields < self.max_fields_to_add:
            for _ in range(util.get_random_int(1, 4)):
                print('\n', end='')
                print(original_field_declaration.replace(':', '{0}:'.format(util.get_random_string(8))), end='')
                self.added_fields += 1

    def get_sdk_class_names(self, smali_files: List[str]) -> Set[str]:
        class_names: Set[str] = set()
        for smali_file in smali_files:
            with open(smali_file, 'r', encoding='utf-8') as current_smali_file:
                for line in current_smali_file:
                    class_match = util.class_pattern.match(line)
                    if class_match:
                        # This is probably a SDK class, but we have its declaration so we can
                        # change the fields inside it.
                        if class_match.group('class_name').startswith(('Landroid', 'Ljava')):
                            class_names.add(class_match.group('class_name'))
                        # There is only one class declaration per file.
                        break
        return class_names

    def rename_field_declarations(self, smali_files: List[str], interactive: bool = False) -> Set[str]:
        renamed_fields: Set[str] = set()

        # Search for field definitions that can be renamed.
        for smali_file in util.show_list_progress(smali_files,
                                                  interactive=interactive,
                                                  description='Renaming field declarations'):
            with util.inplace_edit_file(smali_file) as current_smali_file:
                for line in current_smali_file:
                    # Field declared in class.
                    field_match = util.field_pattern.match(line)

                    if field_match:
                        field_name = field_match.group('field_name')
                        # Avoid sub-fields.
                        if '$' not in field_name:
                            # Rename field declaration (usages of this field will be renamed later) and add some
                            # random fields.
                            line = line.replace(
                                '{0}:'.format(field_name),
                                '{0}:'.format(self.rename_field(field_name))
                            )
                            print(line, end='')
                            self.add_random_fields(line)

                            field = '{field_name}:{field_type}'.format(
                                field_name=field_match.group('field_name'),
                                field_type=field_match.group('field_type')
                            )
                            renamed_fields.add(field)
                        else:
                            print(line, end='')
                    else:
                        print(line, end='')

        return renamed_fields

    def rename_field_references(self, fields_to_rename: Set[str], smali_files: List[str],
                                sdk_classes: Set[str], interactive: bool = False):
        for smali_file in util.show_list_progress(smali_files,
                                                  interactive=interactive,
                                                  description='Renaming field references'):
            with util.inplace_edit_file(smali_file) as current_smali_file:
                for line in current_smali_file:
                    # Field usage.
                    field_usage_match = util.field_usage_pattern.match(line)
                    if field_usage_match:
                        field = '{field_name}:{field_type}'.format(
                            field_name=field_usage_match.group('field_name'),
                            field_type=field_usage_match.group('field_type')
                        )
                        class_name = field_usage_match.group('field_object')
                        field_name = field_usage_match.group('field_name')
                        if field in fields_to_rename and \
                                (not class_name.startswith(('Landroid', 'Ljava')) or class_name in sdk_classes):
                            # Rename field usage.
                            print(line.replace(
                                '{0}:'.format(field_name),
                                '{0}:'.format(self.rename_field(field_name))
                            ), end='')
                        else:
                            print(line, end='')
                    else:
                        print(line, end='')

    def obfuscate(self, obfuscation_info: Obfuscation):
        self.logger.info('Running "{0}" obfuscator'.format(self.__class__.__name__))

        try:
            sdk_class_declarations = self.get_sdk_class_names(obfuscation_info.get_smali_files())
            renamed_field_declarations: Set[str] = set()

            # There is a field limit for dex files.
            self.max_fields_to_add = obfuscation_info.get_remaining_fields_per_obfuscator()
            self.added_fields = 0

            if obfuscation_info.is_multidex():
                for index, dex_smali_files in enumerate(
                        util.show_list_progress(obfuscation_info.get_multidex_smali_files(),
                                                interactive=obfuscation_info.interactive, unit='dex',
                                                description='Processing multidex')):
                    self.max_fields_to_add = obfuscation_info.get_remaining_fields_per_obfuscator()[index]
                    self.added_fields = 0
                    renamed_field_declarations.update(self.rename_field_declarations(dex_smali_files,
                                                                                     obfuscation_info.interactive))
            else:
                renamed_field_declarations = self.rename_field_declarations(obfuscation_info.get_smali_files(),
                                                                            obfuscation_info.interactive)

            # When renaming field references it makes no difference if this is a multidex application,
            # since at this point we are not introducing any new field.
            self.rename_field_references(renamed_field_declarations, obfuscation_info.get_smali_files(),
                                         sdk_class_declarations, obfuscation_info.interactive)

        except Exception as e:
            self.logger.error('Error during execution of "{0}" obfuscator: {1}'.format(self.__class__.__name__, e))
            raise

        finally:
            obfuscation_info.used_obfuscators.append(self.__class__.__name__)
