from unittest import TestSuite


def test_suite():
    from confparse.tests import (
        test_config,
        test_parser,
        test_util
        )
    modules = [
        test_config,
        test_parser,
        test_util
        ]
    suites = map(lambda x: x.test_suite(), modules)
    return TestSuite(suites)
