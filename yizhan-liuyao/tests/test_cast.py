import itertools
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from cast import chart

TIME = '2026-10-04T06:00:00+08:00'


class CastTests(unittest.TestCase):
    def test_known_chart(self):
        result = chart([7, 8, 7, 8, 6, 8], TIME)
        self.assertEqual(result['base'], '地火明夷')
        self.assertEqual(result['changed'], '水火既济')
        self.assertEqual([y['position'] for y in result['lines'] if y['is_changing']], [5])

    def test_timezone_equivalence(self):
        self.assertEqual(chart([7]*6, TIME), chart([7]*6, '2026-10-03T22:00:00+00:00'))

    def test_reject_invalid_inputs(self):
        for values, stamp in [([7]*5, TIME), ([5]*6, TIME), ([True]*6, TIME),
                              ([7]*6, '2026-10-04T06:00:00'), ([7]*6, 'bad')]:
            with self.assertRaises(ValueError):
                chart(values, stamp)

    def test_all_line_combinations(self):
        for values in itertools.product((6, 7, 8, 9), repeat=6):
            result = chart(list(values), TIME)
            self.assertEqual(len(result['lines']), 6)
            self.assertIn(result['shi'], range(1, 7))
            self.assertEqual(abs(result['shi']-result['ying']), 3)
            for v, line in zip(values, result['lines']):
                self.assertEqual(line['yin_yang'], v % 2)
                self.assertEqual(line['changed']['yin_yang'], (v % 2) ^ (v in (6, 9)))


if __name__ == '__main__':
    unittest.main()
