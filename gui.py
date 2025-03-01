import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from PIL import Image, ImageTk, ImageOps, ImageFilter, ImageEnhance

image_path = ''
opened_img = edited_img = ''
img_width = 0
img_height = 0

def select_file() -> None:
    global edited_img, image_path, img_width, img_height
    filetypes = (('image files', '*.png ; *.jpg ; *.jpeg'),)
    image_path = fd.askopenfilename(title='Select an image', filetypes=filetypes)
    if image_path:
        original_img = Image.open(image_path)
        image_ratio = original_img.width / original_img.height
        img_height = height = int(disp_img_frame.winfo_height())
        img_width = width = int(height * image_ratio)
        edited_img = original_img.resize((width, height))
        display_image(edited_img)

def display_image(img : Image) -> None:
    global opened_img
    opened_img = ImageTk.PhotoImage(img)
    w = min(disp_img_frame.winfo_width(), img.width)
    h = min(disp_img_frame.winfo_height(), img.height)
    canvas.config(width = w, height = h)
    canvas.create_image(0, 0, image = opened_img, anchor = 'nw')

def resize_image(event):
    global opened_img
    if image_path:
        frame_ratio = event.width / event.height
        image_ratio = opened_img.width / opened_img.height
        if frame_ratio > image_ratio:
            height = int(event.height)
            width = int(height * image_ratio)
        else:
            width = int(event.width)
            height = int(width / image_ratio)
        opened_img = opened_img.resize((width, height))
        display_image(opened_img)

def crop_image(left, top, right, bottom):
    global edited_img
    cropped_img = Image.open(image_path).resize((img_width, img_height))
    edited_img = cropped_img.crop((left, top, img_width - right, img_height - bottom))
    display_image(edited_img)

def edit_controls(w, h):
    if opened_img:
        controls = tk.Toplevel()
        controls.geometry('400x300')
        controls.attributes('-topmost', 1)

        top_lb = ttk.Label(controls, text = 'Top')
        top_lb.pack(anchor = 'w')
        top_scale = ttk.Scale(controls, from_ = 0, to=h, orient = 'horizontal',
                              command = lambda x: crop_image(left_scale.get(),
                                                             top_scale.get(),
                                                             right_scale.get(),
                                                             bottom_scale.get()))
        top_scale.pack(anchor = 'w', fill = 'x')

        bottom_lb = ttk.Label(controls, text = 'Bottom')
        bottom_lb.pack(anchor = 'w')
        bottom_scale = ttk.Scale(controls, from_=0, to=h, orient='horizontal',
                                 command=lambda x: crop_image(left_scale.get(),
                                                              top_scale.get(),
                                                              right_scale.get(),
                                                              bottom_scale.get()))
        bottom_scale.pack(anchor='w', fill='x')

        left_lb = ttk.Label(controls, text = 'Left')
        left_lb.pack(anchor = 'w')
        left_scale = ttk.Scale(controls, from_=0, to=w, orient='horizontal',
                               command=lambda x: crop_image(left_scale.get(),
                                                            top_scale.get(),
                                                            right_scale.get(),
                                                            bottom_scale.get()))
        left_scale.pack(anchor='w', fill='x')

        right_lb = ttk.Label(controls, text = 'Right')
        right_lb.pack(anchor = 'w')
        right_scale = ttk.Scale(controls, from_=0, to=w, orient='horizontal',
                                command=lambda x: crop_image(left_scale.get(),
                                                             top_scale.get(),
                                                             right_scale.get(),
                                                             bottom_scale.get()))
        right_scale.pack(anchor='w', fill='x')

def convert_to_original():
    if opened_img:
        display_image(edited_img)

def covert_to_greyscale():
    if opened_img:
        img = edited_img.convert("L")
        display_image(img)

def convert_to_bw():
    if opened_img:
        img = edited_img.convert("L").point(lambda x: 255 if x > 128 else 0, mode = '1')
        display_image(img)

def convert_to_inverted():
    if opened_img:
        img = ImageOps.invert(edited_img)
        display_image(img)

def convert_to_blur():
    if opened_img:
        img = edited_img.filter(ImageFilter.GaussianBlur(5))
        display_image(img)

def convert_to_warm():
    if opened_img:
        img = edited_img.convert('RGB')
        r, g, b = img.split()
        r = r.point(lambda p: min(255, p * 1.2))
        g = g.point(lambda p: min(255, p * 1.1))
        b = b.point(lambda p: max(0, p * 0.9))
        warm_img = Image.merge('RGB', (r, g, b))
        warm_img = ImageEnhance.Brightness(warm_img).enhance(1.1)
        warm_img = ImageEnhance.Contrast(warm_img).enhance(1.2)
        display_image(warm_img)

def convert_to_nv():
    if opened_img:
        img = edited_img.convert('RGB')
        r, g, b = img.split()
        nv_img = Image.merge('RGB', (g, g.point(lambda x: min(255, x * 1.5)), g))
        display_image(nv_img)

"""
def zoom_in() -> None:
    global opened_img
    if opened_img:
        width = int(opened_img.width * 1.1)
        height = int(opened_img.height * 1.1)
        resized_img = opened_img.resize((width, height))
        display_image(resized_img)

def zoom_out() -> None:
    global opened_img
    if opened_img:
        width = int(opened_img.width * 0.9)
        height = int(opened_img.height * 0.9)
        resized_img = opened_img.resize((width, height))
        display_image(resized_img)
"""

window = tk.Tk()
window.title('Image Editor')
window.geometry('900x500+330+150')
window.minsize(900, 500)

menu = tk.Menu()
file_menu = tk.Menu(menu, tearoff=0)
file_menu.add_command(label='Open...', command=select_file)
file_menu.add_command(label='Save')
file_menu.add_command(label='Save as copy')
file_menu.add_separator()
file_menu.add_command(label='Exit', command=window.quit)
edit_menu = tk.Menu(menu, tearoff=0)
edit_menu.add_command(label='Crop', command = lambda : edit_controls(w=img_width, h=img_height))
edit_menu.add_command(label='Adjustment')
filter_menu = tk.Menu(edit_menu, tearoff = 0)
filter_menu.add_command(label = 'Warm', command = convert_to_warm)
filter_menu.add_command(label = 'Grayscale', command = covert_to_greyscale)
filter_menu.add_command(label = 'Night Vision', command = convert_to_nv)
filter_menu.add_command(label = 'B&W', command = convert_to_bw)
filter_menu.add_command(label = 'Invert', command = convert_to_inverted)
filter_menu.add_command(label = 'Blur', command = convert_to_blur)
filter_menu.add_command(label = 'None', command = convert_to_original)
edit_menu.add_cascade(label = 'Filters', menu = filter_menu)
edit_menu.add_command(label='Mark-up')
menu.add_cascade(label='File', menu=file_menu)
menu.add_cascade(label='Edit', menu=edit_menu)
window.configure(menu=menu)

disp_img_frame = tk.Frame(window)
disp_img_frame.place(relx = 0.5, rely = 0.5, relwidth = 0.8, relheight = 0.8, anchor = 'center')

canvas = tk.Canvas(disp_img_frame)
canvas.place(relx = 0.5, rely = 0.5, anchor = 'center')

b2 = ttk.Button(window, text = 'Zoom out')
b2.pack(side = 'right', anchor = 'se')
b1 = ttk.Button(window, text = 'Zoom in')
b1.pack(side = 'right', anchor = 'se')

# disp_img_frame.bind('<Configure>', resize_image)

window.mainloop()