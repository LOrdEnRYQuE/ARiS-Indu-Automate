import unittest
from gateway import Gateway
from simulator import simulate
from demo_seed import seed_demo


class DemoSeedTests(unittest.TestCase):
    def test_add_missing_second_machine_without_overwriting_first(self):
        gateway = Gateway(':memory:')
        try:
            for event in simulate(3, alarm_at=2):
                gateway.ingest(event)
            self.assertEqual(seed_demo(gateway), 10)
            self.assertEqual(gateway.summary()['event_count'], 13)
            self.assertEqual(seed_demo(gateway), 0)
        finally:
            gateway.close()

    def test_seed_empty_database_once(self):
        gateway = Gateway(':memory:')
        try:
            self.assertEqual(seed_demo(gateway), 20)
            self.assertEqual(gateway.summary()['equipment_count'], 2)
            self.assertEqual(seed_demo(gateway), 0)
        finally:
            gateway.close()
