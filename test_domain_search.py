#!/usr/bin/env python
# coding: utf-8


import threading
import unittest

import domain_search


class TestDomainSearch(unittest.TestCase):

    def test_can_taken_via_whois(self):
        lock = threading.Lock()
        self.assertTrue(domain_search.can_taken_via_dig('alibabaaldkefcefj.com', lock))


if __name__ == '__main__':
    unittest.main()
