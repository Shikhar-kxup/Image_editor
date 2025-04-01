import tkinter as tk
from tkinter import ttk, PhotoImage
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
crop_active = False
crop_rect = None
rect_coords = None
dragging = None
offset_x = 0
offset_y = 0
a = b = c = d = 0

undo_stack = []
redo_stack = []

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
        undo_stack.append(edited_img)
        display_image()

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

def display_image() -> None:
    global opened_img, image_id
    opened_img = ImageTk.PhotoImage(edited_img)
    canvas.delete('all')
    w = min(disp_img_frame.winfo_width(), edited_img.width)
    h = min(disp_img_frame.winfo_height(), edited_img.height)
    canvas.config(width = w, height = h)
    image_id = canvas.create_image(w / 2, h / 2, image = opened_img, anchor = 'center')

def enable_crop_mode():
    global crop_active, rect_coords
    if edited_img:
        crop_active = True
        rect_coords = (3, 3, canvas.winfo_width() - 4, canvas.winfo_height() - 4)
        draw_crop_rectangle()
        crop_btn.place(relx=0.5, rely=0.95, anchor='center')

def draw_crop_rectangle():
    global crop_rect
    if crop_active and edited_img:
        x1, y1, x2, y2 = rect_coords
        canvas.delete("crop_rect")  # Remove old rectangle
        crop_rect = canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2, tags="crop_rect")

def on_press(event):
    global dragging, offset_x, offset_y
    if not crop_active:
        return

    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    x1, y1, x2, y2 = rect_coords
    margin = 10

    if x1 - margin < x < x1 + margin and y1 - margin < y < y1 + margin:
        dragging = "topleft"
    elif x2 - margin < x < x2 + margin and y1 - margin < y < y1 + margin:
        dragging = "topright"
    elif x1 - margin < x < x1 + margin and y2 - margin < y < y2 + margin:
        dragging = "bottomleft"
    elif x2 - margin < x < x2 + margin and y2 - margin < y < y2 + margin:
        dragging = "bottomright"
    elif x1 < x < x2 and y1 < y < y2:
        dragging = "move"
        offset_x = x - x1
        offset_y = y - y1
    else:
        dragging = None

def on_drag(event):
    global rect_coords
    if not crop_active or not dragging:
        return

    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    x1, y1, x2, y2 = rect_coords

    if dragging == "topleft":
        rect_coords = (min(max(x,3), x2-50), min(max(y,3), y2-50), x2, y2)
    elif dragging == "topright":
        rect_coords = (x1, min(max(y,3), y2-50), max(min(x, canvas.winfo_width()-4), x1+50), y2)
    elif dragging == "bottomleft":
        rect_coords = (min(max(x,3), x2-50), y1, x2, max(min(y, canvas.winfo_height()-4), y1+50))
    elif dragging == "bottomright":
        rect_coords = (x1, y1, max(min(x, canvas.winfo_width()-4), x1+50), max(min(y, canvas.winfo_height()-4), y1+50))
    elif dragging == "move":
        dx, dy = x - offset_x, y - offset_y
        width, height = x2 - x1, y2 - y1
        rect_coords = (min(max(3, dx), canvas.winfo_width() - width - 4),
                       min(max(3, dy), canvas.winfo_height() - height - 4),
                       min(max(3 + width, dx + width), canvas.winfo_width() - 4),
                       min(max(3 + height, dy + height), canvas.winfo_height() - 4))

    draw_crop_rectangle()

def on_release(event):
    global dragging
    dragging = None

def crop_image():
    global edited_img, crop_active, a, b, c, d
    if edited_img:
        x1, y1, x2, y2 = map(int, rect_coords)
        a += (x1 - 3)
        b += (y1 - 3)
        c = a + x2 - x1 + 3
        d = b + y2 - y1 + 3
        edited_img = edited_img.crop((x1-3, y1-3, x2, y2))
        crop_active = False
        undo_stack.append(edited_img)
        if len(redo_stack):
            redo_stack.clear()
        display_image()
        crop_btn.place_forget()

def convert_to_original():
    global filter, edited_img
    if opened_img:
        filter = 0
        edited_img = Image.open(image_path).resize((img_width, img_height))
        if rect_coords:
            edited_img = edited_img.crop((a, b, c, d))
        undo_stack.append(edited_img)
        if len(redo_stack):
            redo_stack.clear()
        display_image()

