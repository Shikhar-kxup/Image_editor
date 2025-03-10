import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from PIL import Image, ImageTk, ImageOps, ImageFilter, ImageEnhance

window = tk.Tk()
window.title('Image Editor')
window.geometry('900x500+330+150')
window.minsize(900, 500)

image_path = ''
output_path = ''
opened_img = edited_img = ''
image_id = ''
img_width = 0
img_height = 0
perc_zoom = ''
filter = 0
top_scale_value = tk.DoubleVar()
bottom_scale_value = tk.DoubleVar()
left_scale_value = tk.DoubleVar()
right_scale_value = tk.DoubleVar()

def select_file() -> None:
    global edited_img, image_path, img_width, img_height, perc_zoom
    filetypes = (('image files', '*.png ; *.jpg ; *.jpeg'),)
    image_path = fd.askopenfilename(title='Select an image', filetypes=filetypes)
    if image_path:
        original_img = Image.open(image_path)
        image_ratio = original_img.width / original_img.height
        img_height = int(disp_img_frame.winfo_height())
        img_width = int(img_height * image_ratio)
        perc_zoom = str(int(img_height / original_img.height * 100)) + '%'
        lb.configure(text = perc_zoom)
        edited_img = original_img.resize((img_width, img_height))
        display_image(edited_img)

def save_file() -> None:
    global output_path, edited_img
    if image_path:
        x1, y1, x2, y2 = canvas.bbox(image_id)
        edited_img = edited_img.crop((abs(x1), abs(y1), canvas.winfo_width(), canvas.winfo_height()))
        if output_path:
            edited_img.save(output_path)
        else:
            output_path = fd.asksaveasfilename(title = 'Save As', defaultextension = '.png',
                                             filetypes = (('.jpg','*.jpg'),('.jpeg','*.jpeg'),('.png','*.png')))
            if output_path:
                edited_img.save(output_path)

def display_image(img : Image) -> None:
    global opened_img, image_id
    opened_img = ImageTk.PhotoImage(img)
    w = min(disp_img_frame.winfo_width(), img.width)
    h = min(disp_img_frame.winfo_height(), img.height)
    canvas.config(width = w, height = h)
    image_id = canvas.create_image(0, 0, image = opened_img, anchor = 'nw')

def crop_image(left, top, right, bottom):
    global edited_img
    cropped_img = Image.open(image_path).resize((img_width, img_height))
    edited_img = cropped_img.crop((left, top, img_width - right, img_height - bottom))
    if filter != 0:
        apply_filter()
    else:
        display_image(edited_img)

def edit_controls(w, h):
    if opened_img:
        controls = tk.Toplevel()
        controls.geometry('400x300')
        controls.attributes('-topmost', 1)

        top_lb = ttk.Label(controls, text = 'Top')
        top_lb.pack(anchor = 'w')
        top_scale = ttk.Scale(controls, from_ = 0, to=h, orient = 'horizontal', variable = top_scale_value,
                              command = lambda x: crop_image(left_scale.get(),
                                                             top_scale.get(),
                                                             right_scale.get(),
                                                             bottom_scale.get()))
        top_scale.pack(anchor = 'w', fill = 'x')

        bottom_lb = ttk.Label(controls, text = 'Bottom')
        bottom_lb.pack(anchor = 'w')
        bottom_scale = ttk.Scale(controls, from_=0, to=h, orient='horizontal', variable = bottom_scale_value,
                                 command=lambda x: crop_image(left_scale.get(),
                                                              top_scale.get(),
                                                              right_scale.get(),
                                                              bottom_scale.get()))
        bottom_scale.pack(anchor='w', fill='x')

        left_lb = ttk.Label(controls, text = 'Left')
        left_lb.pack(anchor = 'w')
        left_scale = ttk.Scale(controls, from_=0, to=w, orient='horizontal', variable = left_scale_value,
                               command=lambda x: crop_image(left_scale.get(),
                                                            top_scale.get(),
                                                            right_scale.get(),
                                                            bottom_scale.get()))
        left_scale.pack(anchor='w', fill='x')

        right_lb = ttk.Label(controls, text = 'Right')
        right_lb.pack(anchor = 'w')
        right_scale = ttk.Scale(controls, from_=0, to=w, orient='horizontal', variable = right_scale_value,
                                command=lambda x: crop_image(left_scale.get(),
                                                             top_scale.get(),
                                                             right_scale.get(),
                                                             bottom_scale.get()))
        right_scale.pack(anchor='w', fill='x')

def convert_to_original():
    global filter, edited_img
    if opened_img:
        filter = 0
        crop_image(int(left_scale_value.get()), int(top_scale_value.get()), int(right_scale_value.get()), int(bottom_scale_value.get()))
        display_image(edited_img)

def convert_to_warm():
    global edited_img, filter
    if opened_img:
        convert_to_original()
        filter = 1
        img = edited_img.convert('RGB')
        r, g, b = img.split()
        r = r.point(lambda p: min(255, p * 1.2))
        g = g.point(lambda p: min(255, p * 1.1))
        b = b.point(lambda p: max(0, p * 0.9))
        edited_img = Image.merge('RGB', (r, g, b))
        edited_img = ImageEnhance.Brightness(edited_img).enhance(1.1)
        edited_img = ImageEnhance.Contrast(edited_img).enhance(1.2)
        display_image(edited_img)

