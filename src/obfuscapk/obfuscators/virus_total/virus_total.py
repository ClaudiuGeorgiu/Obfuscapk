#!/usr/bin/env python3

import json
import logging
import os
from pprint import pformat
from typing import Optional, Dict

import vt

from obfuscapk import obfuscator_category
from obfuscapk.obfuscation import Obfuscation
from obfuscapk.util import sha256sum


class VirusTotal(obfuscator_category.IOtherObfuscator):
    def __init__(self):
        self.logger = logging.getLogger(
            "{0}.{1}".format(__name__, self.__class__.__name__)
        )
        super().__init__()
        self.vt_session = None

    @staticmethod
    def get_positives(report: Dict) -> int:
        return report["data"]["attributes"]["last_analysis_stats"]["malicious"]

    def get_report_or_none(self, sha256_hash: str) -> Optional[dict]:
        try:
            report = self.vt_session.get_json(f"/files/{sha256_hash}")
            return report
        except vt.error.APIError:
            return None

    def scan_apk_file(self, apk_file_path: str) -> dict:
        self.logger.info('Scanning file "{0}"'.format(apk_file_path))
        sha256_hash = sha256sum(apk_file_path)
        report = self.get_report_or_none(sha256_hash)
        if report is not None:
            return report

        with open(apk_file_path, "rb") as f:
            self.logger.info(f"Uploading '{apk_file_path}' to VirusTotal...")
            analysis = self.vt_session.scan_file(f, wait_for_completion=True)
            assert analysis.status == "completed"

        report = self.get_report_or_none(sha256_hash)
        if report is None:
            raise Exception(
                'Error while retrieving scan for file "{0}"'.format(apk_file_path)
            )
        return report

    def obfuscate(self, obfuscation_info: Obfuscation):
        self.logger.info("Sending original and obfuscated application to Virus Total")

        try:
            if not os.path.isfile(obfuscation_info.obfuscated_apk_path):
                raise FileNotFoundError(
                    "Obfuscated apk was not found. Did you execute the Rebuild "
                    "obfuscator?"
                )

            if obfuscation_info.virus_total_api_key is None:
                raise ValueError(
                    "A valid API key has to be provided in order to submit the "
                    "obfuscated application to Virus Total"
                )

            self.vt_session = vt.Client(obfuscation_info.virus_total_api_key)

            original_report = self.scan_apk_file(obfuscation_info.apk_path)
            self.logger.info(
                "Original apk scan result ({0} positives): {1}".format(
                    self.get_positives(original_report), pformat(original_report)
                )
            )
            obfuscated_report = self.scan_apk_file(obfuscation_info.obfuscated_apk_path)
            self.logger.info(
                "Obfuscated apk scan result ({0} positives): {1}".format(
                    self.get_positives(obfuscated_report),
                    pformat(obfuscated_report),
                )
            )

            # Save Virus Total results in 2 json file (original and obfuscated) in
            # the same directory as the obfuscated apk.
            original_report_path = os.path.join(
                os.path.dirname(obfuscation_info.obfuscated_apk_path),
                "{0}.virustotal-original.json".format(
                    os.path.splitext(os.path.basename(obfuscation_info.apk_path))[0]
                ),
            )
            obfuscated_report_path = os.path.join(
                os.path.dirname(obfuscation_info.obfuscated_apk_path),
                "{0}.virustotal-obfuscated.json".format(
                    os.path.splitext(
                        os.path.basename(obfuscation_info.obfuscated_apk_path)
                    )[0]
                ),
            )
            with open(original_report_path, "w") as original_json, open(
                obfuscated_report_path, "w"
            ) as obfuscated_json:
                original_json.write(
                    json.dumps(
                        {"used_obfuscators": [], "virustotal_scan": original_report},
                        indent=2,
                        sort_keys=True,
                    )
                )
                obfuscated_json.write(
                    json.dumps(
                        {
                            "used_obfuscators": obfuscation_info.used_obfuscators,
                            "virustotal_scan": obfuscated_report,
                        },
                        indent=2,
                        sort_keys=True,
                    )
                )

        except Exception as e:
            self.logger.error("Error during Virus Total analysis: {0}".format(e))
            raise

        finally:
            self.vt_session.close()
            obfuscation_info.used_obfuscators.append(self.__class__.__name__)
