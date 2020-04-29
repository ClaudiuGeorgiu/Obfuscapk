#!/usr/bin/env python3

import os

from yapsy.PluginManager import PluginManager

from obfuscapk import obfuscator_category


class ObfuscatorManager(object):
    def __init__(self):
        # Collect all the obfuscators contained in the ./obfuscators directory. Each
        # obfuscator has an associated *.obfuscator file with some metadata and belongs
        # to a category (see the base class of each obfuscator).
        self.manager = PluginManager(
            directories_list=[
                os.path.join(os.path.dirname(os.path.realpath(__file__)), "obfuscators")
            ],
            plugin_info_ext="obfuscator",
            categories_filter={
                "Trivial": obfuscator_category.ITrivialObfuscator,
                "Rename": obfuscator_category.IRenameObfuscator,
                "Encryption": obfuscator_category.IEncryptionObfuscator,
                "Code": obfuscator_category.ICodeObfuscator,
                "Resources": obfuscator_category.IResourcesObfuscator,
                "Other": obfuscator_category.IOtherObfuscator,
            },
        )
        self.manager.collectPlugins()

    def get_all_obfuscators(self):
        return self.manager.getAllPlugins()

    def get_obfuscators_names(self):
        return [
            ob.name
            for ob in sorted(
                self.get_all_obfuscators(), key=lambda x: (x.category, x.name)
            )
        ]
