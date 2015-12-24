# -*- coding: utf-8 -*-

# The parametrize function is generated, so this doesn't work:
#
#     from pytest.mark import parametrize
#
import pytest
parametrize = pytest.mark.parametrize

from btsprice.misc import get_median


class TestMain(object):
    logfile = open("/tmp/test-btsprice.log", 'a')

    def test_get_median(self):
        assert get_median([1, 2, 3, 4]) == 2.5
        assert get_median([1, 2, 3]) == 2
        assert get_median([1]) == 1
        assert get_median([]) is None
