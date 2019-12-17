#!/usr/bin/env python3.7

import json
import logging
import os
import time
from http import HTTPStatus
from itertools import cycle
from pprint import pformat

from virus_total_apis import PublicApi as VirusTotalPublicApi

from obfuscapk import obfuscator_category
from obfuscapk.obfuscation import Obfuscation
from obfuscapk.util import sha256sum


class VirusTotal(obfuscator_category.IOtherObfuscator):

    def __init__(self):
        self.logger = logging.getLogger('{0}.{1}'.format(__name__, self.__class__.__name__))
        super().__init__()

        self.vt_sessions = None

    def get_vt_session(self):
        # Cycle through the Virus Total sessions (one session for each key):
        return next(self.vt_sessions)

    def get_report(self, sha256_hash: str) -> dict:
        sleep_interval = 8  # In seconds.
        attempt = 1
        max_attempts = 16

        for attempt in range(1, max_attempts + 1):
            report = self.get_vt_session().get_file_report(sha256_hash)

            if 'response_code' in report and report['response_code'] == HTTPStatus.OK:
                report_results_rc = report['results']['response_code']
                if report_results_rc == 1:
                    return report

            # Exponential backoff.
            sleep_interval *= attempt
            self.logger.warning('Attempt {0}/{1} (retrying in {2} s), complete result not yet available: {3}'
                                .format(attempt, max_attempts, sleep_interval, report))
            time.sleep(sleep_interval)

        self.logger.error('Maximum number of {0} attempts reached for "{1}"'.format(attempt, sha256_hash))
        raise Exception('Maximum number of attempts reached')

    def scan_apk_file(self, apk_file_path: str) -> dict:
        self.logger.info('Scanning file "{0}"'.format(apk_file_path))

        report = self.get_vt_session().get_file_report(sha256sum(apk_file_path))
        if 'error' in report:
            self.logger.error('Error while retrieving scan for file "{0}": {1}'.format(apk_file_path, report))
            raise Exception('Error while retrieving scan for file "{0}"'.format(apk_file_path))

        rc = report['results']['response_code']

        if rc == 0:
            # The requested resource is not among the finished, queued or pending scans.
            # The apk file needs to be uploaded to Virus Total.
            scan_report = self.get_vt_session().scan_file(apk_file_path)
            if scan_report['response_code'] != HTTPStatus.OK:
                self.logger.error('Error while uploading file "{0}": {1}'.format(apk_file_path, scan_report))
                raise Exception('Error while uploading file "{0}"'.format(apk_file_path))

            report = self.get_report(scan_report['results']['sha256'])

        elif rc != 1:
            # response_code is 1 when Virus Total has a complete result.
            err_msg = report['results']['verbose_msg']
            self.logger.error('Error while retrieving scan for file "{0}": {1}'.format(apk_file_path, err_msg))
            raise Exception('Error while retrieving scan for file "{0}"'.format(apk_file_path))

        return report

    def obfuscate(self, obfuscation_info: Obfuscation):
        self.logger.info('Sending original and obfuscated application to Virus Total')

        try:
            if not os.path.isfile(obfuscation_info.obfuscated_apk_path):
                raise FileNotFoundError('Obfuscated apk was not found. Did you execute the Rebuild obfuscator?')

            if not obfuscation_info.virus_total_api_key:
                raise ValueError('A valid API key has to be provided in order to submit the obfuscated application to '
                                 'Virus Total')

            self.vt_sessions = iter(cycle(VirusTotalPublicApi(key) for key in obfuscation_info.virus_total_api_key))

            original_report = self.scan_apk_file(obfuscation_info.apk_path)
            self.logger.info('Original apk scan result ({0} positives): {1}'
                             .format(original_report['results']['positives'], pformat(original_report)))
            obfuscated_report = self.scan_apk_file(obfuscation_info.obfuscated_apk_path)
            self.logger.info('Obfuscated apk scan result ({0} positives): {1}'
                             .format(obfuscated_report['results']['positives'], pformat(obfuscated_report)))

            # Save Virus Total results in 2 json file (original and obfuscated) in the same directory
            # as the obfuscated apk.
            original_report_path = os.path.join(
                os.path.dirname(obfuscation_info.obfuscated_apk_path),
                '{0}.virustotal-original.json'.format(
                    os.path.splitext(os.path.basename(obfuscation_info.apk_path))[0]))
            obfuscated_report_path = os.path.join(
                os.path.dirname(obfuscation_info.obfuscated_apk_path),
                '{0}.virustotal-obfuscated.json'.format(
                    os.path.splitext(os.path.basename(obfuscation_info.obfuscated_apk_path))[0]))
            with open(original_report_path, 'w') as original_json, open(obfuscated_report_path, 'w') as obfuscated_json:
                original_json.write(json.dumps({
                    'used_obfuscators': [],
                    'virustotal_scan': original_report
                }, indent=2, sort_keys=True))
                obfuscated_json.write(json.dumps({
                    'used_obfuscators': obfuscation_info.used_obfuscators,
                    'virustotal_scan': obfuscated_report
                }, indent=2, sort_keys=True))

        except Exception as e:
            self.logger.error('Error during Virus Total analysis: {0}'.format(e))
            raise

        finally:
            obfuscation_info.used_obfuscators.append(self.__class__.__name__)
