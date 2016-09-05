# window.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.0-alpha

import os
import tkinter as pygui
from PIL import Image, ImageTk
from app.blackjack.game.error import GameError

class Window(object):

  def __init__(self, window_title="BlackJack"):
    # create new instance of TK
    self.window = pygui.Tk()

    # save the window title
    self.window_title = window_title

    # initialize remote connection
    self.remote_connection = None

    # [Splash GUI Init] ::start
    self.splash_bootstrapped = False

    self.splash_frame = pygui.Frame(self.window)
    self.start_btn = pygui.Button(self.splash_frame, text="Start Game", command=lambda: self.switch_context('main'))
    self.splash_logo_canvas = pygui.Canvas(self.splash_frame, width=375, height=355)
    # [Splash GUI Init] ::end

    # [Main GUI Init] ::start
    self.main_frame = pygui.Frame(self.window)
    # self.deal_btn = pygui.Button(self.main_frame, text="Deal")
    # self.hit_btn = pygui.Button(self.main_frame, text="Hit")
    # [Main GUI Init] ::end

  def bootstrap(self):
    # set window title
    self.window.wm_title(self.window_title)

    # show the splash page
    self.splash_gui()

    # set default window size
    self.window.minsize(500, 500)

    # Start the GUI
    self.window.mainloop()

  def switch_context(self, context):
    if context == 'main':
      # hide the splash page
      self.splash_frame.pack_forget()

      # Show the frame for the game
      self.main_gui()
    else:
      # hide the game
      self.main_frame.pack_forget()

      # Show the splash page.
      self.splash_gui()

  def splash_gui(self):
    if self.splash_bootstrapped is False:
      splash_logo_img = os.path.join(os.getcwd(), "resources/images/royal-flush.png")

      if not os.path.exists(splash_logo_img):
        raise GameError("Logo for Splash page not found!")

      # open the image and render it on the canvas
      splash_logo = Image.open(splash_logo_img)

      # prevent garbage collection that's why we are storing the reference to the window object
      self.window.splash_logo = splash_logo_tk = ImageTk.PhotoImage(splash_logo)

      self.splash_logo_canvas.create_image(0, 0, image=splash_logo_tk, anchor=pygui.NW)
      self.splash_logo_canvas.pack()

      # position the start button
      self.start_btn.grid(row=1, column=0)
      self.start_btn.configure()
      self.start_btn.pack()

      # set the bootstrap flag to true
      self.splash_bootstrapped = True

    self.splash_frame.pack(padx=10, pady=25)

  def main_gui(self):
    pass


