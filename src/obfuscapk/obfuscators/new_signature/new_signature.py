#!/usr/bin/env python3

import logging

from obfuscapk import obfuscator_category
from obfuscapk.obfuscation import Obfuscation


class NewSignature(obfuscator_category.ITrivialObfuscator):
    def __init__(self):
        self.logger = logging.getLogger(
            "{0}.{1}".format(__name__, self.__class__.__name__)
        )
        super().__init__()

    def obfuscate(self, obfuscation_info: Obfuscation):
        self.logger.info('Running "{0}" obfuscator'.format(self.__class__.__name__))

        try:
            obfuscation_info.sign_obfuscated_apk()
        except Exception as e:
            self.logger.error(
                'Error during execution of "{0}" obfuscator: {1}'.format(
                    self.__class__.__name__, e
                )
            )
            raise

        finally:
            obfuscation_info.used_obfuscators.append(self.__class__.__name__)
