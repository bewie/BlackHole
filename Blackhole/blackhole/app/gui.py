# -*- coding: utf-8 -*-
import logging
import time
import urwid
from blackhole import get_version
import blackhole
from .popup import PopUpNotificationLauncher
# global cache of directory information
global _environments_cache
global _environments_cache_index


_environments_cache = {}
_environments_cache_index = []

QUIT_KEYS = ('q', 'Q')
EXPAND_KEYS = (" ", "enter")

logger = logging.getLogger("blackhole.gui")

def store_initial_environment(initial, end):
    """Store the initial current working directory path components."""
    global _initial_environment, _end_environment
    _initial_environment = initial # Nombre del primer environment
    _end_environment = end # nombre del segundo environment


def get_environment(name):
    """Return the Directory object for a given path.  Create if necessary."""
    return _environments_cache[name]


def get_next_environment(name):
    index = _environments_cache_index.index(name)
    if index < len(_environments_cache_index) - 1:
        return _environments_cache[_environments_cache_index[index + 1]]
    return False


def get_prev_environment(name):
    index = _environments_cache_index.index(name)
    if index > 0:
        return _environments_cache[_environments_cache_index[index - 1]]
    return False


def set_cache(environment, host_connections, window):
    """
    en _environments_cache guarda los evironmentStore y usa _environments_cache_index como indice para acceder en forma directa
    """
    _environments_cache[environment.name] = EnvironmentStore(environment, host_connections, window)
    _environments_cache_index.append(environment.name)


class Window():

    def __init__(self, blackhole_app):
        logger.debug(u"Window Created")
        self.blackhole = blackhole_app
        self.version = get_version()
        self.current_user_full_name = self.blackhole.get_user_full_name()
        self.header_text = ""
        self.footer_text = ""
        self.draw_ui()

    def set_palette(self):
        self.palette = [
            ('body', 'black', 'light gray'),  # Normal Text
            ('focus', 'light green', 'black', 'standout'),  # Focus
            ('head', 'white', 'dark gray', 'standout'),  # Header
            ('foot', 'light gray', 'dark gray'),  # Footer Separator
            ('key', 'light green', 'dark gray', 'bold'),
            ('title', 'white', 'black', 'bold'),
            ('environmentMark', 'dark blue', 'light gray', 'bold'),
            ('focus_error', 'dark red', 'black'),
            ('error', 'dark red', 'light gray', 'bold'),
            ('footer_msg', 'yellow', 'dark gray'),
            ('popup', 'white', 'dark red'),
            ('DB', 'dark magenta', 'light gray'),
            ('DB_focus', 'light green', 'dark magenta', 'standout'),  # Focus
            ('SSH', 'dark blue', 'light gray', 'underline'),
            ('SSH_focus', 'light green', 'dark blue', 'standout'),  # Focus
        ]

    def set_footer_text(self):
        self.footer_text = [
            ('footer_msg', "Move:"),
            ('key', "up"), ",", ('key', "down"), ",",
            ('key', "home"), ",",
            ('key', "end"), ",",
            ('key', "left"), ",",
            ('key', "w/Mouse"), " ",
            ('footer_msg', "Expand:"),
            ('key', "space"), ",", ('key', "click"), " ",
            ('footer_msg', "Select:"),
            ('key', "enter"), " ",
            ('footer_msg', "Quit:"),
            ('key', "q"), " ",
            ('footer_msg', "By:"),
            ('key', blackhole.get_author()),
            ('footer_msg', '(v%s)' % self.version)]

    def update_header_text(self):
        if hasattr(self, "listbox"):
            focus, _ign = self.listbox.body.get_focus()
            self.header_text = [('key', "BlackHole"), " ",
                                ('footer_msg', "User:"),
                                ('key', "%s" % self.current_user_full_name), " ",
                                ('footer_msg', "- Selected:"),
                                ('key', "%s" % focus.selected_text if focus else "No targets available")]
            self.header_widget.set_text(self.header_text)

    def draw_ui(self):
        logger.debug(u"Drawing UI")
        self.set_palette()
        #Menu
        self.listbox = urwid.ListBox(EnvironmentWalker(self.blackhole.user, self.blackhole.get_environments(), self))
        self.listbox.offset_rows = 1
        # Footer
        self.set_footer_text()
        self.footer = urwid.AttrMap(urwid.Text(self.footer_text, align='center'), 'foot')
        # Header
        self.header_widget = urwid.Text(self.header_text, align='left')
        self.update_header_text()
        #popup
        self.popup_launcher = PopUpNotificationLauncher()
        pop_pad = urwid.Padding(self.popup_launcher, 'right', 20)
        popup_map = urwid.AttrMap(pop_pad, 'indicator')
        header_map = urwid.AttrMap(self.header_widget, 'head')
        self.header = urwid.Columns([header_map, popup_map])
        self.view = urwid.Frame(urwid.AttrWrap(self.listbox, 'body'), header=self.header, footer=self.footer)
        self.screen = urwid.raw_display.Screen()
        self.loop = urwid.MainLoop(self.view, palette=self.palette, unhandled_input=self.handle_key, pop_ups=True, screen=self.screen)

    def handle_key(self, key):
        if not urwid.is_mouse_event(key):
            if key in QUIT_KEYS:
                self.blackhole.quit()
        return True

    def show_notification(self, message):
        self.popup_launcher.message = message
        self.popup_launcher.open_pop_up()

    def start_ui(self):
        logger.debug(u"Gui started")
        self.loop.run()

    def stop_ui(self):
        logger.debug(u"Gui stopped")
        raise urwid.ExitMainLoop()

    def pause_screen(self):
        logger.debug(u"Gui paused")
        self.loop.screen.stop()

    def restore_screen(self):
        logger.debug(u"Gui restored")
        self.loop.screen.start()

    # Signals Callbacks

    def focus_changed(self):
        self.update_header_text()

    def start_connection(self, sender):
        self.loop.draw_screen()
        try:
            self.blackhole.start_connection(sender)
        except Exception as e:
            #logger.error(e)
            self.show_notification(e.message)
        finally:
            self.restore_screen()



