from gohlkegrabber.gohlkegrabber import version_compare
from unittest import TestCase


class TestVersionCompare(TestCase):
    def _all_ops(self, lesser, greater, size):
        self.assertTrue(version_compare(lesser, '==', lesser),
                        f'{size} digit versions {lesser} == {lesser}')
        self.assertFalse(version_compare(lesser, '==', greater),
                         f'{size} digit versions not {lesser} == {greater}')

        self.assertTrue(version_compare(lesser, '<=', lesser),
                        f'equal {size} digit versions {lesser} <= {lesser}')
        self.assertTrue(version_compare(lesser, '<=', greater),
                        f'lesser {size} digit versions {lesser} <= {greater}')
        self.assertFalse(version_compare(greater, '<=', lesser),
                         f'greater {size} digit versions not {greater} <= {lesser}')

        self.assertTrue(version_compare(lesser, '>=', lesser),
                        f'equal {size} digit versions  {lesser} >= {lesser}')
        self.assertTrue(version_compare(greater, '>=', lesser),
                        f'greater {size} digit versions {greater} >= {lesser}')
        self.assertFalse(version_compare(lesser, '>=', greater),
                         f'lesser {size} digit versions not {lesser} >= {greater}')

        self.assertTrue(version_compare(greater, '>', lesser),
                        f'greater {size} digit versions {greater} > {lesser}')
        self.assertFalse(version_compare(lesser, '>', lesser),
                         f'equal {size} digit versions not  {lesser} > {lesser}')
        self.assertFalse(version_compare(lesser, '>', greater),
                         f'lesser {size} digit versions not {lesser} > {greater}')

        self.assertTrue(version_compare(lesser, '<', greater),
                        f'lesser {size} digit versions {lesser} < {greater}')
        self.assertFalse(version_compare(lesser, '<', lesser),
                         f'equal {size} digit versions not  {lesser} < {lesser}')
        self.assertFalse(version_compare(greater, '<', lesser),
                         f'greater {size} digit versions not {greater} <>=> {lesser}')

    def test_single(self):
        self._all_ops('1', '2', 'single')
        self._all_ops('1', '12', 'single')
        self._all_ops('3', '21', 'single')

    def test_double(self):
        self._all_ops('1.1', '2.1', 'double')
        self._all_ops('1.1', '2.0', 'double')
        self._all_ops('1.0', '1.1', 'double')
        self._all_ops('1', '1.1', 'double')
        self._all_ops('1.1', '2', 'double')
        self._all_ops('1.2', '1.12', 'double')

    def test_triple(self):
        self._all_ops('1.0.1', '1.0.2', 'triple')
        self._all_ops('1.0.2', '1.1.0', 'triple')
        self._all_ops('1.1.1', '2.1.1', 'triple')
        self._all_ops('1.0.0', '1.1', 'triple')
        self._all_ops('2.1', '2.1.1', 'triple')
        self._all_ops('2.1.2', '2.1.10', 'double')

    def test_mixed(self):
        self._all_ops('1', '1a', 'mixed')
        self._all_ops('1a', '1b', 'mixed')
        self._all_ops('3a', '21', 'mixed')
        self._all_ops('1.0', '1.0b', 'mixed')
        self._all_ops('1.0a', '1.0b', 'mixed')
        self._all_ops('1.0.0a', '1.0.0b', 'mixed')
