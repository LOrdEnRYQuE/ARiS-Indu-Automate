import unittest
from telemetry_freshness import assess_freshness


class TelemetryFreshnessTests(unittest.TestCase):
    def test_recent_observation(self):
        result = assess_freshness({'KUKA-VIRTUAL-01': 100.0}, now=104.0, timeout_seconds=10.0)
        self.assertEqual(result['KUKA-VIRTUAL-01']['telemetry_state'], 'fresh')

    def test_old_observation_is_stale_not_proven_disconnection(self):
        result = assess_freshness({'KUKA-VIRTUAL-01': 100.0}, now=111.0, timeout_seconds=10.0)
        self.assertEqual(result['KUKA-VIRTUAL-01']['telemetry_state'], 'stale')
        self.assertFalse(result['KUKA-VIRTUAL-01']['communication_loss_confirmed'])

    def test_missing_observation_is_unknown(self):
        self.assertEqual(assess_freshness({'KUKA-VIRTUAL-01': None}, now=111.0)['KUKA-VIRTUAL-01']['telemetry_state'], 'unknown')

    def test_future_observation_is_unknown(self):
        self.assertEqual(assess_freshness({'KUKA-VIRTUAL-01': 120.0}, now=111.0)['KUKA-VIRTUAL-01']['telemetry_state'], 'unknown')

    def test_invalid_timeout_rejected(self):
        with self.assertRaises(ValueError):
            assess_freshness({}, now=1.0, timeout_seconds=0)