################ Urwid Classes


class EnvironmentStore(object):
    """
    Stores the environment and its hosts as Tree widgets
    * environments: environment object
    """
    def __init__(self, environment, host_connections, window):
        """
        Constructor.
        Arguments:
        user -- User Object
        environment -- Environment Object
        """
        self.window = window
        self.environment = environment
        self.environment_w = EnvironmentTree(self.environment, len(host_connections), window)
        self.widgets = {}
        self.widgets_index = []
        self.set_hosts(host_connections)

    def set_hosts(self, host_connections):
        """Crea los objetos equipos.
        Tengo que pasar una lista, que contenga una lista con los equipos de cada ambiente.
        y en el index 0 el ambiente"""
        j = 0
        for hostConnection in host_connections:
            key = "%s_%s" % (hostConnection.host.name, hostConnection.id)
            if key not in self.widgets:
                host_tree = HostTree(self.environment, hostConnection, j, self.window)
                urwid.connect_signal(host_tree, 'connect', self.window.start_connection)
                self.widgets[key] = host_tree
                self.widgets_index.append(key)
                j += 1

    def get_widget(self, name):
        """Return the widget for a given host."""
        if name == self.environment.name:
            return self.environment_w
        else:
            return self.widgets[name]

    def next_inorder_from(self, index):
        """Return the Widget following index depth first."""
        if index < len(self.widgets_index) - 1:
                index += 1
                return self.get_widget(self.widgets_index[index])
        else:
            nextEnvironment = get_next_environment(self.environment.name)
            if nextEnvironment:
                return nextEnvironment.environment_w
            else:
                return None

    def prev_inorder_from(self, index):
        """Return the TreeWidget preceeding index depth first."""
        if index > 0:
            index -= 1
            return self.get_widget(self.widgets_index[index])
        else:
            return self.environment_w

    def get_first(self):
        """Return the first TreeWidget in the directory."""
        if self.environment_w.expanded:
            return self.get_widget(self.widgets_index[0])
        else:
            return self.environment_w

    def get_last(self):
        """Return the last TreeWIdget in the directory."""
        if self.environment_w.expanded:
            return self.get_widget(self.widgets_index[-1])
        else:
            return self.environment_w


class EnvironmentWalker(urwid.ListWalker):
    def __init__(self, user, environments, window):
        self._window = window
        if len(environments) > 0:
            first_environment_name = environments[0].name
            last_environment_name = environments[-1].name
            store_initial_environment(first_environment_name, last_environment_name)
            for environment in environments:
                hc = user.profile.get_hostsConnections(environment)
                set_cache(environment, hc, window)
            widget = get_environment(first_environment_name).environment_w
            self.focus = first_environment_name, widget.target_id
        else:
            pass

    def get_focus(self):
        """
        get the widget in focus
        """
        if not len(_environments_cache):
            return None, None
        else:
            parent, target_id = self.focus
            widget = get_environment(parent).get_widget(target_id)
            return widget, self.focus

    def set_focus(self, focus):
        """
        set focus in especific widget
        """
        parent, target_id = focus
        self.focus = parent, target_id
        self._modified()
        self._window.update_header_text()


    def get_next(self, start_from):
        """
        get next widget
        """
        parent, target_id = start_from
        widget = get_environment(parent).get_widget(target_id)
        target = widget.next_inorder()
        if target is None:
            return None, None
        return target, (target.environment, target.target_id)

    def get_prev(self, start_from):
        """
        get previous widget
        """
        parent, target_id = start_from
        widget = get_environment(parent).get_widget(target_id)
        target = widget.prev_inorder()
        if target is None:
            return None, None
        return target, (target.environment, target.target_id)


