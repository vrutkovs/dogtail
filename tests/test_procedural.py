#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Unit tests for the dogtail.procedural API
"""
__author__ = "Zack Cerza <zcerza@redhat.com>"

from dogtail.procedural import focus, keyCombo, deselect, activate, select, click, tree, FocusError, run, config, type
from dogtail.rawinput import press, release, drag, doubleClick, relativeMotion, absoluteMotion, pressKey
from dogtail.tree import ActionNotSupported, NotSensitiveError
config.logDebugToFile = False
config.logDebugToStdOut = True
import pyatspi
from time import sleep
from gtkdemotest import GtkDemoTest, trap_stdout


class GtkDemoTest(GtkDemoTest):

    def setUp(self):
        self.pid = run('gtk3-demo')
        self.app = focus.application.node


class TestFocusApplication(GtkDemoTest):

    def test_focusing_bogus_name_without_fatal_error(self):
        config.fatalErrors = False
        output = trap_stdout(focus.application, "should not be found")
        self.assertTrue(
            'The requested widget could not be focused: "should not be found" application' in output)

    def test_throw_exception_on_focusing_bogus_name(self):
        config.fatalErrors = True
        self.assertRaises(FocusError, focus.application, "should not be found")

    def test_focusing_basic(self):
        focus.application.node = None
        focus.application("gtk3-demo")
        self.assertEquals(focus.application.node, self.app)

    def test_throw_exception_on_get_no_such_attribute(self):
        with self.assertRaises(AttributeError):
            focus.no_such_attribute

    def test_throw_exception_on_get_no_such_attribute_when_node_doesnt_exist(self):
        focus.application.node = None
        with self.assertRaises(AttributeError):
            focus.no_such_attribute

    def test_throw_exception_on_set_no_such_attribute(self):
        with self.assertRaises(AttributeError):
            focus.no_such_attribute = 0


class TestFocusWindow(GtkDemoTest):

    def test_focusing_bogus_name_without_a_fatal_error(self):
        config.fatalErrors = False
        output = trap_stdout(focus.window, "should not be found")
        self.assertEquals(focus.window.node, None)
        self.assertTrue(
            'The requested widget could not be focused: "should not be found" window' in output)

    def test_throw_exception_on_focusing_bogus_name(self):
        config.fatalErrors = True
        self.assertRaises(FocusError, focus.window, "should not be found")


class TestFocusDialog(GtkDemoTest):

    def test_focusing_bogus_name_without_a_fatal_error(self):
        config.fatalErrors = False
        output = trap_stdout(focus.dialog, "should not be found")
        self.assertEquals(focus.dialog.node, None)
        self.assertTrue(
            'The requested widget could not be focused: "should not be found" dialog' in output)

    def test_throw_exception_on_focusing_bogus_name(self):
        config.fatalErrors = True
        self.assertRaises(FocusError, focus.dialog, "should not be found")


class TestFocusWidget(GtkDemoTest):

    def test_focusing_empty_name(self):
        self.assertRaises(TypeError, focus.widget)

    def test_focusing_bogus_name_without_a_fatal_error(self):
        config.fatalErrors = False
        output = trap_stdout(focus.widget, "should not be found")
        self.assertEquals(focus.widget.node, None)
        self.assertTrue(
            'The requested widget could not be focused: child with name="should not be found"' in output)

    def test_throw_exception_on_focusing_bogus_name(self):
        config.fatalErrors = True
        self.assertRaises(FocusError, focus.widget, "should not be found")

    def test_focusing_basic(self):
        "Ensure that focus.widget('foo') finds a node with name 'foo'"
        focus.widget("Application window")
        self.assertEquals(focus.widget.name, "Application window")


class TestFocus(GtkDemoTest):

    def test_initial_state(self):
        self.assertEquals(focus.widget.node, None)
        self.assertEquals(focus.dialog.node, None)
        self.assertEquals(focus.window.node, None)

    def test_focusing_app(self):
        focus.app.node = None
        focus.app('gtk3-demo')
        self.assertEquals(focus.app.node, self.app)

    def test_focusing_app_via_application(self):
        focus.app.node = None
        focus.application('gtk3-demo')
        self.assertEquals(focus.app.node, self.app)

    def test_focus_getting_bogus_attribute(self):
        self.assertRaises(AttributeError, getattr, focus, 'nosuchtype')

    def test_focus_setting_bogus_attribute(self):
        self.assertRaises(
            AttributeError, setattr, focus, 'nosuchtype', 'nothing')

    def test_focusing_role_name(self):
        focus.widget(roleName='page tab')
        self.assert_(isinstance(focus.widget.node, tree.Node))
        self.assertEquals(focus.widget.node.role, pyatspi.ROLE_PAGE_TAB)

    def test_focus_menu(self):
        self.runDemo('Application window')
        focus.window('Application Window')
        focus.menu('File')
        self.assert_(isinstance(focus.widget.node, tree.Node))
        self.assertEquals(focus.widget.node.role, pyatspi.ROLE_MENU)

    def test_focus_menu_item(self):
        self.runDemo('Application window')
        focus.window('Application Window')
        click.menu('File')
        focus.menuItem('New')
        self.assert_(isinstance(focus.widget.node, tree.Node))
        self.assertEquals(focus.widget.node.role, pyatspi.ROLE_MENU_ITEM)

    def test_focus_button(self):
        self.runDemo('Application window')
        focus.window('Application Window')
        focus.button('Open')
        self.assert_(isinstance(focus.widget.node, tree.Node))
        self.assertEquals(focus.widget.node.role, pyatspi.ROLE_PUSH_BUTTON)

    def test_focus_table(self):
        self.runDemo('Builder')
        focus.window('GtkBuilder demo')
        focus.table('')
        self.assert_(isinstance(focus.widget.node, tree.Node))
        self.assertEquals(focus.widget.node.role, pyatspi.ROLE_TABLE)

    def test_focus_table_cell(self):
        self.runDemo('Builder')
        focus.window('GtkBuilder demo')
        focus.tableCell('')
        self.assert_(isinstance(focus.widget.node, tree.Node))
        self.assertEquals(focus.widget.node.role, pyatspi.ROLE_TABLE_CELL)

    def test_focus_text(self):
        self.runDemo('Application window')
        focus.window('Application Window')
        focus.text('')
        self.assert_(isinstance(focus.widget.node, tree.Node))
        self.assertEquals(focus.widget.node.role, pyatspi.ROLE_TEXT)

    def test_focus_icon(self):
        self.runDemo('Application window')
        focus.window('Application Window')
        focus.icon('')
        self.assert_(isinstance(focus.widget.node, tree.Node))
        self.assertEquals(focus.widget.node.role, pyatspi.ROLE_ICON)


class TestKeyCombo(GtkDemoTest):

    def test_keyCombo(self):
        self.runDemo('Application window')
        focus.window('Application Window')
        keyCombo("<ctrl>a")
        focus.dialog('About GTK+ Code Demos')

    def test_keyCombo_on_widget(self):
        self.runDemo('Application window')
        focus.window('Application Window')
        focus.icon('')
        keyCombo("<ctrl>a")
        focus.dialog('About GTK+ Code Demos')


class TestActions(GtkDemoTest):

    def test_click(self):
        click('Source')
        self.assertTrue(focus.widget.isSelected)

    def test_double_click(self):
        click('Source')
        self.assertTrue(focus.widget.isSelected)

    def test_click_on_invisible_element(self):
        with self.assertRaises(ValueError):
            click("Transparent")

    def test_click_with_raw(self):
        click('Source', raw=True)
        self.assertTrue(focus.widget.isSelected)

    def test_select(self):
        select('Source')
        self.assertTrue(focus.widget.isSelected)

    def test_deselect(self):
        type('Icon View')
        click('Icon View')
        type('+')
        sleep(0.5)
        self.runDemo('Icon View Basics')
        focus.window('GtkIconView demo')

        focus.widget(roleName='icon')
        select()
        deselect()
        self.assertFalse(focus.widget.isSelected)

    def test_typing_on_widget(self):
        self.runDemo('Dialog and Message Boxes')
        focus.window('Dialogs')
        focus.widget(roleName='text')
        type("hello world")
        from time import sleep
        sleep(0.1)
        self.assertEquals(focus.widget.node.text, 'hello world')

    def test_custom_actions(self):
        activate("CSS Theming")
        self.assertEquals(focus.widget.node.text, 'CSS Theming')

    def test_blink_on_actions(self):
        config.blinkOnActions = True
        activate("CSS Theming")
        self.assertEquals(focus.widget.node.text, 'CSS Theming')

    def test_custom_actions_button(self):
        self.runDemo('Dialog and Message Boxes')
        focus.window('Dialogs')
        click.button('Interactive Dialog')
        self.assertTrue(focus.dialog("Interactive Dialog"))

    def test_custom_actions_menu(self):
        self.runDemo('Application window')
        focus.window('Application Window')
        click.menu('File')
        click.menuItem('New')
        self.assert_(isinstance(focus.widget.node, tree.Node))
        self.assertEquals(focus.widget.node.role, pyatspi.ROLE_MENU_ITEM)

    def test_custom_actions_text(self):
        self.runDemo('Builder')
        focus.window('GtkBuilder demo')
        click.text('')
        self.assert_(isinstance(focus.widget.node, tree.Node))
        self.assertEquals(focus.widget.node.role, pyatspi.ROLE_TEXT)

    def test_custom_actions_text_with_debug(self):
        self.runDemo('Builder')
        focus.window('GtkBuilder demo')
        config.debugSearching = True
        output = trap_stdout(click.text, '')
        self.assertIn(
            u"searching for descendent of [frame | GtkBuilder demo]: child with roleName='text'",
            output)

        self.assert_(isinstance(focus.widget.node, tree.Node))
        self.assertEquals(focus.widget.node.role, pyatspi.ROLE_TEXT)

    def test_custom_actions_table_cell(self):
        activate.tableCell("CSS Theming")
        self.assert_(isinstance(focus.widget.node, tree.Node))
        self.assertEquals(focus.widget.node.role, pyatspi.ROLE_TABLE_CELL)

    def test_throws_action_not_supported(self):
        self.runDemo('Builder')
        focus.window('GtkBuilder demo')
        with self.assertRaises(ActionNotSupported) as cm:
            activate.text('')
        self.assertEquals(str(cm.exception), "Cannot do 'activate' action on [text | ]")

    def test_action_description(self):
        widget = focus.application.node.child('Application class')
        edit_action = widget.actions['edit']
        self.assertEquals(edit_action.name, 'edit')
        self.assertEquals(
            edit_action.description,
            'Creates a widget in which the contents of the cell can be edited')
        self.assertEquals(edit_action.keyBinding, '')
        self.assertEquals(str(edit_action), '[action | edit |  ]')

    def test_action_on_insensitive(self):
        self.runDemo("Assistant")
        wnd = focus.application.node.window("Sample assistant (1 of 4)")
        child = wnd.child("Continue")
        config.ensureSensitivity = True
        with self.assertRaises(NotSensitiveError):
            child.actions['click'].do()
        config.ensureSensitivity = False
        output = trap_stdout(child.actions['click'].do)
        self.assertEquals(
            output,
            u"""click on [push button | Continue]
