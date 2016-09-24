# tkimg.py
#
# Copyright(c) Exequiel Ceasar Navarrete <esnavarrete1@up.edu.ph>
# Licensed under MIT
# Version 1.0.2

import os
from PIL import Image, ImageTk
import tkinter as pygui

card_img = os.path.join(os.getcwd(), "resources/images/cards.png")

window = pygui.Tk()

# set default window size
window.minsize(500, 500)

# open the image file
card_img = Image.open(card_img)

# destructure list
width, height = card_img.size

# create the game canvas
canvas = pygui.Canvas(window, width=1200, height=650)

# [Automatic] ::start
top    = 0
right  = int(width / 13)
bottom = int(height / 5)
left   = 0

# create tmp coordinates
tmp_top    = top
tmp_right  = right
tmp_bottom = bottom
tmp_left   = left

# prevent garbage collection that's why we are storing the reference to the window object
window.resolved_cards = []

for shape in range(0, 4):
  for face in range(0, 13):
    # resolve each card
    resolved_face_and_shape = card_img.crop((tmp_left, tmp_top, tmp_right, tmp_bottom))

    # create tk image
    tk_resolved_face_and_shape = ImageTk.PhotoImage(resolved_face_and_shape)
    window.resolved_cards.append(tk_resolved_face_and_shape)

    # create canvas image
    canvas.create_image(tmp_left, tmp_top, image=tk_resolved_face_and_shape, anchor=pygui.NW)

    # adjust left and right coordinates
    tmp_left  += right
    tmp_right += right

  # reset top and left coordinates
  tmp_left  = 0
  tmp_right = right

  # adjust top and bottom coordinates
  tmp_top    += bottom
  tmp_bottom += bottom

# close the file pointer
card_img.close()
# [Automatic] ::end

# [Manual] ::start
# # left, top, right, bottom
# ace_space = window.card_img.crop((0, 0, 80, 124))
# window.card_ace_spade = ImageTk.PhotoImage(ace_space)

# # left, top, right, bottom
# two_spade = window.card_img.crop((80, 0, 160, 124))
# window.card_two_spade = ImageTk.PhotoImage(two_spade)

# # left, top, right, bottom
# ace_diamond = window.card_img.crop((0, 124, 80, 248))
# window.card_ace_diamond = ImageTk.PhotoImage(ace_diamond)

# # draw image on the canvas
# canvas.img_item = canvas.create_image(0, 0, image=window.card_ace_spade, anchor=pygui.NW)
# canvas.img_item_two = canvas.create_image(80, 0, image=window.card_two_spade, anchor=pygui.NW)
# canvas.img_item_three = canvas.create_image(160, 0, image=window.card_ace_diamond, anchor=pygui.NW)

# # delete item from the canvas
# canvas.delete(canvas.img_item_three)
# [Manual] ::end

# display the canvas
canvas.pack(side=pygui.LEFT)

# start the window
window.mainloop()


