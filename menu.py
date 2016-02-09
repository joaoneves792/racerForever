import sys
sys.path.append('./libs')

from gi.repository import Gtk
from singletons import Window
from racerForever import Game

__play__ = False


class Menu(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="RACER Forever")

        self.grid = Gtk.Grid()
        self.grid.set_orientation(Gtk.Orientation.VERTICAL)
        self.add(self.grid)
        image = Gtk.Image.new_from_file("./Menuscreen.png")
        self.grid.add(image)
        self.box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.HORIZONTAL, homogeneous=False)
        self.grid.add(self.box)
        label = Gtk.Label(label="Resolution", halign=Gtk.Align.CENTER)
        self.box.pack_start(label, False, False, 0)
        self.width = Gtk.Entry()
        self.width.set_text(str(Window.WIDTH))
        self.box.pack_start(self.width, False, False, 0)
        self.height = Gtk.Entry()
        self.height.set_text(str(Window.HEIGHT))
        self.box.pack_start(self.height, False, False, 0)
        self.fullscreen = Gtk.CheckButton("Fullscreen")
        self.fullscreen.set_active(Window.FULLSCREEN)
        self.box.pack_start(self.fullscreen, False, False, 0)
        play = Gtk.Button(label="Play!")
        self.box.pack_end(play, False, False, 0)
        play.connect("clicked", self.play_game)

        self.resize(800, 600)

    def play_game(self, widget):
        global __play__
        __play__ = True
        Window.WIDTH = int(self.width.get_text())
        Window.HEIGHT = int(self.height.get_text())
        Window.FULLSCREEN = self.fullscreen.get_active()
        self.hide()
        Gtk.main_quit()

menu = Menu()
menu.connect("delete-event", Gtk.main_quit)
menu.show_all()
Gtk.main()
if __play__:
    game = Game()