def convert_to_warm():
    global edited_img, filter
    if opened_img:
        edited_img = Image.open(image_path).resize((img_width, img_height))
        if rect_coords:
            edited_img = edited_img.crop((a, b, c, d))
        filter = 1
        img = edited_img.convert('RGB')
        r, g, bl = img.split()
        r = r.point(lambda p: min(255, p * 1.2))
        g = g.point(lambda p: min(255, p * 1.1))
        bl = bl.point(lambda p: max(0, p * 0.9))
        edited_img = Image.merge('RGB', (r, g, bl))
        edited_img = ImageEnhance.Brightness(edited_img).enhance(1.1)
        edited_img = ImageEnhance.Contrast(edited_img).enhance(1.2)
        undo_stack.append(edited_img)
        if len(redo_stack):
            redo_stack.clear()
        display_image()

def convert_to_greyscale():
    global edited_img, filter
    if opened_img:
        edited_img = Image.open(image_path).resize((img_width, img_height))
        if rect_coords:
            edited_img = edited_img.crop((a, b, c, d))
        filter = 2
        edited_img = edited_img.convert("L")
        undo_stack.append(edited_img)
        if len(redo_stack):
            redo_stack.clear()
        display_image()

def convert_to_nv():
    global edited_img, filter
    if opened_img:
        edited_img = Image.open(image_path).resize((img_width, img_height))
        if rect_coords:
            edited_img = edited_img.crop((a, b, c, d))
        filter = 3
        img = edited_img.convert('RGB')
        r, g, bl = img.split()
        edited_img = Image.merge('RGB', (g, g.point(lambda x: min(255, x * 1.5)), g))
        undo_stack.append(edited_img)
        if len(redo_stack):
            redo_stack.clear()
        display_image()

def convert_to_bw():
    global edited_img, filter
    if opened_img:
        edited_img = Image.open(image_path).resize((img_width, img_height))
        if rect_coords:
            edited_img = edited_img.crop((a, b, c, d))
        filter = 4
        edited_img = edited_img.convert("L").point(lambda x: 255 if x > 128 else 0, mode = '1')
        undo_stack.append(edited_img)
        if len(redo_stack):
            redo_stack.clear()
        display_image()

def convert_to_invert():
    global edited_img, filter
    if opened_img:
        edited_img = Image.open(image_path).resize((img_width, img_height))
        if rect_coords:
            edited_img = edited_img.crop((a, b, c, d))
        filter = 5
        edited_img = ImageOps.invert(edited_img)
        undo_stack.append(edited_img)
        if len(redo_stack):
            redo_stack.clear()
        display_image()

def convert_to_blur():
    global edited_img, filter
    if opened_img:
        edited_img = Image.open(image_path).resize((img_width, img_height))
        if rect_coords:
            edited_img = edited_img.crop((a, b, c, d))
        filter = 6
        edited_img = edited_img.filter(ImageFilter.GaussianBlur(5))
        undo_stack.append(edited_img)
        if len(redo_stack):
            redo_stack.clear()
        display_image()

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
        if filter != 0:
            apply_filter()
        else:
            display_image()

def zoom_out() -> None:
    global edited_img, img_width, img_height, perc_zoom
    if opened_img:
        img_width = int(img_width * 0.95)
        img_height = int(img_height * 0.95)
        img = Image.open(image_path)
        perc_zoom = str(int(img_height / img.height * 100)) + '%'
        lb.configure(text = perc_zoom)
        edited_img = img.resize((img_width, img_height))
        if filter != 0:
            apply_filter()
        else:
            display_image()

def undo() -> None:
    global edited_img
    if len(undo_stack) > 1:
        redo_stack.append(undo_stack.pop())
        edited_img = undo_stack[-1]
        display_image()

def redo() -> None:
    global edited_img
    if len(redo_stack):
        undo_stack.append(redo_stack.pop())
        edited_img = undo_stack[-1]
        display_image()

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
edit_menu.add_command(label='Crop', command = enable_crop_mode)
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
menu.add_command(label = 'Undo', command = undo)
menu.add_command(label = 'Redo', command = redo)
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

crop_btn = tk.Button(window, text="Crop", command=crop_image)
crop_btn.place(relx=0.5, rely=0.95, anchor='center')
crop_btn.place_forget()

canvas.bind('<ButtonPress-1>', on_press)
canvas.bind('<B1-Motion>', on_drag)
canvas.bind('<ButtonRelease-1>', on_release)

window.mainloop()