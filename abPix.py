import os
from tkinter import *
from tkinter import filedialog, messagebox
import png

class g:
    root = Tk()
    root.title('abPix')
    if os.name == 'nt': root.state('zoomed')

    hx = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f')
    hxrev = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'a':10, 'b':11, 'c':12, 'd':13, 'e':14, 'f':15}
    color = '#000'
    img, imgmap, log = [], [], []
    colorpick_state = scale = makenew_active = left_panel_indent = move_x = move_y = move_posx = move_posy = 0
    saved = 1
    current_file = 0
    swidth, sheight = root.winfo_screenwidth(), root.winfo_screenheight()-20
    palette_section_indent, palette_section_size, blend_section_size = sheight // 21, sheight//21 - 5, sheight // 14 - 5
    right_panel_x, left_panel_x = swidth - sheight//3, swidth // 15
    right_panel_mid_x = swidth - sheight//6
    click_canvas, release_canvas, click_canvas_secondary = lambda x, y: (), lambda x, y: (), lambda x, y: ()
    
    c = Canvas(width = swidth, height = sheight, highlightthickness = 0, bg = '#000')
    c.pack()

def rect(x, y, nx, ny, fill): return g.c.create_rectangle(x, y, nx, ny, fill = fill)
def ret_color(x, y): return '#'+g.hx[(y*4-1)*(x < 2 or x > 4)*(y>0)]+g.hx[(y*4-1)*((x > 0 and x < 4)or x>5)*(y>0)]+g.hx[(y*4-1)*(x > 2 and x < 7)*(y>0)]

def make_palette():
    for i in g.rect_buffer: g.c.delete(i)
    prev_cpx = cpx = g.swidth-g.sheight//3+5
    cpy = g.palette_section_indent
    for j in range(5):
        for i in range(7):
            g.rect_buffer.append(rect(cpx, cpy, cpx+g.palette_section_size, cpy+g.palette_section_size, ret_color(i, j)))
            cpx += g.palette_section_indent
        cpx = prev_cpx
        cpy += g.palette_section_size
def click_palette(x, y):
    if y > g.palette_section_size and y < g.palette_section_size*6:
        posx, posy = (x-g.right_panel_x)//g.palette_section_indent, y//g.palette_section_size-1
        x, y = posx*g.palette_section_indent+g.right_panel_x, posy*g.palette_section_size+g.palette_section_indent
        for i in g.color_select_rect: g.c.delete(i)
        g.color, g.color_select_rect = ret_color(posx, posy), [rect(x, y, x+5, y+g.palette_section_size, '#ff0')]
def select_palette(): 
    g.colorpick_state = 0
    g.c.delete(g.colormode_select_rect)
    g.colormode_select_rect = rect(g.right_panel_x+5, 0, g.right_panel_x+15, g.palette_section_size, '#ff0')
    for i in g.color_select_rect: g.c.delete(i)
    g.color_select_rect = [rect(g.right_panel_x, g.palette_section_size, g.right_panel_x + 5, g.palette_section_size*2, '#ff0')]
    make_palette()
        
def make_blend():
    for i in g.rect_buffer: g.c.delete(i)
    cpx = g.swidth-g.sheight//3+5
    cpy = prev_cpy = g.palette_section_size
    for j in range(3):
        for i in range(5):
            g.rect_buffer.append(rect(cpx, cpy, cpx+g.blend_section_size*1.5, cpy+g.blend_section_size, ret_color(j*2, i)))
            cpy += g.blend_section_size
        cpy = prev_cpy
        cpx += g.blend_section_size*1.75