def convert_to_greyscale():
    global edited_img, filter
    if opened_img:
        convert_to_original()
        filter = 2
        edited_img = edited_img.convert("L")
        display_image(edited_img)

def convert_to_nv():
    global edited_img, filter
    if opened_img:
        convert_to_original()
        filter = 3
        img = edited_img.convert('RGB')
        r, g, b = img.split()
        edited_img = Image.merge('RGB', (g, g.point(lambda x: min(255, x * 1.5)), g))
        display_image(edited_img)

def convert_to_bw():
    global edited_img, filter
    if opened_img:
        convert_to_original()
        filter = 4
        edited_img = edited_img.convert("L").point(lambda x: 255 if x > 128 else 0, mode = '1')
        display_image(edited_img)

def convert_to_invert():
    global edited_img, filter
    if opened_img:
        convert_to_original()
        filter = 5
        edited_img = ImageOps.invert(edited_img)
        display_image(edited_img)

def convert_to_blur():
    global edited_img, filter
    if opened_img:
        convert_to_original()
        filter = 6
        edited_img = edited_img.filter(ImageFilter.GaussianBlur(5))
        display_image(edited_img)

def apply_filter():
    if filter == 1:
        convert_to_warm()
    elif filter == 2:
        convert_to_greyscale()
    elif filter == 3:
        convert_to_nv()
    elif filter == 4:
        convert_to_bw()
    elif filter == 5:
        convert_to_invert()
    elif filter == 6:
        convert_to_blur()
    else:
        convert_to_original()

def zoom_in() -> None:
    global edited_img, img_width, img_height, perc_zoom
    if opened_img:
        img_width = int(img_width * 1.05)
        img_height = int(img_height * 1.05)
        img = Image.open(image_path)
        perc_zoom = str(int(img_height / img.height * 100)) + '%'
        lb.configure(text = perc_zoom)
        edited_img = img.resize((img_width, img_height))
        display_image(edited_img)

def zoom_out() -> None:
    global edited_img, img_width, img_height, perc_zoom
    if opened_img:
        img_width = int(img_width * 0.95)
        img_height = int(img_height * 0.95)
        img = Image.open(image_path)
        perc_zoom = str(int(img_height / img.height * 100)) + '%'
        lb.configure(text = perc_zoom)
        edited_img = img.resize((img_width, img_height))
        display_image(edited_img)

def move_image(event) -> None:
    global opened_img
    # if opened_img:

def clear() -> None:
    global image_path, edited_img, opened_img, img_width, img_height, perc_zoom, filter
    if opened_img:
        image_path = ''
        opened_img = edited_img = ''
        img_width = 0
        img_height = 0
        perc_zoom = ''
        filter = 0
        lb.configure(text = '')
        canvas.delete(image_id)

menu = tk.Menu()
file_menu = tk.Menu(menu, tearoff=0)
file_menu.add_command(label='Open...', command = select_file)
file_menu.add_command(label='Save', command = save_file)
file_menu.add_command(label='Save as copy', command = save_file)
file_menu.add_separator()
file_menu.add_command(label='Exit', command=window.quit)
edit_menu = tk.Menu(menu, tearoff=0)
edit_menu.add_command(label='Crop', command = lambda : edit_controls(w=img_width, h=img_height))
edit_menu.add_command(label='Adjustment')
filter_menu = tk.Menu(edit_menu, tearoff = 0)
filter_menu.add_command(label = 'Warm', command = convert_to_warm)
filter_menu.add_command(label = 'Greyscale', command = convert_to_greyscale)
filter_menu.add_command(label = 'Night Vision', command = convert_to_nv)
filter_menu.add_command(label = 'B&W', command = convert_to_bw)
filter_menu.add_command(label = 'Invert', command = convert_to_invert)
filter_menu.add_command(label = 'Blur', command = convert_to_blur)
filter_menu.add_command(label = 'None', command = convert_to_original)
edit_menu.add_cascade(label = 'Filters', menu = filter_menu)
edit_menu.add_command(label='Mark-up')
menu.add_cascade(label='File', menu=file_menu)
menu.add_cascade(label='Edit', menu=edit_menu)
menu.add_command(label = 'Undo')
menu.add_command(label = 'Redo')
menu.add_command(label = 'Clear', command = clear)
window.configure(menu = menu)

disp_img_frame = tk.Frame(window)
disp_img_frame.place(relx = 0.5, rely = 0.5, relwidth = 0.8, relheight = 0.8, anchor = 'center')

canvas = tk.Canvas(disp_img_frame)
canvas.place(relx = 0.5, rely = 0.5, anchor = 'center')

b2 = ttk.Button(window, text = 'Zoom out', command = zoom_out)
b2.pack(side = 'right', anchor = 'se')
b1 = ttk.Button(window, text = 'Zoom in', command = zoom_in)
b1.pack(side = 'right', anchor = 'se')
lb = ttk.Label(window, text = perc_zoom)
lb.pack(side = 'right', anchor = 'se', padx = 3, pady = 3)

canvas.bind('<B1-Motion>', move_image)

window.mainloop()