Warning: Cannot click [push button | Continue]. It is not sensitive.""")


class TestRawInput(GtkDemoTest):
    def test_motion(self):
        absoluteMotion(0, 0)
        absoluteMotion(0, 0, mouseDelay=1)
        absoluteMotion(-100, -100, check=False)
        absoluteMotion(0, 0, mouseDelay=1, check=False)
        relativeMotion(-100, -100)
        absoluteMotion(0, 0)
        relativeMotion(-100, -100, mouseDelay=1)

    def test_doubleClick(self):
        btn = focus.application.node.child('Builder')
        doubleClick(btn.position[0], btn.position[1])
        focus.window('GtkBuilder demo')

    def test_press(self):
        self.runDemo('Builder')
        focus.window('GtkBuilder demo')
        btn = focus.window.node.button('New')
        press(btn.position[0], btn.position[1])
        self.assertIn(pyatspi.STATE_ARMED, btn.getState().getStates())
        release(btn.position[0], btn.position[1])
        self.assertNotIn(pyatspi.STATE_ARMED, btn.getState().getStates())

    def test_drag(self):
        self.runDemo('Tool Palette')
        focus.window('Tool Palette')
        src_position = focus.window.node.child("gtk-caps-lock-warning").position
        dst_position = focus.window.node.child("Passive DnD Mode").position
        dst_position = (dst_position[0] + 50, dst_position[1] + 50)
        drag(src_position, dst_position)

    def test_pressKey_no_such_key(self):
        with self.assertRaises(KeyError):
            pressKey("no such key")
