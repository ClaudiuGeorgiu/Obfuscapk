#!/usr/bin/env python3

from abc import ABC, abstractmethod

from yapsy.IPlugin import IPlugin

from obfuscapk.obfuscation import Obfuscation


class IBaseObfuscator(ABC, IPlugin):
    def __init__(self):
        super().__init__()

        self.is_adding_fields = False
        self.is_adding_methods = False

    @abstractmethod
    def obfuscate(self, obfuscation_info: Obfuscation):
        raise NotImplementedError()


class ITrivialObfuscator(IBaseObfuscator):
    @abstractmethod
    def obfuscate(self, obfuscation_info: Obfuscation):
        raise NotImplementedError()


class IRenameObfuscator(IBaseObfuscator):
    @abstractmethod
    def obfuscate(self, obfuscation_info: Obfuscation):
        raise NotImplementedError()


class IEncryptionObfuscator(IBaseObfuscator):
    @abstractmethod
    def obfuscate(self, obfuscation_info: Obfuscation):
        raise NotImplementedError()


class ICodeObfuscator(IBaseObfuscator):
    @abstractmethod
    def obfuscate(self, obfuscation_info: Obfuscation):
        raise NotImplementedError()


class IResourcesObfuscator(IBaseObfuscator):
    @abstractmethod
    def obfuscate(self, obfuscation_info: Obfuscation):
        raise NotImplementedError()


class IOtherObfuscator(IBaseObfuscator):
    @abstractmethod
    def obfuscate(self, obfuscation_info: Obfuscation):
        raise NotImplementedError()