def click_blend(x, y):
    if y > g.blend_section_size and y < g.blend_section_size*6:
        posx, posy = int((x-g.right_panel_x)//(g.blend_section_size*1.75)), y//g.blend_section_size-1
        x, y = posx*(g.blend_section_size*1.75)+g.right_panel_x, posy*g.blend_section_size+g.palette_section_size
        g.c.delete(g.color_select_rect[posx])
        g.color_select_rect[posx] = rect(x, y, x+5, y+g.blend_section_size, '#ff0')
        g.color, colorset = '#', [g.color[1], g.color[2], g.color[3]]
        colorset[posx] = ret_color(posx*2, posy)[posx+1]
        for i in colorset: g.color += i
def select_blend():
    g.colorpick_state = 1
    g.c.delete(g.colormode_select_rect)
    g.colormode_select_rect = rect(g.right_panel_mid_x+5, 0, g.right_panel_mid_x+15, g.palette_section_size, '#ff0')
    for i in g.color_select_rect: g.c.delete(i)
    blend_x0, blend_x1, blend_x2 = g.right_panel_x, g.right_panel_x+g.blend_section_size*1.75, g.right_panel_x+g.blend_section_size*3.5
    g.color_select_rect = [rect(blend_x0, g.palette_section_size, blend_x0+5, g.palette_section_size+g.blend_section_size, '#ff0'), rect(blend_x1, g.palette_section_size, blend_x1+5, g.palette_section_size+g.blend_section_size, '#ff0'), rect(blend_x2, g.palette_section_size, blend_x2+5, g.palette_section_size+g.blend_section_size, '#ff0')]
    make_blend()

def left_selector(pos):
    g.c.delete(g.mode_select_rect)
    g.mode_select_rect = rect(g.left_panel_x-5, g.sheight//20*pos, g.left_panel_x, g.sheight//20*(pos+1), '#ff0')

def make_new(): 
    def new_project():
        try:
            wd, hg = int(width_entry.get()), int(height_entry.get())
            if wd // 255 or hg // 255: raise
            build_canvas(wd, hg)
            close_makenew()    
        except: messagebox.showinfo('abPix error', 'Error. Please check that width and height is numbers, less than 255')
    def close_makenew():
        g.makenew_active = 0
        makenew.destroy()

    if g.makenew_active: return messagebox.showinfo('abPix error', 'New project creation window is already open')
    if not g.saved:
        proceed = messagebox.askokcancel('Unsaved file', 'Your current project is unsaved, proceed?')
        if not proceed: return
    makenew = Tk()
    makenew.title('New abPix project')
    makenew.config(bg = '#333')
    makenew.geometry('400x300')
    makenew.protocol('WM_DELETE_WINDOW', lambda: close_makenew())
    width, height = StringVar(), StringVar()
    Label(makenew, text = 'New project', bg = '#333', fg = '#ddd').pack()
    Label(makenew, text = 'Width:', bg = '#333', fg = '#ddd').pack()
    width_entry = Entry(makenew, textvariable = width, bg = '#222', fg = '#ddd')
    width_entry.pack()
    Label(makenew, text = 'Height:', bg = '#333', fg = '#ddd').pack()
    height_entry = Entry(makenew, textvariable = height, bg = '#222', fg = '#ddd')
    height_entry.pack()
    Button(makenew, text = 'Ok', command = lambda: new_project(), bd = 4, bg = '#333', fg = '#ddd', activebackground = '#666').pack()
    Button(makenew, text = 'Cancel', command = lambda: close_makenew(), bd = 4, bg = '#333', fg = '#ddd', activebackground = '#666').pack()
    g.makenew_active = 1
    makenew.mainloop()
    
def make_open():
    if not g.saved:
        proceed = messagebox.askokcancel('Unsaved file', 'Your current project is unsaved, proceed?')
        if not proceed: return
    fname = filedialog.askopenfile(title = 'Load project',filetypes=[("abPix Project File", "*.abpix")])
    if not fname: return
    try: exec(open(fname.name).read())
    except: return messagebox.showinfo('abPix error', 'abPix can load only .abpix files')
    g.move_x = g.move_y = 0
    g.log = []
    g.saved = 1
    click_scale(0)
def make_save():
    fname = filedialog.asksaveasfilename(title = 'Save project',filetypes=[("abPix Project File", "*.abpix")])
    if not fname: return
    testname = fname + ' '
    if testname[-7:-1] != '.abpix': fname += '.abpix'
    f = open(fname, 'w')
    f.write('build_canvas('+str(len(g.imgmap[0]))+', '+str(len(g.imgmap))+')\ng.imgmap = '+str(g.imgmap))
    f.close()
    if not g.saved: g.saved = 1 
def make_export():
    fname = filedialog.asksaveasfilename(title = 'Export As PNG',filetypes=[("PNG Image", "*.png")])
    testname = fname + ' '
    if testname[-5:-1] != '.png': fname += '.png'
    towrite = []
    for i in range(len(g.imgmap)):
        towrite.append([])
        for j in g.imgmap[i]:
            v1, v2, v3 = g.hxrev[j[1]], g.hxrev[j[2]], g.hxrev[j[3]]
            v1, v2, v3 = v1*v1, v2*v2, v3*v3
            if j: towrite[i] += [v1, v2, v3, 255]
            else: towrite[i] += [0, 0, 0, 0]
    png.Writer(width = len(g.imgmap[0]), height = len(g.imgmap), alpha = True, greyscale = False).write(open(fname, 'wb'), towrite)

def make_draw():
    left_selector(5)
    g.click_canvas = lambda x, y: click_draw(x, y)
    g.click_canvas_secondary = lambda x, y: click_draw(x, y, mode = 0)
    g.release_canvas = lambda x, y: ()
def click_draw(x, y, mode = 1):
    if g.saved: g.saved = 0
    coord_x = (x-g.left_panel_x) // g.scale * g.scale - 1 + g.left_panel_x
    coord_y = y // g.scale * g.scale
    point_x = (x-g.left_panel_x)//g.scale-g.move_x
    point_y = y//g.scale-g.move_y
    g.log.append((point_x, point_y, g.imgmap[point_y][point_x]))
    if mode: g.imgmap[point_y][point_x] = g.color
    else: g.imgmap[point_y][point_x] = 0
    g.c.delete(g.img[point_y][point_x])
    if mode: g.img[point_y][point_x] = g.c.create_rectangle(coord_x, coord_y, coord_x+g.scale, coord_y+g.scale, fill=g.imgmap[point_y][point_x])
    else: g.img[point_y][point_x] = g.c.create_rectangle(coord_x, coord_y, coord_x+g.scale, coord_y+g.scale, fill='#fff')
    
def make_scale(): 
    left_selector(6)
    g.click_canvas = lambda x, y: click_scale(5)
    g.click_canvas_secondary = lambda x, y: click_scale(-5)
    g.release_canvas = lambda x, y: ()
    
def click_scale(scale_val):
    g.scale += scale_val*(not ((g.scale < 10) and (scale_val < 0)))
    posx = prev_posx = g.move_x*g.scale+g.left_panel_x
    posy = g.move_y*g.scale
    for i in range(len(g.img)):
        for j in g.img[i]: g.c.delete(j)
    for i in range(len(g.imgmap)):
        for j in range(len(g.imgmap[i])): 
            if posx+g.scale < g.right_panel_x and posx > g.left_panel_x-1 and posy < g.sheight and posy > -1:
                if g.imgmap[i][j]: g.img[i].append(rect(posx, posy, posx+g.scale, posy+g.scale, fill = g.imgmap[i][j]))
                else: g.img[i].append(rect(posx, posy, posx+g.scale, posy+g.scale, fill = '#fff'))
            posx += g.scale
        posx = prev_posx
        posy += g.scale
    
def make_move():
    left_selector(7)
    g.click_canvas = lambda x, y: click_move_press(x, y)
    g.release_canvas = lambda x, y: click_move_release(x, y)
    g.click_canvas_secondary = lambda x, y: ()
def click_move_press(x, y): g.dyn_start_x, g.dyn_start_y = x, y
def click_move_release(x, y):
    g.move_x += (x - g.dyn_start_x) // g.scale
    g.move_y += (y - g.dyn_start_y) // g.scale
    click_scale(0)

def make_undo():
    g.imgmap[g.log[-1][1]][g.log[-1][0]] = g.log[-1][2]
    g.log.pop()
    click_scale(0)
    
def click_right_panel(x, y):
    if g.colorpick_state: click_blend(x, y)
    else: click_palette(x, y)

def build_canvas(x, y):
    for i in range(len(g.img)):
        for j in g.img[i]: g.c.delete(j)
    g.scale = min([(g.swidth - g.left_panel_x - (g.swidth-g.right_panel_x)) // x, g.sheight // y])
    g.move_x = g.move_y = 0
    g.img, g.imgmap = [], []
    for i in range(y):
        g.img.append([])
        g.imgmap.append([])
        for j in range(x): g.imgmap[i].append(0)
    click_scale(0)
    make_draw()

def click_main(x, y):
    if x > g.left_panel_x and x < g.right_panel_x: g.click_canvas(x, y)
    elif x > g.right_panel_x: click_right_panel(x, y)
def click_release(x, y):
    if x > g.left_panel_x and x < g.right_panel_x: g.release_canvas(x, y)
def click_secondary(x, y):
    if x > g.left_panel_x and x < g.right_panel_x: g.click_canvas_secondary(x, y)
    elif x > g.right_panel_x: click_right_panel(x, y)

def click_hotkey(key, mod):
    if (mod & 0x4) or mod == 4:
        if key == 39 or key == 83: make_save()
        elif key == 52 or key == 90: make_undo()
        elif key == 32 or key == 79: make_open()
        elif key == 26 or key == 69: make_export()
    if key == 20 or key == 189: click_scale(-5)
    elif key == 21 or key == 187: click_scale(5)
    elif key == 111 or key == 37: g.move_y += 1; click_scale(0)
    elif key == 113 or key == 38: g.move_x += 1; click_scale(0)
    elif key == 116 or key == 40: g.move_y -= 1; click_scale(0)
    elif key == 114 or key == 39: g.move_x -= 1; click_scale(0)

def init_abpix():
    rect(0, 0, g.swidth // 15, g.sheight, '#222')
    rect(g.swidth, g.sheight, g.swidth-g.sheight // 3, 0, '#222')   
    g.rect_buffer = []
    g.color_select_rect = []
    g.colormode_select_rect = rect(g.right_panel_x + 5, 0, g.right_panel_x + 15, g.palette_section_size, '#ff0')
    g.mode_select_rect = rect(g.left_panel_x - 5, g.sheight // 20 * 5, g.left_panel_x, g.sheight //20 * 6, '#ff0')
    buttons = ((lambda: make_new(), 'New'),(lambda: make_open(), 'Open'),(lambda: make_save(), 'Save'),(lambda: make_export(), 'Export'),(lambda: make_draw(), 'Draw'),(lambda: make_scale(),  'Scale'),(lambda: make_move(), 'Move'),(lambda: make_undo(), 'Undo'))
    for i in range(len(buttons)): Button(text = buttons[i][1], bd = 4, bg = '#333', fg = '#ddd', activebackground = '#666', command = buttons[i][0]).place(x = 0, y = g.sheight // 20 *(i + (i > 3)), width = g.swidth // 15 - 5, height = g.sheight // 20)

    Button(text = 'Palette', bd = 4, bg = '#333', fg = '#ddd', activebackground = '#666', command = lambda: select_palette()).place(x = g.swidth - g.sheight//3+10, y = 0, width = g.sheight//6 - 10, height = g.palette_section_size)
    Button(text = 'Blend', bd = 4, bg = '#333', fg = '#ddd', activebackground = '#666', command = lambda: select_blend()).place(x = g.swidth - g.sheight//6+10, y = 0, width = g.sheight//6 - 10, height = g.palette_section_size)
    make_palette()
    
    g.root.bind('<ButtonPress-1>', lambda event: click_main(event.x, event.y))
    g.root.bind('<ButtonRelease-1>', lambda event: click_release(event.x, event.y))
    g.root.bind('<Button-3>', lambda event: click_secondary(event.x, event.y))

    g.root.bind('<ButtonPress-2>', lambda event: click_move_press(event.x, event.y))
    g.root.bind('<ButtonRelease-2>', lambda event: click_move_release(event.x, event.y))
    g.root.bind('<KeyPress>', lambda event: click_hotkey(event.keycode, event.state))

    build_canvas(16, 16)
    
    g.root.mainloop()

init_abpix()
