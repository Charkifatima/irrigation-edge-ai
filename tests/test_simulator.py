"""Contrat de la démo edge et comportement de la CLI."""
from datetime import datetime
import json
import subprocess
import sys
import unittest

from irrigation_edge_ai.simulator import samples


class SimulatorTest(unittest.TestCase):
    def test_twenty_valid_measurements(self):
        records = list(samples(20, 42))
        self.assertEqual(len(records), 20)
        self.assertEqual([r["sequence"] for r in records], list(range(1, 21)))
        for record in records:
            self.assertTrue(record["simulated"])
            self.assertEqual(record["device_id"], "edge-sim-01")
            self.assertEqual(record["schema_version"], 1)
            self.assertIsNotNone(datetime.fromisoformat(record["timestamp_utc"]).tzinfo)
            for key, lower, upper in (
                ("soil_moisture_pct", 15, 65),
                ("air_temperature_c", 18, 38),
                ("relative_humidity_pct", 25, 85),
            ):
                self.assertGreaterEqual(record[key], lower)
                self.assertLessEqual(record[key], upper)

    def test_seed_reproduces_values(self):
        first = list(samples(3, 42))
        second = list(samples(3, 42))
        for record in first + second:
            record.pop("timestamp_utc")
        self.assertEqual(first, second)
        different = list(samples(3, 7))
        for record in different:
            record.pop("timestamp_utc")
        self.assertNotEqual(first, different)

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-m", "irrigation_edge_ai.simulator", *args],
            capture_output=True, text=True, timeout=10,
        )

    def test_cli_outputs_json_lines_and_exits(self):
        result = self.run_cli("--count", "20", "--interval", "0")
        self.assertEqual(result.returncode, 0, result.stderr)
        records = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual(len(records), 20)
        self.assertEqual(records[-1]["sequence"], 20)

    def test_cli_rejects_invalid_count(self):
        for value in ("0", "-1", "abc"):
            with self.subTest(value=value):
                result = self.run_cli("--count", value, "--interval", "0")
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")

    def test_cli_rejects_invalid_interval(self):
        for value in ("-1", "nan", "inf", "abc"):
            with self.subTest(value=value):
                result = self.run_cli("--interval", value)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
