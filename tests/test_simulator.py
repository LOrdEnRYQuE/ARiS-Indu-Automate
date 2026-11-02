import unittest
from simulator import simulate

class TestSimulator(unittest.TestCase):
    def test_production(self):
        events = simulate(3)
        self.assertEqual([x["produced_units"] for x in events], [1, 2, 3])
        self.assertTrue(all(x["status"] == "running" for x in events))

    def test_alarm_freezes_counter(self):
        events = simulate(5, alarm_at=2)
        self.assertEqual([x["produced_units"] for x in events], [1, 2, 2, 2, 2])
        self.assertEqual(events[2]["alarm_code"], "SIM_FEED_BLOCKED")

    def test_invalid_inputs(self):
        for kwargs in ({"cycles": -1}, {"cycles": 2, "alarm_at": 2}, {"cycles": True}):
            with self.assertRaises(ValueError):
                simulate(**kwargs)

    def test_zero_cycles(self):
        self.assertEqual(simulate(0), [])

if __name__ == "__main__":
    unittest.main()
