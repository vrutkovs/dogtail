#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for the dogtail.Node class

Notes on pyunit (the "unittest" module):

Test classes are written as subclass of unittest.TestCase.
A test is a method of such a class, beginning with the string "test"

unittest.main() will run all such methods.  Use "-v" to get feedback on which tests are being run.  Tests are run in alphabetical order; all failure reports are gathered at the end.

setUp and tearDown are "magic" methods, called before and after each such
test method is run.
"""
__author__ = "Dave Malcolm <dmalcolm@redhat.com>"

import unittest
import dogtail.tree
import dogtail.predicate
import dogtail.config
import dogtail.utils
import pyatspi
from gtkdemotest import GtkDemoTest, trap_stdout


class TestNodeAttributes(GtkDemoTest):

    """
    Unit tests for the the various synthesized attributes of a Node
    """

    def test_get_bogus(self):
        self.assertRaises(
            AttributeError, getattr, self.app, "thisIsNotAnAttribute")

    # 'name' (read-only string):
    def test_get_name(self):
        self.assertEquals(self.app.name, 'gtk3-demo')
        self.assertEquals(dogtail.tree.root.name, 'main')

    def test_set_name(self):
        self.assertRaises(
            AttributeError, self.app.__setattr__, "name", "hello world")

    def test_get_debugName(self):
        self.assertEquals(self.app.debugName, '"gtk3-demo" application')
        self.assertEquals(dogtail.tree.root.debugName, 'root')

    def test_set_debugName(self):
        self.app.debugName = "my application"
        self.assertEquals(self.app.debugName, 'my application')

        dogtail.tree.root.debugName = "my root"
        self.assertEquals(dogtail.tree.root.debugName, 'my root')

    # 'roleName' (read-only string):
    def test_get_roleName(self):
        self.assertEquals(self.app.roleName, 'application')

    def test_set_roleName(self):
        self.assertRaises(
            AttributeError, self.app.__setattr__, "roleName", "hello world")

    # 'role' (read-only atspi role enum):
    def test_get_role(self):
        self.assertEquals(self.app.role, dogtail.tree.pyatspi.ROLE_APPLICATION)

    def test_set_role(self):
        # FIXME should be AttributeError?
        self.assertRaises(
            RuntimeError, self.app.__setattr__, "role", pyatspi.Atspi.Role(1))

    # 'description' (read-only string):
    def test_get_description(self):
        # FIXME: can we get a more interesting test case here?
        self.assertEquals(self.app.description, "")

    def test_set_description(self):
        self.assertRaises(
            AttributeError, self.app.__setattr__, "description", "hello world")

    # 'parent' (read-only Node instance):
    def test_get_parent(self):
        # the app has a parent if gnome-shell is used, so parent.parent is a
        # safe choice
        if filter(lambda x: x.name == 'gnome-shell', self.app.applications()):
            self.assertEquals(self.app.parent.parent, None)
        self.assertEquals(self.app.children[0].parent, self.app)

    def test_set_parent(self):
        self.assertRaises(
            AttributeError, self.app.__setattr__, "parent", None)

    # 'children' (read-only list of Node instances):
    def test_get_children(self):
        kids = self.app.children
        self.assertEquals(len(kids), 1)
        self.assertEquals(kids[0].name, "GTK+ Code Demos")
        self.assertEquals(kids[0].roleName, "frame")

    def test_set_children(self):
        self.assertRaises(
            AttributeError, self.app.__setattr__, "children", [])

    def test_get_children_with_limit(self):
        haveWarnedAboutChildrenLimit = False
        print(haveWarnedAboutChildrenLimit)  # make pyflakes happy about it
        dogtail.config.config.childrenLimit = 1
        widget = self.app.child(roleName='tree table')
        self.assertEquals(len(widget.children), 1)

    #  combovalue (string):
    def test_get_combo_value(self):
        self.runDemo('Combo boxes')
        wnd = self.app.window('Combo boxes')
        combo = wnd.child(roleName='combo box')
        self.assertEquals(combo.combovalue, 'Warning')

    def test_get_URI_not_implemented(self):
        with self.assertRaises(NotImplementedError):
            self.app.URI

    # 'text' (string):
    def test_set_text(self):
        self.runDemo('Dialog and Message Boxes')
        wnd = self.app.window('Dialogs')
        wnd.button('Interactive Dialog').click()
        dlg = self.app.dialog('Interactive Dialog')
        entry1 = dlg.child(label='Entry 1')
        entry2 = dlg.child(roleName='text')

        # Try reading the entries:
        self.assertEquals(entry1.text, "")
        self.assertEquals(entry2.text, "")

        # Set them...
        entry1.text = "hello"
        entry2.text = "world"

        # Ensure that they got set:
        self.assertEquals(entry1.text, "hello")
        self.assertEquals(entry2.text, "world")

        # and try again, searching for them again, to ensure it actually
        # affected the UI:
        self.assertEquals(dlg.child(label='Entry 1').text, "hello")
        self.assertEquals(dlg.child(label='Entry 2').text, "world")

        # Ensure app.text is None
        self.assertEquals(self.app.text, None)

        # Ensure a label's text is read-only as expected:
        # FIXME: this doesn't work; the label has no 'text'; it has a name.  we wan't a readonly text entry
        # label = dlg.child('Entry 1')
        # self.assertRaises(dogtail.tree.ReadOnlyError, label.text.__setattr__, "text", "hello world")

        # FIXME: should we assert that things are logged and delays are added?
        # FIXME: should have a test case involving the complex GtkTextView
        # widget

    def test_caretOffset(self):
        self.runDemo('Dialog and Message Boxes')
        wnd = self.app.window('Dialogs')
        entry1 = wnd.child(label='Entry 1')
        entry2 = wnd.child(roleName='text')

        # Try reading the entries:
        self.assertEquals(entry1.text, '')
        self.assertEquals(entry2.text, '')

        # Set them...
        s1 = "I just need a sentence"
        s2 = "And maybe a second one to be sure"
        entry1.text = s1
        entry2.text = s2

        # Make sure the caret offset is zero
        self.assertEquals(entry1.caretOffset, 0)
        self.assertEquals(entry2.caretOffset, 0)

        # Set the caret offset to something ridiculous
        entry1.caretOffset = len(s1 * 3)
        entry2.caretOffset = len(s2 * 3)

        # Make sure the caret offset only goes as far as the end of the string
        self.assertEquals(entry1.caretOffset, len(s1))
        self.assertEquals(entry2.caretOffset, len(s2))

        def splitByOffsets(node, string):
            # Verify the equality of node.text and string, word by word.
            # I realize this doesn't really test dogtail itself, but that could
            #   change in the future and I don't want to throw the code away.
            textIface = node.queryText()
            endOffset = -1  # We only set this now so the loop looks nicer
            startOffset = 0
            while startOffset != len(string):
                (text, startOffset, endOffset) = textIface.getTextAtOffset(
                    startOffset, pyatspi.TEXT_BOUNDARY_WORD_START)
                self.assertEquals(startOffset,
                                  string.find(text, startOffset, endOffset))
                startOffset = endOffset

        splitByOffsets(entry1, s1)
        splitByOffsets(entry2, s2)

    # 'combovalue' (read/write string):
    def test_comboValue(self):
        self.runDemo('Combo boxes')
        wnd = self.app.window('Combo boxes')
        combo1 = wnd.child('Some stock icons').child(roleName='combo box')
        combo1.combovalue = 'Clear'
        self.assertEquals(combo1.combovalue, 'Clear')

    # 'stateSet' (read-only StateSet instance):
    def test_getStateSet(self):
        self.assert_(not self.app.sensitive)

    def test_setStateSet(self):
        """Node.stateSet should be read-only"""
        # FIXME should be AttributeError?
        self.assertRaises(
            RuntimeError, self.app.__setattr__, "states", pyatspi.StateSet())

    # 'relations' (read-only list of atspi.Relation instances):
    def test_getRelations(self):
        # FIXME once relations are used for something other than labels
        pass

    # 'labelee' (read-only list of Node instances):
    def test_get_labelee(self):
        self.runDemo('Dialog and Message Boxes')
        wnd = self.app.window('Dialogs')
        label = wnd.child(roleName='label', name='Entry 1')
        self.assertEquals(label.labelee.roleName, 'text')
        self.assertEquals(label.labellee.roleName, 'text')

    def test_set_labelee(self):
        self.assertRaises(
            AttributeError, self.app.__setattr__, "labellee", None)

    # 'labeler' (read-only list of Node instances):
    def test_get_labeler(self):
        self.runDemo('Dialog and Message Boxes')
        wnd = self.app.window('Dialogs')
        text = wnd.findChildren(dogtail.predicate.GenericPredicate(roleName='text'))[1]
        self.assertEquals(text.labeler.name, 'Entry 1')
        self.assertEquals(text.labeller.name, 'Entry 1')

    def test_set_labeller(self):
        self.assertRaises(
            AttributeError, self.app.__setattr__, "labeller", None)

    # 'sensitive' (read-only boolean):
    def test_get_sensitive(self):
        self.assert_(not self.app.sensitive)
        self.assert_(self.app.children[0].sensitive)

    def test_set_sensitive(self):
        self.assertRaises(
            AttributeError, self.app.__setattr__, "sensitive", True)

    # 'showing' (read-only boolean):
    def test_get_showing(self):
        self.assert_(not self.app.showing)
        self.assert_(self.app.children[0].showing)

    def test_set_showing(self):
        self.assertRaises(
            AttributeError, self.app.__setattr__, "showing", True)

    # 'actions' (read-only list of Action instances):
    def test_get_actions(self):
        self.assertEquals(len(self.app.actions), 0)

    def test_set_actions(self):
        self.assertRaises(AttributeError, self.app.__setattr__, "actions", {})

    # 'extents' (readonly tuple):
    def test_get_extents(self):
        (x, y, w, h) = self.app.children[0].extents
        self.assert_(w > 0)
        self.assert_(h > 0)

    def test_set_extents(self):
        self.assertRaises(
            AttributeError, self.app.__setattr__, "extents", (0, 0, 640, 480))

    # 'position' (readonly tuple):
    def test_get_position(self):
        (x, y) = self.app.children[0].position

    def test_set_position(self):
        self.assertRaises(
            AttributeError, self.app.__setattr__, "position", (0, 0))

    # 'size' (readonly tuple):
    def test_get_size(self):
        (w, h) = self.app.children[0].size
        self.assert_(w > 0)
        self.assert_(h > 0)

    def test_set_size(self):
        self.assertRaises(
            AttributeError, self.app.__setattr__, "size", (640, 480))

    # 'toolkitName' (readonly string):
    def test_get_toolkit(self):
        self.assertEquals(self.app.toolkitName, "gtk")

    def test_set_toolkit(self):
        self.assertRaises(
            AttributeError, self.app.__setattr__, "toolkitName", "gtk")

    # 'ID'
    def test_get_ID(self):
        self.assertEquals(type(self.app.id), type(42))

    def test_set_ID(self):
        self.assertRaises(AttributeError, setattr, self.app, "id", 42)

    def test_checked(self):
        self.runDemo("Application window")
        wnd = self.app.window("Application Window")
        wnd.menu("Preferences").click()
        mnuItem = wnd.menu("Preferences").menuItem("Bold")
        self.assertTrue(mnuItem.checked)
        self.assertTrue(mnuItem.isChecked)

    def test_dead(self):
        self.runDemo('Application window')
        wnd = self.app.window('Application Window')
        self.assertFalse(wnd.dead)
        import os
        import signal
        os.kill(self.pid, signal.SIGKILL)
        dogtail.utils.doDelay(5)
        self.assertTrue(wnd.dead)

    # https://bugzilla.gnome.org/show_bug.cgi?id=710730
    # GError: Method "Contains" with signature "iin" on interface "org.a11y.atspi.Component" doesn't exist
    # def test_contains(self):
    #     child = self.app.children[0]
    #     position = child.position
    #     self.assertTrue(child.contains(position[0]+1, position[1]+1))

    # https://bugzilla.gnome.org/show_bug.cgi?id=710730
    # returns None as contains is broken
    # def test_childAtPoint(self):
    #     child = self.app.children[0]
    #     position = child.position
    #     actual_child = self.app.getChildAtPoint(position[0], position[1])
    #     self.assertEquals(actual_child, child)

    def test_click(self):
        self.runDemo('Dialog and Message Boxes')
        wnd = self.app.window('Dialogs')
        wnd.button('Interactive Dialog').click()
        self.assertTrue(self.app.dialog("Interactive Dialog").showing)

    def test_doubleClick(self):
        builder = self.app.child("Builder")
        builder.doubleClick()
        self.assertTrue(self.app.window("GtkBuilder demo").showing)

    def test_point(self):
        self.runDemo("Application window")
        wnd = self.app.window("Application Window")
        wnd.menu("Preferences").click()
        color = wnd.menu("Preferences").menu("Color")
        red = wnd.menu("Preferences").menu("Color").menuItem("Red")
        self.assertFalse(red.showing)
        color.point()
        self.assertTrue(red.showing)


class TestSelection(GtkDemoTest):

    def test_tabs(self):
        # Use the Info/Source tabs of gtk-demo:
        info = self.app.child('Info')
        source = self.app.child('Source')

        # Check initial state:
        self.assert_(info.isSelected)
        self.assert_(not source.isSelected)

        # Select other tab:
        source.select()

        # Check new state:
        self.assert_(not info.isSelected, False)
        self.assert_(source.isSelected)

    def test_iconView(self):
        self.app.child(roleName='tree table').typeText("Icon View")
        self.app.child(roleName='tree table').child("Icon View").click()
        self.app.child(roleName='tree table').child("Icon View").typeText("+")
        self.runDemo('Icon View Basics')
        wnd = self.app.window('GtkIconView demo')

        pane = wnd.child(roleName="layered pane")
        icons = pane.children

        pane.selectAll()
        self.assertNotIn(False, [x.selected for x in icons])
        # Crashes here
        #pane.deselectAll()
        #self.assertNotIn(True, [x.selected for x in icons])
        pane.select_all()
        self.assertNotIn(False, [x.selected for x in icons])
        #pane.deselect_child(0)
        #self.assertTrue(icons[0].selected)
        #self.assertNotIn(False, [x.selected for x in icons[1:]])
        pane.select_child(0)
        self.assertTrue(icons[0].selected)
        self.assertNotIn(False, [x.selected for x in icons])


class TestValue(GtkDemoTest):

    def test_get_value(self):
        "The scrollbar starts out at position zero."
        sb = self.app.child(roleName='scroll bar')
        self.assertEquals(sb.value, 0)

    def test_set_value(self):
        sb = self.app.findChildren(dogtail.predicate.GenericPredicate(roleName='scroll bar'))[1]
        sb.value = 100
        self.assertEquals(sb.value, 100)

    def test_min_value(self):
        sb = self.app.findChildren(dogtail.predicate.GenericPredicate(roleName='scroll bar'))[1]
        self.assertEquals(sb.minValue, 0)

    def test_max_value(self):
        sb = self.app.findChildren(dogtail.predicate.GenericPredicate(roleName='scroll bar'))[1]
        self.assert_(sb.maxValue > 250)

    def test_min_value_increment(self):
        sb = self.app.findChildren(dogtail.predicate.GenericPredicate(roleName='scroll bar'))[1]
        self.assertEquals(sb.minValueIncrement, sb.minValueIncrement)


class TestSearching(GtkDemoTest):

    def test_findChildren(self):
        pred = dogtail.predicate.GenericPredicate(roleName='table cell')
        tableCells = self.app.findChildren(pred)

        def get_table_cells_recursively(node):
            counter = 0
            for child in node.children:
                if child.roleName == 'table cell':
                    counter += 1
                counter += get_table_cells_recursively(child)
            return counter

        counter = get_table_cells_recursively(self.app)
        self.assertEquals(len(tableCells), counter)

    def test_findChildren2(self):
        pred = dogtail.predicate.GenericPredicate(roleName='page tab list')
        pageTabLists = self.app.findChildren(pred)
        pred = dogtail.predicate.GenericPredicate(roleName='page tab')
        # The second page tab list is the one with the 'Info' and 'Source' tabs
        pageTabs = pageTabLists[1].findChildren(pred)
        self.assertEquals(len(pageTabs), 6)

    def test_findAncestor(self):
        pred = dogtail.predicate.GenericPredicate(roleName='tree table')
        child = self.app.child("Builder")
        parent = child.findAncestor(pred)
        self.assertIn(child, parent.children)
        pred = dogtail.predicate.GenericPredicate(roleName='frame')
        parent = child.findAncestor(pred)
        self.assertIn(parent, self.app.children)
        # No ancestor found
        self.assertIsNone(parent.findAncestor(pred))

    def test_isChild(self):
        parent = self.app.child(roleName='tree table')
        self.assertTrue(parent.isChild("Builder"))

    def test_getUserVisibleStrings(self):
        child = self.app.child("Builder")
        self.assertEquals(child.getUserVisibleStrings(), ['Builder'])

    def test_satisfies(self):
        pred = dogtail.predicate.GenericPredicate(roleName='table cell')
        builder = self.app.child("Builder")
        self.assertTrue(builder.satisfies(pred))

    def test_absoluteSearchPath(self):
        self.assertEquals(
            str(self.app.getAbsoluteSearchPath()),
            '{/("gtk3-demo" application,False)}')
        builder = self.app.child("Builder")
        self.assertEquals(
            str(builder.getAbsoluteSearchPath()),
            '{/("gtk3-demo" application,False)/("GTK+ Code Demos" window,False)/(child with name="Widget (double click for demo)" roleName=\'page tab\',True)/(child with name="Builder" roleName=\'table cell\',True)}')

    def test_compare_equal_search_paths(self):
        builder = self.app.child("Builder")
        builder_sp = builder.getAbsoluteSearchPath()
        self.assertTrue(builder_sp == builder_sp)

    def test_compare_unequal_search_paths_different_length(self):
        builder = self.app.child("Builder")
        builder_sp = builder.getAbsoluteSearchPath()
        app_sp = self.app.getAbsoluteSearchPath()
        self.assertFalse(builder_sp == app_sp)

    def test_compare_unequal_search_paths_same_length(self):
        builder = self.app.child("Builder")
        assistant = self.app.child("Assistant")
        builder_sp = builder.getAbsoluteSearchPath()
        assistant_sp = assistant.getAbsoluteSearchPath()
        self.assertFalse(builder_sp == assistant_sp)

    def test_get_search_path_length(self):
        builder = self.app.child("Builder")
        builder_sp = builder.getAbsoluteSearchPath()
        self.assertEquals(builder_sp.length(), 4)

    def test_iterate_search_path(self):
        builder = self.app.child("Builder")
        builder_sp = builder.getAbsoluteSearchPath()
        self.assertEquals(
            [x[0].makeScriptVariableName() for x in builder_sp],
            ['gtk3DemoApp', 'gtkCodeDemosWin', 'widgetDoubleClickForDemoNode', 'builderNode'])

    def test_make_script_method_call_from_search_path(self):
        builder = self.app.child("Builder")
        builder_sp = builder.getAbsoluteSearchPath()
        # FIXME: dot in the beginning
        self.assertEquals(
            builder_sp.makeScriptMethodCall(),
            u'.application("gtk3-demo").window("GTK+ Code Demos").child( name="Widget (double click for demo)" roleName=\'page tab\').child( name="Builder" roleName=\'table cell\')')

    def test_get_relative_search_path_for_path(self):
        builder = self.app.child("Builder")
        builder_sp = builder.getAbsoluteSearchPath()
        frame_sp = self.app.window("GTK+ Code Demos").getAbsoluteSearchPath()
        # FIXME: Should be "child( name="Widget (double click for demo)" roleName=\'page tab\').child( name="Builder" roleName=\'table cell\')"
        self.assertIsNone(builder_sp.getRelativePath(frame_sp))

    def test_get_prefix_for_search_path(self):
        builder = self.app.child("Builder")
        builder_sp = builder.getAbsoluteSearchPath()
        self.assertEquals(
            str(builder_sp.getPrefix(1)),
            '{/("gtk3-demo" application,False)}')

    def test_get_predicate(self):
        builder = self.app.child("Builder")
        builder_sp = builder.getAbsoluteSearchPath()
        pred = builder_sp.getPredicate(0)
        self.assertEqual(type(pred), dogtail.predicate.IsAnApplicationNamed)
        self.assertEqual(str(pred.appName), '"gtk3-demo"')

    def test_getRelativeSearch_app(self):
        relpath = self.app.getRelativeSearch()
        self.assertEquals(str(relpath[0]), '[desktop frame | main]')
        self.assertEquals(relpath[1].name.untranslatedString, u'gtk3-demo')
        self.assertFalse(relpath[2])

    def test_getRelativeSearch_widget(self):
        builder = self.app.child("Builder")
        relpath = builder.getRelativeSearch()
        self.assertEquals(str(relpath[0]), '[page tab | Widget (double click for demo)]')
        self.assertEquals(relpath[1].describeSearchResult(), u'child with name="Builder" roleName=\'table cell\'')
        self.assertTrue(relpath[2])

    def testFindChildrenNonRecursive(self):
        self.app.child(roleName='tree table').typeText("Tree View")
        self.app.child(roleName='tree table').child("Tree View").click()
        self.app.child(roleName='tree table').child("Tree View").typeText("+")
        self.runDemo('Tree Store')
        wnd = self.app.window('Card planning sheet')
        table = wnd.child(roleName='tree table')
        pred = dogtail.predicate.GenericPredicate(roleName='table cell')
        dogtail.config.config.childrenLimit = 10000
        cells = table.findChildren(pred, recursive=False)
        direct_cells = filter(lambda cell: cell.roleName == 'table cell', table.children)
        self.assertEquals(len(cells), len(direct_cells))

    def test_find_by_shortcut(self):
        self.runDemo("Application window")
        wnd = self.app.window("Application Window")
        self.assertIsNotNone(wnd.menu("File"))
        self.assertIsNotNone(wnd.menu("File").menuItem("New"))
        self.assertIsNotNone(wnd.textentry(""))
        self.assertIsNotNone(wnd.childNamed("File"))
        self.assertIsNotNone(self.app.tab("Info"))

    def test_find_by_shortcut2(self):
        self.runDemo('Dialog and Message Boxes')
        wnd = self.app.window('Dialogs')
        self.assertIsNotNone(wnd.childLabelled("Entry 1"))
        self.assertIsNotNone(wnd.button("Message Dialog"))

# Crashes: TypeError: object.__init__() takes no parameters
#class TestWizard(GtkDemoTest):
#    def test_wizard(self):
#        self.runDemo("Assistant")
#        wnd = self.app.window("Sample assistant (1 of 4)")
#        wizard = dogtail.tree.Wizard(wnd)

# Fails to find
#class TestLinks(GtkDemoTest):
#    def test_link_anchor(self):
#        self.runDemo("Links")
#        wnd = self.app.window("Links")


class TestActions(GtkDemoTest):
    # FIXME: should test the various actions
    pass


# class TestExceptions(GtkDemoTest):

#     def test_exception(self):
#         # Kill the gtk-demo prematurely:
#         import os
#         import signal
#         os.kill(self.pid, signal.SIGKILL)
#         dogtail.utils.doDelay(5)

#         from gi.repository import GLib
#         # Ensure that we get an exception when we try to work further with it:
#         self.assertRaises(GLib.GError, self.app.dump)


class TestConfiguration(unittest.TestCase):

    def test_get_set_all_properties(self):
        for option in dogtail.config.config.defaults.keys():
            print("Setting config.%s property" % option)
            value = ''
            if 'Dir' in option:
                value = '/tmp/dogtail/'  # Special value for dir-related properties
            dogtail.config.config.__setattr__(option, value)
            self.assertEquals(dogtail.config.config.__getattr__(option), value)

    def test_default_directories_created(self):
        import os.path
        self.assertEquals(
            os.path.isdir(dogtail.config.config.scratchDir), True)
        self.assertEquals(os.path.isdir(dogtail.config.config.logDir), True)
        self.assertEquals(os.path.isdir(dogtail.config.config.dataDir), True)

    def test_set(self):
        self.assertRaises(
            AttributeError, setattr, dogtail.config.config, 'nosuchoption', 42)

    def test_get(self):
        self.assertRaises(
            AttributeError, getattr, dogtail.config.config, 'nosuchoption')

    def helper_create_directory_and_set_option(self, path, property_name):
        import os.path
        if os.path.isdir(path):
            import shutil
            shutil.rmtree(path)
        dogtail.config.config.__setattr__(property_name, path)
        self.assertEquals(os.path.isdir(path), True)

    def test_create_scratch_directory(self):
        new_folder = "/tmp/dt"
        self.helper_create_directory_and_set_option(new_folder, 'scratchDir')

    def test_create_data_directory(self):
        new_folder = "/tmp/dt_data"
        self.helper_create_directory_and_set_option(new_folder, 'dataDir')

    def test_create_log_directory(self):
        new_folder = "/tmp/dt_log"
        self.helper_create_directory_and_set_option(new_folder, 'logDir')

    def test_load(self):
        dogtail.config.config.load({'actionDelay': 2.0})
        self.assertEquals(dogtail.config.config.actionDelay, 2.0)

    def test_reset(self):
        default_actionDelay = dogtail.config.config.defaults['actionDelay']
        dogtail.config.config.actionDelay = 2.0
        dogtail.config.config.reset()
        self.assertEquals(
            dogtail.config.config.actionDelay, default_actionDelay)


class TestDump(GtkDemoTest):

    def test_dump_to_stdout(self):
        child = self.app.child('Source')
        output = trap_stdout(child.dump)
        self.assertEquals(
            output,
            """[page tab | Source]
 [scroll pane | ]
  [text | ]
  [scroll bar | ]
  [scroll bar | ]""")

    def test_dump_with_actions(self):
        child = self.app.child('Builder')
        output = trap_stdout(child.dump)
        self.assertEquals(
            output,
            """[table cell | Builder]
 [action | edit |  ]
 [action | expand or contract |  ]
 [action | activate |  ]""")

#    def test_dump_to_file(self):
#        import os
#        filepath = "/tmp/testfile"
#        child = self.app.child('Builder')
#        child.dump(fileName=filepath)
#        try:
#            with open(filepath, 'r') as content_file:
#                content = content_file.read()
#                self.assertEquals(
#                    content,
#                    """[table cell | Builder]
# [action | edit |  ]
# [action | expand or contract |  ]
# [action | activate |  ]""")
#        finally:
#            os.remove(filepath)
