#!/usr/bin/env python3.7
# coding: utf-8

import logging
import re

from obfuscapk import obfuscator_category
from obfuscapk import util
from obfuscapk.obfuscation import Obfuscation


class DebugRemoval(obfuscator_category.ICodeObfuscator):

    def __init__(self):
        self.logger = logging.getLogger('{0}.{1}'.format(__name__, self.__class__.__name__))
        super().__init__()

    def obfuscate(self, obfuscation_info: Obfuscation):
        self.logger.info('Running "{0}" obfuscator'.format(self.__class__.__name__))

        try:
            debug_op_codes = ['.source ', '.line ', '.prologue', '.epilogue',
                              '.local ', '.end local', '.restart local',
                              '.param ']

            param_with_annotation_pattern = re.compile(r'\.param.+?'
                                                       r'\.annotation.+?'
                                                       r'\.end annotation\n'
                                                       r'\s+\.end param\n', re.UNICODE | re.MULTILINE | re.DOTALL)

            for smali_file in util.show_list_progress(obfuscation_info.get_smali_files(),
                                                      interactive=obfuscation_info.interactive,
                                                      description='Removing debug information'):
                self.logger.debug('Removing debug information from file "{0}"'.format(smali_file))

                with open(smali_file, 'r', encoding='utf-8') as current_file:
                    file_content = current_file.read()

                with open(smali_file, 'w', encoding='utf-8') as current_file:
                    # Remove .param <annotation> .end param.
                    file_content = param_with_annotation_pattern.sub('', file_content)

                    # Keep only the lines not containing debug op codes.
                    lines_to_keep = []
                    for line in file_content.splitlines(keepends=True):
                        if not any(line.strip().startswith(op_code) for op_code in debug_op_codes):
                            lines_to_keep.append(line)
                    current_file.writelines(lines_to_keep)

        except Exception as e:
            self.logger.error('Error during execution of "{0}" obfuscator: {1}'.format(self.__class__.__name__, e))
            raise

        finally:
            obfuscation_info.used_obfuscators.append(self.__class__.__name__)
