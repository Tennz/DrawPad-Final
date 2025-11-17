import tkinter as tk
from tkinter import colorchooser, filedialog

root = tk.Tk()
root.title("DrawPad")
root.geometry("1000x700")
root.config(bg="#333")

brush_color = "black"
brush_size = 5
eraser_size = 10
drawing = False
using_eraser = False
last_x, last_y = None, None
strokes = []
redo_strokes = []
current_stroke = []

zoom_level = 1.0
zoom_factor = 1.1

main_frame = tk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

canvas_frame = tk.Frame(main_frame)
canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

h_scroll = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
v_scroll = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
canvas = tk.Canvas(canvas_frame, bg="white", width=900, height=550,
                   xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
h_scroll.config(command=canvas.xview)
v_scroll.config(command=canvas.yview)
h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
canvas.pack(fill=tk.BOTH, expand=True)

cursor_circle = None

def draw_cursor_circle(event):
    global cursor_circle
    if cursor_circle:
        canvas.delete(cursor_circle)
    size = eraser_size if using_eraser else brush_size
    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    cursor_circle = canvas.create_oval(x - size/2, y - size/2, x + size/2, y + size/2, outline="gray")

def start_draw(event):
    global drawing, last_x, last_y, current_stroke
    drawing = True
    last_x, last_y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    current_stroke = []

def draw(event):
    global last_x, last_y
    x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
    if drawing:
        size = eraser_size if using_eraser else brush_size
        color = canvas["bg"] if using_eraser else brush_color
        line = canvas.create_line(last_x, last_y, x, y, width=size, fill=color,
                                  capstyle=tk.ROUND, smooth=True)
        current_stroke.append((line, color, size))
        last_x, last_y = x, y
    draw_cursor_circle(event)

def stop_draw(event):
    global drawing, strokes, redo_strokes, current_stroke
    if drawing:
        drawing = False
        if current_stroke:
            strokes.append(current_stroke)
            current_stroke = []
        redo_strokes.clear()

def undo():
    global strokes, redo_strokes
    if strokes:
        stroke = strokes.pop()
        for obj, _, _ in stroke:
            canvas.delete(obj)
        redo_strokes.append(stroke)

def redo():
    global strokes, redo_strokes
    if redo_strokes:
        stroke = redo_strokes.pop()
        new_objs = []
        for _, color, size in stroke:
            coords = canvas.coords(_)
            new_obj = canvas.create_line(*coords, width=size, fill=color, capstyle=tk.ROUND, smooth=True)
            new_objs.append((new_obj, color, size))
        strokes.append(new_objs)

def set_color():
    global brush_color, using_eraser
    using_eraser = False
    color = colorchooser.askcolor()[1]
    if color:
        brush_color = color

def use_eraser():
    global using_eraser
    using_eraser = True

def set_brush_size(val):
    global brush_size
    brush_size = int(val)

def set_eraser_size(val):
    global eraser_size
    eraser_size = int(val)

def clear_canvas():
    global strokes, redo_strokes
    for stroke in strokes:
        for obj, _, _ in stroke:
            canvas.delete(obj)
    strokes.clear()
    redo_strokes.clear()

def save_canvas():
    file = filedialog.asksaveasfilename(defaultextension=".ps",
                                        filetypes=[("PostScript files", "*.ps")])
    if file:
        canvas.postscript(file=file, colormode='color')

def zoom(event):
    global zoom_level
    if event.state & 0x0004:  # Ctrl key pressed
        scale = zoom_factor if event.delta > 0 else 1 / zoom_factor
        zoom_level *= scale
        canvas.scale("all", canvas.canvasx(event.x), canvas.canvasy(event.y), scale, scale)
        canvas.configure(scrollregion=canvas.bbox("all"))

toolbar = tk.Frame(root, bg="#333")
toolbar.pack(pady=5)

tk.Button(toolbar, text="Color", command=set_color, width=10).grid(row=0, column=0, padx=5)
tk.Button(toolbar, text="Eraser", command=use_eraser, width=10).grid(row=0, column=1, padx=5)
tk.Button(toolbar, text="Undo", command=undo, width=10).grid(row=0, column=2, padx=5)
tk.Button(toolbar, text="Redo", command=redo, width=10).grid(row=0, column=3, padx=5)
tk.Button(toolbar, text="Clear", command=clear_canvas, width=10).grid(row=0, column=4, padx=5)
tk.Button(toolbar, text="Save", command=save_canvas, width=10).grid(row=0, column=5, padx=5)

tk.Label(toolbar, text="Brush Size", bg="#333", fg="white").grid(row=0, column=6, padx=2)
brush_slider = tk.Scale(toolbar, from_=1, to=20, orient=tk.HORIZONTAL, command=set_brush_size,
                        bg="#333", fg="white", troughcolor="white")
brush_slider.set(5)
brush_slider.grid(row=0, column=7, padx=5)

tk.Label(toolbar, text="Eraser Size", bg="#333", fg="white").grid(row=0, column=8, padx=2)
eraser_slider = tk.Scale(toolbar, from_=1, to=50, orient=tk.HORIZONTAL, command=set_eraser_size,
                         bg="#333", fg="white", troughcolor="white")
eraser_slider.set(10)
eraser_slider.grid(row=0, column=9, padx=5)

canvas.bind("<Button-1>", start_draw)
canvas.bind("<B1-Motion>", draw)
canvas.bind("<ButtonRelease-1>", stop_draw)
canvas.bind("<Motion>", draw_cursor_circle)
canvas.bind_all("<MouseWheel>", zoom)

root.mainloop()
