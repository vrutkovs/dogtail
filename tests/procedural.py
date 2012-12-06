#!/usr/bin/python
"""
Unit tests for the dogtail.procedural API
"""
__author__ = "Zack Cerza <zcerza@redhat.com>"

import unittest
from dogtail.procedural import *
config.logDebugToFile = False
config.logDebugToStdOut = True
import pyatspi
import Node

class GtkDemoTest(Node.GtkDemoTest):
    def setUp(self):
        self.pid = run('gtk-demo')
        self.app = focus.application.node

    #FIXME: Implement doubleclick() in d.procedural and override the other 
    # methods of Node.GtkDemoTest


class TestFocusApplication(GtkDemoTest):
    def testFocusingBogusName(self):
        config.fatalErrors = True
        self.assertRaises(FocusError, focus.application, "should not be found")

    def testFocusingBasic(self):
        "Ensure that focus.application() sets focus.application.node properly"
        focus.application.node = None
        focus.application("gtk-demo")
        self.assertEquals(focus.application.node, self.app)


class TestFocusWidget(GtkDemoTest):
    def testFocusingEmptyName(self):
        self.assertRaises(TypeError, focus.widget)

    def testFocusingBogusName(self):
        focus.widget("should not be found")
        self.assertEquals(focus.widget.node, None)

    def testThrowExceptionFocusingBogusName(self):
        config.fatalErrors = True
        self.assertRaises(FocusError, focus.widget, "should not be found")

    def testFocusingBasic(self):
        "Ensure that focus.widget('foo') finds a node with name 'foo'"
        focus.widget("Application main window")
        self.assertEquals(focus.widget.name, "Application main window")


class TestFocusWindow(GtkDemoTest):
    def testFocusingBogusName(self):
        focus.window("should not be found")
        self.assertEquals(focus.window.node, None)


class TestFocusDialog(GtkDemoTest):
    def testFocusingBogusName(self):
        focus.dialog("should not be found")
        self.assertEquals(focus.dialog.node, None)


class TestFocus(GtkDemoTest):
    def testInitialState(self):
        "Ensure that focus.widget, focus.dialog and focus.window are None " + \
                "initially."
        self.assertEquals(focus.widget.node, None)
        self.assertEquals(focus.dialog.node, None)
        self.assertEquals(focus.window.node, None)

    def testFocusingApp(self):
        "Ensure that focus.app() works like focus.application()"
        focus.app.node = None
        focus.app('gtk-demo')
        self.assertEquals(focus.app.node, self.app)

    def testFocusingRoleName(self):
        "Ensure that focus.widget(roleName=...) works."
        focus.widget(roleName = 'page tab')
        self.assert_(isinstance(focus.widget.node, tree.Node))
        self.assertEquals(focus.widget.node.role, pyatspi.ROLE_PAGE_TAB)

    def testFocusMenu(self):
        self.runDemo('Application main window')
        focus.window('Application Window')
        focus.menu('File')
        self.assert_(isinstance(focus.widget.node, tree.Node))
        self.assertEquals(focus.widget.node.role, pyatspi.ROLE_MENU)

class TestKeyCombo(GtkDemoTest):
    def testKeyCombo(self):
        self.runDemo('Application main window')
        focus.window('Application Window')
        keyCombo("<ctrl>a")
        focus.dialog('About GTK+ Code Demos')

class TestActions(GtkDemoTest):
    def testClick(self):
        click('Source')
        self.assertTrue(focus.widget.isSelected)

    def testSelect(self):
        select('Source')
        self.assertTrue(focus.widget.isSelected)

    def testTyping(self):
        self.runDemo('Dialog and Message Boxes')
        focus.window('Dialogs')
        focus.widget(roleName='text')
        type("hello world")
        self.assertEquals(focus.widget.node.text, 'hello world')

if __name__ == "__main__":
    unittest.main()
