"""
SEMRinterface/tests.py
package github.com/ajk77/SimpleEMRSystem

This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

---TODO---
[] Write the tests.

"""
from django.test import TestCase


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)
