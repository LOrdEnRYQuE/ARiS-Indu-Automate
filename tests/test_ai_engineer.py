import unittest
from ai_engineer import analyze

class AIEngineerTests(unittest.TestCase):
    def test_known_alarm_is_grounded(self):
        result = analyze({"equipment_id":"KUKA-VIRTUAL-01","source":"simulator","status":"alarm","alarm_code":"SIM_FEED_BLOCKED"})
        self.assertEqual(result["severity"], "warning")
        self.assertEqual(result["equipment_id"], "KUKA-VIRTUAL-01")
        self.assertEqual(result["basis"], "known_simulator_alarm")
        self.assertFalse(result["machine_command_allowed"])

    def test_unknown_alarm_is_not_diagnosed_as_fact(self):
        result = analyze({"equipment_id":"KUKA-VIRTUAL-01","source":"simulator","status":"alarm","alarm_code":"UNKNOWN"})
        self.assertEqual(result["basis"], "unknown_alarm")
        self.assertIn("Unknown", result["explanation"])
        self.assertFalse(result["machine_command_allowed"])

    def test_normal_status(self):
        result = analyze({"equipment_id":"KUKA-VIRTUAL-01","source":"simulator","status":"running","alarm_code":None})
        self.assertEqual(result["severity"], "info")

    def test_real_source_rejected(self):
        with self.assertRaises(ValueError):
            analyze({"equipment_id":"KUKA-REAL-01","source":"plc","status":"alarm","alarm_code":"SIM_FEED_BLOCKED"})

if __name__ == "__main__":
    unittest.main()
