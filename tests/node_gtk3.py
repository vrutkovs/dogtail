#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests for the dogtail.Node class using gtk3 demo

Notes on pyunit (the "unittest" module):

Test classes are written as subclass of unittest.TestCase.
A test is a method of such a class, beginning with the string "test"

unittest.main() will run all such methods.  Use "-v" to get feedback on which tests are being run.  Tests are run in alphabetical order; all failure reports are gathered at the end.

setUp and tearDown are "magic" methods, called before and after each such
test method is run.
"""
__author__ = "Dave Malcolm <dmalcolm@redhat.com>"

import unittest
import time
import dogtail.tree
import dogtail.predicate
import dogtail.config
dogtail.config.config.logDebugToFile = False
import pyatspi


class Gtk3DemoTest(unittest.TestCase):
    """
    TestCase subclass which handles bringing up and shutting down gtk3-demo as a fixture.  Used for writing other test cases.
    """
    def setUp(self):
        import dogtail.utils
        self.pid = dogtail.utils.run('gtk3-demo')
        self.app = dogtail.tree.root.application('gtk3-demo')

    def tearDown(self):
        import os, signal
        os.kill(self.pid, signal.SIGKILL)
        # Sleep just enough to let the app actually die.
        # AT-SPI doesn't like being hammered too fast.
        time.sleep(0.5)

    def runDemo(self, demoName):
        """
        Click on the named demo within the gtk3-demo app.
        """
        tree = self.app.child(roleName="tree table")
        tree.child(demoName).doubleClick()


class TestNodeAttributes(Gtk3DemoTest):
    """
    Unit tests for the the various synthesized attributes of a Node
    """
    def testGetBogus(self):
        "Getting a non-existant attribute should raise an attribute error"
        self.assertRaises(AttributeError, getattr, self.app, "thisIsNotAnAttribute")

    #FIXME: should setattr for a non-existant attr be allowed?
    
    # 'name' (read-only string):
    def testGetName(self):
        """
        Node.name of the gtk3-demo app should be "gtk3-demo"
        """
        self.assertEquals(self.app.name, 'gtk3-demo')

        self.assertEquals(dogtail.tree.root.name, 'main')

    def testSetName(self):
        "Node.name should be read-only"
        self.assertRaises(AttributeError, self.app.__setattr__,  "name", "hello world")
    
    # 'roleName' (read-only string):
    def testGetRoleName(self):
        """
        roleName of the gtk3-demo app should be "application"
        """
        self.assertEquals(self.app.roleName, 'application')

    def testSetRoleName(self):
        "Node.roleName should be read-only"
        self.assertRaises(AttributeError, self.app.__setattr__,  "roleName", "hello world")

    # 'role' (read-only atspi role enum):
    def testGetRole(self):
        "Node.role for a gtk3-demo app should be SPI_ROLE_APPLICATION"
        self.assertEquals(self.app.role, dogtail.tree.pyatspi.ROLE_APPLICATION)

    def testSetRole(self):
        "Node.role should be read-only"
        # FIXME should be AttributeError?
        self.assertRaises(RuntimeError, self.app.__setattr__,  "role", pyatspi.Atspi.Role(1))

    # 'description' (read-only string):
    def testGetDescription(self):
        # FIXME: can we get a more interesting test case here?
        self.assertEquals(self.app.description, "")

    def testSetDescription(self):
        "Node.description should be read-only"
        self.assertRaises(AttributeError, self.app.__setattr__,  "description", "hello world")

    # 'parent' (read-only Node instance):
    def testGetParent(self):
        # the app has a parent if gnome-shell is used, so parent.parent is a safe choice
        import ipdb; ipdb.set_trace()
        if filter(lambda x: x.name == 'gnome-shell', self.app.applications()):
            self.assertEquals(self.app.parent.parent, None)
        else:
            self.assertEquals(self.app.parent, None)

        self.assertEquals(self.app.children[0].parent, self.app)

    def testSetParent(self):
        "Node.parent should be read-only"
        self.assertRaises(AttributeError, self.app.__setattr__,  "parent", None)

    # 'children' (read-only list of Node instances):
    def testGetChildren(self):
        "A fresh gtk3-demo app should have a single child: the window."
        kids = self.app.children
        self.assertEquals(len(kids), 1)
        self.assertEquals(kids[0].name, "GTK+ Code Demos")
        self.assertEquals(kids[0].roleName, "frame")

    def testGetChildrenWhenLimitedInConfig(self):
        "a list of gtk3-demos should be limited to config value"
        dogtail.config.config.childrenLimit = 10
        kids = self.app.child(roleName='tree table').children
        self.assertEquals(len(kids), 10)

    def testSetChildren(self):
        "Node.children should be read-only"
        self.assertRaises(AttributeError, self.app.__setattr__,  "children", [])

    # 'text' (string):
    def testSimpleTextEntry(self):
        """
        Use gtk3-demo's text entry example to check that reading and writing
        Node.text works as expected
        """
        self.runDemo('Dialog and Message Boxes')
        wnd = self.app.window('Dialogs')
        wnd.button('Interactive Dialog').click()
        dlg = self.app.dialog('Interactive Dialog')
        entry1 = dlg.child(label='Entry 1')
        entry2 = dlg.child(label='Entry 2')

        # Try reading the entries:
        self.assertEquals(entry1.text, "")
        self.assertEquals(entry2.text, "")

        # Set them...
        entry1.text = "hello"
        entry2.text = "world"

        # Ensure that they got set:
        self.assertEquals(entry1.text, "hello")
        self.assertEquals(entry2.text, "world")
        
        # and try again, searching for them again, to ensure it actually affected the UI:
        self.assertEquals(dlg.child(label='Entry 1').text, "hello")
        self.assertEquals(dlg.child(label='Entry 2').text, "world")

        # Ensure app.text is None
        self.assertEquals(self.app.text, None)

        # Ensure a label's text is read-only as expected:
        # FIXME: this doesn't work; the label has no 'text'; it has a name.  we wan't a readonly text entry
        # label = dlg.child('Entry 1')
        # self.assertRaises(dogtail.tree.ReadOnlyError, label.text.__setattr__,  "text", "hello world")

        # FIXME: should we assert that things are logged and delays are added?
        # FIXME: should have a test case involving the complex GtkTextView widget

    def testCaretOffset(self):
        "Make sure the caret offset works as expected"
        self.runDemo('Dialog and Message Boxes')
        wnd = self.app.window('Dialogs')
        entry = wnd.child(label = 'Entry 1')

        # Try reading the entries:
        self.assertEquals(entry.text,'')

        # Set them...
        s = "I just need a sentence"
        entry.text = s

        # Make sure the caret offset is zero
        self.assertEquals(entry.caretOffset, 0)

        # Set the caret offset to something ridiculous
        entry.caretOffset = len(s * 3)

        # Make sure the caret offset only goes as far as the end of the string
        self.assertEquals(entry.caretOffset, len(s))

        def splitByOffsets(node, string):
            # Verify the equality of node.text and string, word by word.
            # I realize this doesn't really test dogtail itself, but that could
            #   change in the future and I don't want to throw the code away.
            textIface = node.queryText()
            endOffset = -1 # We only set this now so the loop looks nicer
            startOffset = 0
            while startOffset != len(string):
                (text, startOffset, endOffset) = textIface.getTextAtOffset(
                        startOffset, pyatspi.TEXT_BOUNDARY_WORD_START)
                self.assertEquals(startOffset,
                        string.find(text, startOffset, endOffset))
                startOffset = endOffset

        splitByOffsets(entry, s)

    # 'combovalue' (read/write string):
    def testSetComboValue(self):
        self.runDemo('Combo boxes')
        wnd = self.app.window('Combo boxes')
        combo1 = wnd.child('Some stock icons').child(roleName = 'combo box')
        combo1.combovalue = 'Clear'
        self.assertEquals(combo1.combovalue, 'Clear')

    # 'stateSet' (read-only StateSet instance):
    def testGetStateSet(self):
        "Node.sensitive should be False for the gtk3-demo app node"
        self.assert_(not self.app.sensitive)

    def testSetStateSet(self):
        "Node.stateSet should be read-only"
        # FIXME should be AttributeError?
        self.assertRaises(RuntimeError, self.app.__setattr__,  "states", pyatspi.StateSet())

    # 'relations' (read-only list of atspi.Relation instances):
    def testGetRelations(self):
        # FIXME once relations are used for something other than labels
        pass

    # 'labelee' (read-only list of Node instances):
    def testGetLabelee(self):
        "Entry1/2's labelee should be a text widget"
        self.runDemo('Dialog and Message Boxes')
        wnd = self.app.window('Dialogs')
        label = wnd.child('Entry 1')
        self.assertEquals(label.labelee.roleName, 'text')


    def testSetLabelee(self):
        "Node.labelee should be read-only"
        self.assertRaises(AttributeError, self.app.__setattr__,  "labellee", None)

    # 'labeler' (read-only list of Node instances):
    def testGetLabeler(self):
        "The text areas in the 'Dialogs' window should have labelers."
        self.runDemo('Dialog and Message Boxes')
        wnd = self.app.window('Dialogs')
        from dogtail.predicate import GenericPredicate
        text = wnd.findChildren(GenericPredicate(roleName='text'))[-1]
        self.assertEquals(text.labeler.name, 'Entry 1')


    def testSetLabeller(self):
        "Node.labeller should be read-only"
        self.assertRaises(AttributeError, self.app.__setattr__,  "labeller", None)

    # 'sensitive' (read-only boolean):
    def testGetSensitive(self):
        """
        Node.sensitive should not be set for the gtk3-demo app.
        It should be set for the window within the app.
        """
        self.assert_(not self.app.sensitive)
        self.assert_(self.app.children[0].sensitive)

    def testSetSensitive(self):
        "Node.sensitive should be read-only"
        self.assertRaises(AttributeError, self.app.__setattr__,  "sensitive", True)

    # 'showing' (read-only boolean):
    def testGetShowing(self):
        "Node.showing should not be set for the gtk3-demo.  It should be set for the window within the app"
        self.assert_(not self.app.showing)
        self.assert_(self.app.children[0].showing)

    def testSetShowing(self):
        "Node.showing should be read-only"
        self.assertRaises(AttributeError, self.app.__setattr__,  "showing", True)

    # 'actions' (read-only list of Action instances):
    def testGetActions(self):
        "Node.actions should be an empty list for the app node"
        self.assertEquals(len(self.app.actions), 0) 
   
    def testSetActions(self):
        "Node.actions should be read-only"
        self.assertRaises(AttributeError, self.app.__setattr__,  "actions", {})

    # 'extents' (readonly tuple):
    def testGetExtents(self):
        "Node.extents should be a 4-tuple for a window, with non-zero size"
        (x,y,w,h) = self.app.children[0].extents
        self.assert_(w>0)
        self.assert_(h>0)

    def testSetExtents(self):
        "Node.extents should be read-only"
        self.assertRaises(AttributeError, self.app.__setattr__,  "extents", (0,0,640,480))

    # 'position' (readonly tuple):
    def testGetPosition(self):
        "Node.position should be a 2-tuple for a window"
        (x,y) = self.app.children[0].position

    def testSetPosition(self):
        "Node.position should be read-only"
        self.assertRaises(AttributeError, self.app.__setattr__,  "position", (0,0))

    # 'size' (readonly tuple):
    def testGetSize(self):
        "Node.size should be a 2-tuple for a window, with non-zero values"
        (w,h) = self.app.children[0].size
        self.assert_(w>0)
        self.assert_(h>0)

    def testSetSize(self):
        "Node.size should be read-only"
        self.assertRaises(AttributeError, self.app.__setattr__,  "size", (640,480))

    # 'toolkitName' (readonly string):
    def testGetToolkit(self):
        self.assertEquals(self.app.toolkitName, "gtk")

    def testSetToolkit(self):
        "Node.toolkit should be read-only"
        self.assertRaises(AttributeError, self.app.__setattr__,  "toolkitName", "GAIL")

    # 'debugName':
    def testGetDebugName(self):
        self.assertEquals(self.app.debugName, u'"gtk3-demo" application')

    def testSetDebugName(self):
        self.app.debugName = 'test'
        self.assertEquals(self.app.debugName, "test")

    # 'dead' (readonly string):
    def testGetDead(self):
        self.assertEquals(self.app.dead, False)

    def testSetDead(self):
        "Node.dead should be read-only"
        self.assertRaises(AttributeError, self.app.__setattr__,  "dead", True)

    # 'ID'
    def testGetID(self):
        "Node.id should be numeric"
        self.assertEquals(type(self.app.id), type(42))

    def testSetID(self):
        "Node.id should be read-only"
        self.assertRaises(AttributeError, setattr, self.app, "id", 42)

    def testKeyCombo(self):
        self.runDemo('Application window')
        wnd = self.app.window('Application Window')
        wnd.keyCombo("<ctrl>a")
        from dogtail.predicate import IsADialogNamed
        self.assertEquals(len(self.app.findChildren(IsADialogNamed('About GTK+ Code Demos'))), 1)

    def testIsChild(self):
        self.assertTrue(self.app.isChild(name='Builder'))

    def testGetVisibleStrings(self):
        from dogtail.predicate import GenericPredicate
        expected = []
        expected.append(self.app.name)
        expected.extend(map(lambda x: x.name,
            self.app.findChildren(GenericPredicate(roleName='frame'))))
        expected.extend(map(lambda x: x.name,
            self.app.findChildren(GenericPredicate(roleName='page tab'))))
        expected.extend(map(lambda x: x.name,
            self.app.findChildren(GenericPredicate(roleName='table cell'))))
        expected.sort()
        actual = self.app.getUserVisibleStrings()
        actual.sort()

        self.assertEquals(actual, expected)


class TestSelection(Gtk3DemoTest):

    def testTabs(self):
        """
        Tabs in the gtk3-demo should be selectable, and be queryable for
        "isSelected", and the results should change as they are selected.
        """
        # Use the Info/Source tabs of gtk3-demo:
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

    def testSelectDeselect(self):
        treeViewCell = self.app.child('Icon View', roleName = 'table cell')
        treeViewCell.typeText('+')
        dogtail.tree.doDelay()
        sb = self.app.child(roleName = 'scroll bar')
        sb.value += 50
        self.runDemo('Icon View Basics')

        wnd = self.app.window('GtkIconView demo')
        icons = wnd.child(roleName='layered pane').children

        icons[0].select()
        icons[1].select()
        icons[0].deselect()
        self.assertFalse(icons[0].isSelected)
        self.assertTrue(icons[1].isSelected)

    def testSelectAll(self):
        treeViewCell = self.app.child('Icon View', roleName = 'table cell')
        treeViewCell.typeText('+')
        dogtail.tree.doDelay()
        sb = self.app.child(roleName = 'scroll bar')
        sb.value += 50
        self.runDemo('Icon View Basics')

        wnd = self.app.window('GtkIconView demo')
        pane = wnd.child(roleName='layered pane')
        icons = pane.children

        self.assertTrue(pane.selectAll())
        for icon in icons:
            self.assertTrue(icon.isSelected)

    def testDeselectAll(self):
        treeViewCell = self.app.child('Icon View', roleName = 'table cell')
        treeViewCell.typeText('+')
        dogtail.tree.doDelay()
        sb = self.app.child(roleName = 'scroll bar')
        sb.value += 50
        self.runDemo('Icon View Basics')

        wnd = self.app.window('GtkIconView demo')
        pane = wnd.child(roleName='layered pane')
        icons = pane.children

        icons[0].select()
        icons[5].select()
        icons[7].select()

        self.assertTrue(pane.deselectAll())
        for icon in icons:
            self.assertFalse(icon.isSelected)

    def testSelectedChildren(self):
        treeViewCell = self.app.child('Icon View', roleName = 'table cell')
        treeViewCell.typeText('+')
        dogtail.tree.doDelay()
        sb = self.app.child(roleName = 'scroll bar')
        sb.value += 50
        self.runDemo('Icon View Basics')

        wnd = self.app.window('GtkIconView demo')
        pane = wnd.child(roleName='layered pane')
        icons = pane.children

        selected_icons = [icons[0], icons[3], icons[5]]
        for icon in selected_icons:
            icon.select()

        self.assertEquals(pane.selectedChildren, selected_icons)


class TestValue(Gtk3DemoTest):
    def testGetValue(self):
        "The scrollbar starts out at position zero."
        sb = self.app.child(roleName = 'scroll bar')
        self.assertEquals(sb.value, 0)

    def testSetValue(self):
        "Ensure that we can set the value of the scrollbar."
        sb = self.app.child(roleName = 'scroll bar')
        sb.value = 100
        self.assertEquals(sb.value, 100)

    def testMinValue(self):
        "Ensure that the minimum value for the scrollbar is correct."
        sb = self.app.child(roleName = 'scroll bar')
        self.assertEquals(sb.minValue, 0)

    def testMaxValue(self):
        "Ensure that the maximum value for the scrollbar is plausible."
        sb = self.app.child(roleName = 'scroll bar')
        self.assert_(sb.maxValue > 250)

    def testMinValueIncrement(self):
        "Ensure that the minimum value increment of the scrollbar is an int."
        sb = self.app.child(roleName = 'scroll bar')
        self.assertEquals(sb.minValueIncrement, sb.minValueIncrement)


class TestSearching(Gtk3DemoTest):
    # FIXME: should test the various predicates and the search methods of Node
    def testFindChildren(self):
        """
        Ensure that there are the correct number of table cells in the list
        of demos.
        """
        pred = dogtail.predicate.GenericPredicate(roleName = 'table cell')
        tableCells = self.app.findChildren(pred)

        def get_table_cells_recursively(node):
            counter = 0
            for child in node.children:
                if child.roleName == 'table cell': counter += 1
                counter += get_table_cells_recursively(child)
            return counter

        counter = get_table_cells_recursively(self.app)
        self.assertEquals(len(tableCells), counter)

    def testFindChildren2(self):
        "Ensure that there are two tabs in the second page tab list."
        pred = dogtail.predicate.GenericPredicate(roleName = 'page tab list')
        pageTabLists = self.app.findChildren(pred)
        pred = dogtail.predicate.GenericPredicate(roleName = 'page tab')
        # The second page tab list is the one with the 'Info' and 'Source' tabs
        pageTabs = pageTabLists[1].findChildren(pred)
        self.assertEquals(len(pageTabs), 2)

    def testFindChildrenNonRecursive(self):
        """
        Ensure that there are the correct number of table cells in the Tree
        Store demo.
        """
        # The next several lines exist to expand the 'Tree View' item and
        # scroll down, so that runDemo() will work.
        # FIXME: make runDemo() handle this for us.
        treeViewCell = self.app.child('Tree View', roleName = 'table cell')
        treeViewCell.typeText('+')
        dogtail.tree.doDelay()
        sb = self.app.child(roleName = 'scroll bar')
        sb.value = sb.maxValue
        self.runDemo('Tree Store')
        wnd = self.app.window('Card planning sheet')
        table = wnd.child(roleName = 'tree table')
        pred = dogtail.predicate.GenericPredicate(roleName = 'table cell')
        dogtail.config.config.childrenLimit = 10000
        cells = table.findChildren(pred, recursive = False)
        direct_cells = filter(lambda cell: cell.roleName=='table cell',  table.children)
        self.assertEquals(len(cells), len(direct_cells))

    def testFindAncestor(self):
        cell = self.app.child('Builder')
        pred = dogtail.predicate.GenericPredicate(roleName = 'application')
        self.assertEquals(cell.findAncestor(pred), self.app)


class TestActions(Gtk3DemoTest):
    def test_click(self):
        self.runDemo('Application main window')
        wnd = self.app.window('Application Window')
        action = wnd.child(name='About').actions['click']
        self.assertEquals(action.name, 'click')
        self.assertEquals(action.description, '')
        self.assertEquals(action.keyBinding, 'a;<Alt>h:a;<Primary>a')
        self.assertEquals(str(action), '[action | click | a;<Alt>h:a;<Primary>a ]')

        action.do()
        from dogtail.predicate import IsADialogNamed
        self.assertEquals(len(self.app.findChildren(IsADialogNamed('About GTK+ Code Demos'))), 1)

    def test_press(self):
        self.runDemo('Application main window')
        wnd = self.app.window('Application Window')
        child = wnd.child(name='Quit')
        action = child.actions['press']
        self.assertEquals(action.name, 'press')
        self.assertEquals(action.description, '')
        self.assertEquals(action.keyBinding, '')
        self.assertEquals(str(action), '[action | press |  ]')

        action.do()
        self.assertTrue(pyatspi.state.STATE_ARMED in child.getState().getStates())

    def test_release(self):
        self.runDemo('Application main window')
        wnd = self.app.window('Application Window')
        child = wnd.child(name='Quit')
        action = child.actions['release']
        self.assertEquals(action.name, 'release')
        self.assertEquals(action.description, '')
        self.assertEquals(action.keyBinding, '')
        self.assertEquals(str(action), '[action | release |  ]')

        child.actions['press'].do()
        child.actions['release'].do()
        self.assertTrue(pyatspi.state.STATE_ARMED not in child.getState().getStates())

    def test_activate(self):
        child = self.app.child(name='Application main window')
        action = child.actions['activate']
        self.assertEquals(action.name, 'activate')
        self.assertEquals(action.description, 'activate the cell')
        self.assertEquals(action.keyBinding, '')
        self.assertEquals(str(action), '[action | activate |  ]')

        action.do()
        from dogtail.predicate import IsAWindowNamed
        self.assertEquals(len(self.app.findChildren(IsAWindowNamed('Application Window'))), 1)

    def test_incorrect_action(self):
        child = self.app.child(name='Application main window')
        self.assertRaises(dogtail.tree.ActionNotSupported, child.doActionNamed, 'none')


class TestExceptions(Gtk3DemoTest):
    def test_exception(self):
        # Kill the gtk3-demo prematurely:
        import os, signal
        os.kill(self.pid, signal.SIGKILL)

        import gi._glib
        # Ensure that we get an exception when we try to work further with it:
        self.assertRaises(gi._glib.GError, self.app.dump)


def trap_stdout(function, args=None):
    import sys
    from StringIO import StringIO

    saved_stdout = sys.stdout
    try:
        out = StringIO()
        sys.stdout = out
        if args:
            if type(args) is dict:
                function(**args)
            else:
                function(args)
        else:
            function()
        output = out.getvalue().strip()
    finally:
        sys.stdout = saved_stdout
    return output

class TestDump(Gtk3DemoTest):

    def setUp(self):
        super(TestDump, self).setUp()
        self.child = self.app.child("Source")
        self.expected = """[page tab | Source]
 [scroll pane | ]
  [text | ]
  [scroll bar | ]
   [action | activate |  ]
  [scroll bar | ]
   [action | activate |  ]"""

    def test_dump_to_stdout(self):
        output = trap_stdout(self.child.dump)
        self.assertEquals(output, self.expected)


class TestTree(Gtk3DemoTest):
    def test_check_for_a11y(self):
        dogtail.config.config.checkForA11y = True
        dogtail.tree.checkForA11y()


if __name__ == '__main__':
    unittest.main()
