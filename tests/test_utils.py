#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Unit tests for the dogtail.procedural API
"""
__author__ = "Zack Cerza <zcerza@redhat.com>"

import unittest
import dogtail.tree
import dogtail.predicate
import dogtail.i18n
import os.path
import dogtail.version
dogtail.config.config.logDebugToFile = False
dogtail.config.config.logDebugToStdOut = True
from gtkdemotest import GtkDemoTest


class TestScreenshot(GtkDemoTest):

    def make_expected_and_compare(self, actual_path, jpg_tolerance=None):
        extension = actual_path.split('.')[-1]
        expected_path = actual_path.replace(extension, "expected." + extension)

        import os
        os.system("gnome-screenshot -f %s" % expected_path)

        command = ["compare", "-metric", "MAE",
                   actual_path, expected_path, "output"]
        import subprocess
        p = subprocess.Popen(command, stderr=subprocess.PIPE)
        output, error = p.communicate()

        import re
        m = re.search(r"\((.*)\)", error)
        self.assertTrue(0.1 >= float(m.group(1)))

    def test_screenshot_incorrect_timestamp(self):
        self.assertRaises(
            TypeError, dogtail.utils.screenshot, "timeStamp", None)

    def test_screenshot_default(self):
        actual_path = dogtail.utils.screenshot()
        self.make_expected_and_compare(actual_path)

    def test_screenshot_basename(self):
        actual_path = dogtail.utils.screenshot("basename")
        self.make_expected_and_compare(actual_path)

    def test_screenshot_no_time_stamp(self):
        actual_path = dogtail.utils.screenshot(timeStamp=False)
        self.make_expected_and_compare(actual_path)

    def test_screenshot_jpeg(self):
        actual_path = dogtail.utils.screenshot("basename.jpg")
        self.make_expected_and_compare(actual_path, jpg_tolerance=True)

    def test_screenshot_unknown_format(self):
        self.assertRaises(ValueError, dogtail.utils.screenshot, "basename.dat")


class TestA11Y(unittest.TestCase):

    def test_bail_when_a11y_disabled(self):
        self.assertRaises(SystemExit, dogtail.utils.bailBecauseA11yIsDisabled)

    def test_enable_a11y(self):
        dogtail.utils.enableA11y()


class TestLock(unittest.TestCase):
    def test_set_unrandomized_lock(self):
        test_lock = dogtail.utils.Lock(lockname='test.lock', randomize=False)
        self.assertEquals(test_lock.lockdir, "/tmp/test.lock")
        self.assertFalse(os.path.isdir(test_lock.lockdir))
        test_lock.lock()
        self.assertTrue(os.path.isdir(test_lock.lockdir))
        test_lock.unlock()
        self.assertFalse(os.path.isdir(test_lock.lockdir))

    def test_double_lock(self):
        test_lock = dogtail.utils.Lock(lockname='test.lock', randomize=False)
        test_lock.lock()
        with self.assertRaises(OSError):
            test_lock.lock()

    def test_double_unlock(self):
        test_lock = dogtail.utils.Lock(lockname='test.lock', randomize=False)
        test_lock.lock()
        test_lock.unlock()
        with self.assertRaises(OSError):
            test_lock.unlock()

    def test_lock_on_del(self):
        test_lock = dogtail.utils.Lock(lockname='test.lock', randomize=False)
        test_lock.lock()
        test_dir = test_lock.lockdir
        del test_lock
        self.assertFalse(os.path.isdir(test_dir))

    def test_randomize(self):
        test_lock = dogtail.utils.Lock(lockname='test.lock', randomize=True)
        self.assertIn("/tmp/test.lock", test_lock.lockdir)
        self.assertFalse(os.path.isdir(test_lock.lockdir))
        test_lock.lock()
        self.assertTrue(os.path.isdir(test_lock.lockdir))
        test_lock.unlock()
        self.assertFalse(os.path.isdir(test_lock.lockdir))


class TestI18N(unittest.TestCase):
    def test_safeDecode(self):
        self.assertEquals(dogtail.i18n.safeDecode("woot"), "woot")
        self.assertEquals(dogtail.i18n.safeDecode(u"woot"), "woot")
        self.assertEquals(
            dogtail.i18n.safeDecode(u"непонятные буквы"),
            u'\u043d\u0435\u043f\u043e\u043d\u044f\u0442\u043d\u044b\u0435 \u0431\u0443\u043a\u0432\u044b')

    def test_load_all_translations_for_language(self):
        dogtail.i18n.loadAllTranslationsForLanguage('en_US')

# Breaks travis builds on Ubuntu: PackageNotFoundError: language-pack-gnome-en
#    def test_load_translations_for_package(self):
#        dogtail.i18n.loadTranslationsFromPackageMoFiles('kernel')


class TestVersion(unittest.TestCase):
    def test_version_from_string_list(self):
        version = dogtail.version.Version([1, 2, 3])
        self.assertEquals(str(version), "1.2.3")

    def test_version_from_string(self):
        version = dogtail.version.Version.fromString("1.2.3")
        self.assertEquals(str(version), "1.2.3")

    def test_version_less_than(self):
        version = dogtail.version.Version.fromString("1.2.3")
        version_less1 = dogtail.version.Version.fromString("1.2.2")
        version_less2 = dogtail.version.Version.fromString("1.1.3")
        version_less3 = dogtail.version.Version.fromString("0.8.3")
        self.assertTrue(version_less1 < version)
        self.assertTrue(version_less2 < version)
        self.assertTrue(version_less3 < version)
        self.assertTrue(version_less1 <= version)
        self.assertTrue(version_less2 <= version)
        self.assertTrue(version_less3 <= version)

    def test_version_more_than(self):
        version = dogtail.version.Version.fromString("1.2.3")
        version_less1 = dogtail.version.Version.fromString("1.2.2")
        version_less2 = dogtail.version.Version.fromString("1.1.3")
        version_less3 = dogtail.version.Version.fromString("0.8.3")
        self.assertTrue(version > version_less1)
        self.assertTrue(version > version_less2)
        self.assertTrue(version > version_less3)
        self.assertTrue(version >= version_less1)
        self.assertTrue(version >= version_less2)
        self.assertTrue(version >= version_less3)

    def test_version_equals(self):
        version = dogtail.version.Version([1, 2, 3])
        version1 = dogtail.version.Version.fromString("1.2.3")
        version2 = dogtail.version.Version.fromString("1.2.2")
        self.assertTrue(version == version1)
        self.assertFalse(version == version2)
        self.assertTrue(version >= version1)
        # FIXME: Fails here
        #self.assertFalse(version >= version2)
        self.assertTrue(version <= version1)
        self.assertFalse(version <= version2)
        self.assertFalse(version != version1)
        self.assertFalse(version1 != version)
        self.assertTrue(version2 != version)
        self.assertTrue(version2 != version1)