class TreeWidget(urwid.WidgetWrap):
    """A widget representing something in the file tree.
    * environment: string with the name of the environment
    * name: string with the name of the object
    * index: integer with the index of the object
    * display:
    * description: string with the description of the object
    """
    def __init__(self, environment, name, target_id, index, description, window):
        self.last_click = None
        self._window = window
        self._selectable = True
        self.environment = environment
        self.name = name
        self.target_id = target_id
        self.index = index
        self.description = description
        w = urwid.AttrWrap(self.widget, None)
        self.__super.__init__(w)
        self.selected = False
        self.update_w()

    @property
    def focus_style(self):
        return self._focus_style

    def selectable(self):
        return self._selectable

    def keypress(self, size, key):
        """Toggle selected on space, ignore other keys."""
        return key

    def update_w(self):
        """
        Update the attributes of wrapped widget based on self.selected.
        """
        self._w.attr = 'body'
        self._w.focus_attr = self.focus_style

    def first_child(self):
        """Default to have no children."""
        return None

    def last_child(self):
        """Default to have no children."""
        return None

    def next_inorder(self):
        """Return the next TreeWidget depth first from this one."""
        return get_environment(self.environment).next_inorder_from(self.index)

    def prev_inorder(self):
        """Return the previous TreeWidget depth first from this one."""
        return get_environment(self.environment).prev_inorder_from(self.index)


class EnvironmentTree(TreeWidget):
    def __init__(self, environment, host_count, window):
        self._focus_style = "focus"
        self.widget = urwid.Text([""])
        self.__super.__init__(environment.name, environment.name, environment.name, 0, environment.description, window)
        self.expanded = False
        self.number_of_hosts = host_count
        self.update_widget()

    def next_inorder(self):
        if not self.expanded:
            next_environment = get_next_environment(self.target_id)
            if next_environment:
                return next_environment.environment_w
            else:
                return None
        else:
            return self.first_child()

    def prev_inorder(self):
        prev_environment = get_prev_environment(self.target_id)
        if prev_environment:
            if not prev_environment.environment_w.expanded:
                return prev_environment.environment_w
            else:
                return prev_environment.environment_w.last_child()

    def update_widget(self):
        """Update display widget text."""
        if self.expanded:
            mark = "[-]"
        else:
            mark = "[+]"
        self.widget.set_text(["", ('environmentMark', mark), " ",
                             u"{0} - Targets: {1}".format(self.description, self.number_of_hosts)])

    def keypress(self, size, key):
        """Handle expand & collapse requests."""
        if key in EXPAND_KEYS:
            self.expanded = not self.expanded
            self.update_widget()
            return None
        else:
            return key

    def mouse_event(self, size, event, button, col, row, focus):
        if event != 'mouse press' or button != 1:
            return False
        if row == 0 and col < 3:
            self.expanded = not self.expanded
            self.update_widget()
            return True
        else:
            if self.last_click:
                now = time.time()
                i = now - self.last_click
                if i < 0.6:
                    self.expanded = not self.expanded
                    self.update_widget()
                    self.last_click = None
                else:
                    self.last_click = now
            else:
                self.last_click = time.time()
        return False

    def first_child(self):
        """Return first child if expanded."""
        if not self.expanded:
            return get_environment(self.environment).environment_w
        return get_environment(self.environment).get_first()

    def last_child(self):
        """Return last child if expanded."""
        if not self.expanded:
            return get_environment(self.environment).environment_w
        else:
            return get_environment(self.environment).get_last()

    @property
    def selected_text(self):
        return self.description

class HostTree(TreeWidget):
    signals = ['connect']

    def __init__(self, environment, host_connection, index, window):
        self.host_connection = host_connection
        self._focus_style = "{0}_focus".format(self.host_connection.host.CONNECTION_TYPE)
        self._connecting_widget_text = [(self._focus_style, 'Connecting...')]
        self._widget_text = [u"  {0} <{1.CONNECTION_TYPE}> ".format(self.description_text, self.host_connection.host)]
        self.widget = urwid.Text(self._widget_text)
        target_id = u"%s_%s" % (self.host_connection.host.name, self.host_connection.id)
        self.__super.__init__(environment.name, self.host_connection.host.name, target_id, index, self.description_text, window)

    @property
    def description_text(self):
        return u"{0.host.name} - {0.host.description} (as {0.authentication_user.username})".format(self.host_connection) if self.host_connection.host.description else "{0.host.name} (as {0.authentication_user.username})".format(self.host_connection)

    def keypress(self, size, key):
        """Handle expand & collapse requests."""
        if key == "enter":
            self.widget.set_text(self._connecting_widget_text)
            self._emit('connect')
            self.widget.set_text(self._widget_text)
            return None
        elif key == 'left':
            self._window.listbox.body.set_focus((self.environment, self.environment))
        else:
            return key

    def mouse_event(self, size, event, button, col, row, focus):
        if event != 'mouse press' or button != 1:
            return False
        if self.last_click:
            now = time.time()
            i = now - self.last_click
            if i < 0.6:
                self.last_click = None
                self.widget.set_text(self._connecting_widget_text)
                self._emit('connect')
                self.widget.set_text(self._widget_text)
                return False
            else:
                self.last_click = now
        else:
            self.last_click = time.time()
        return False

    @property
    def selected_text(self):
        return self.name