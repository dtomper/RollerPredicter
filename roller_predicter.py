import matplotlib.pyplot as plt
from PIL import ImageTk, Image
from datetime import datetime
from time import sleep
import multiprocessing
import tkinter as tk
import mplcursors
import pyglet
import ctypes

# Configure Matplotlib
mpl_background_color = "#181928"
mpl_text_color = "white"

plt.rcParams['axes.facecolor'] = mpl_background_color
plt.rcParams['figure.facecolor'] = mpl_background_color

plt.rcParams['text.color'] = mpl_text_color
plt.rcParams['axes.labelcolor'] = mpl_text_color
plt.rcParams['xtick.color'] = mpl_text_color
plt.rcParams['ytick.color'] = mpl_text_color
plt.rcParams['axes.edgecolor'] = mpl_text_color

# Initialize some stuff that child processes won't need
# Colors
bg = "#181928"
light_blue = "#03e1e4"
gold_yellow = "#ffdc00"
light_green = "#2bd600"
default_sep_color = "#353542"
entry_color = "#1f1f2d"
entry_highlight_color = "#353542"
entry_border_color = "#6a668a"
entry_dropdown_border_color = "#02b4b6"
miners_container_frame_bg = "#161724"
miners_container_frame_border_color = "#55526e"
miners_container_frame_scrollbar_color = "#454550"
miner_frame_hover_color = "#2d2e3a"
miner_frame_selection_color = "#014344"

# Constants
power_units = ["Gh/s", "Th/s", "Ph/s", "Eh/s"]

pyglet.font.add_file("assets/Fonts/PixelOperatorSC.ttf")
roller_font_name = "Pixel Operator SC"

if __name__ == "__main__":
    window = tk.Tk()

    window_width, window_height = 600, 850
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    win_x = int((screen_width - window_width)/2)
    win_y = int((screen_height - window_height)/2)

    window.title("Roller Predicter")
    window.iconbitmap("assets/Icon/icon.ico")
    window.geometry(f"{window_width}x{window_height}+{win_x}+{win_y}")
    window.resizable(0, 0)

    window.configure(bg=bg)

    item_clicked = False
    def focus_event(event):
        global item_clicked
        if item_clicked:
            item_clicked = False
            return
        event.widget.focus_set()
            
    window.bind_all("<Button-1>", focus_event)

else:
    window = None # So that child processes don't throw NameErrors (not defined)


# Tkinter Classes
class ScrollableFrame(tk.Frame):
    def __init__(self, master, root, width, height, scrollbar_color = miners_container_frame_scrollbar_color,
                 scrollbar_hover_color = entry_dropdown_border_color, border_size = None,
                 border_color = None, scroll_jump_size = 20, *args, **kwargs):
        self.root = root
        self.scrollbar_color = scrollbar_color
        self.scrollbar_hover_color = scrollbar_hover_color
        self.scroll_jump_size = scroll_jump_size

        # Trick the user into thinking this outer_frame the actual frame,
        # when in reality it's the container.
        self.border_frame = None
        if border_size and border_color:
            # Add another frame for border, because the default borders are fucked up
            # at the bottom. When its inner frame gets bigger than it, the bottom border
            # stops showing.
            self.border_frame = tk.Frame(master,
                                         width = width + border_size,
                                         height = height + border_size,
                                         bg = border_color)
            self.border_frame.propagate(0)
            self.outer_frame = tk.Frame(self.border_frame, width = width, height = height, *args, **kwargs)
            self.outer_frame.place(anchor = tk.CENTER, relx = 0.5, rely = 0.5)
        else:
            self.outer_frame = tk.Frame(master, width = width, height = height, *args, **kwargs)
        
        self.outer_frame.propagate(0)
        master.update()

        self.outer_frame.bind_all("<MouseWheel>", self.on_mousewheel, add = "+")

        # Initialize the frame that'll hold the inner widgets, this frame is self.
        # I'll refer to this frame as super() because sometimes I override the methods
        # of this class so I use the overrided method instead of the original one
        super().__init__(self.outer_frame, width = width, bg = self.outer_frame.cget("bg"))
        # super().bind("<Configure>", self.update_scrollbar) # Don't use this with manual_height_update
        super().place(anchor = tk.NW, x = 0, y = 0)

        # self.outer_frame.bind_all("<MouseWheel>", self.on_mousewheel)

        self.scrollbar_width = 10

        self.scrollbar_hidden = True
        self.scrollbar = tk.Frame(self.outer_frame, bg = scrollbar_color, width = self.scrollbar_width, height = height)        
        self.scrollbar.bind("<ButtonPress-1>", self.on_scrollbar_mouse_down)
        self.scrollbar.bind("<ButtonRelease-1>", self.on_scrollbar_mouse_up)
        self.scrollbar.bind("<Enter>", self.on_scrollbar_enter)
        self.scrollbar.bind("<Leave>", self.on_scrollbar_leave)

        self.scrollbar_y_pad = 5
        self.scrollbar_x_right_pad = 5

        self.root_motion_funcid = None
        self.starting_y = None

        self.scrollable = False
        self.scrolling = False

    def set_scrollbar_percentage(self, scrollbar_percentage):
        if not self.scrollable:
            return
        self.update_scrollbar_position(scrollbar_percentage)
        self.update_inner_frame_position(scrollbar_percentage)

    def update_scrollbar_height(self):
        # Updates the height of the scrollbar depending on the size of the
        # inner frame when compared with the outer frame
        self.master.update()

        outer_width = self.outer_frame.winfo_height()
        inner_width = super().winfo_height()

        new_height_ratio = outer_width / inner_width
        if new_height_ratio >= 1:
            self.scrollable = False

            if not self.scrollbar_hidden:
                # Hide scrollbar
                self.scrollbar.place_forget()
                self.scrollbar_hidden = True
            return

        self.scrollable = True

        if self.scrollbar_hidden:
            # Show scrollbar
            self.scrollbar.place(anchor = tk.NE, relx = 1, rely = 0)
            self.scrollbar_hidden = False

        new_height = new_height_ratio * outer_width

        # Set scrollbar's height
        self.scrollbar.configure(height = new_height)

    def manual_height_update(self, reset_y = False):
        empty_label = tk.Frame(self, width=1, height=1, borderwidth=0, highlightthickness=0)

        # Call grid on empty_label to update height of its parent frame (self)
        empty_label.grid(row = 1000, column = 1000)
        self.master.update_idletasks()

        # Destroy label
        empty_label.destroy()

        # Update the height of the scrollbar
        self.update_scrollbar_height()

        # Reset Y coordinate to 0
        if reset_y:
            if self.scrollable:
                self.update_scrollbar_position(0)
            self.update_inner_frame_position(0)

        # Otherwise update its position accordingly
        elif self.scrollable:
            self.update_scrollbar_position()

    def on_scrollbar_mouse_down(self, event):
        self.scrolling = True
        self.scrollbar.configure(bg = self.scrollbar_hover_color)
        self.root_motion_funcid = self.root.bind("<Motion>", self.on_root_motion, add = "+")
        self.starting_y = event.y
    
    def on_scrollbar_mouse_up(self, event):
        self.scrolling = False
        # self.scrollbar.configure(bg = self.scrollbar_color)
        if self.root_motion_funcid:
            self.root.unbind("<Motion>", self.root_motion_funcid)

    def on_mousewheel(self, event):
        if not self.scrollable:
            return

        temp = event.widget
        while temp != self.root:
            if temp == self.outer_frame:
                break
            temp = temp.master
        else:
            # temp was never equal to self.outer_frame, which means
            # event.widget is not a child (or grandgrand...child) of self.outer_frame
            return
        
        # Move inner_frame vertically
        current_y = super().winfo_y()
        new_y = current_y + self.scroll_jump_size * (event.delta / abs(event.delta))

        outer_frame = self.outer_frame.winfo_height()
        inner_height = super().winfo_height()

        max_value = 0
        min_value = outer_frame - inner_height

        if new_y < min_value: new_y = min_value
        if new_y > max_value: new_y = max_value

        super().place(anchor = tk.NW, relx = 0, y = new_y)
        scroll_percentage = new_y / (outer_frame - inner_height)
        self.update_scrollbar_position(scroll_percentage)

    def on_root_motion(self, event):
        # For some reason, event.y if `y of mouse` - `y of scrollbar` (Top of scrollbar)
        # In other words, event.y is the y coordinate of the mouse inside the scrollbar
        # even though this event is binded to self.root :/
        
        current_y = self.scrollbar.winfo_y()
        new_y = current_y + (event.y - self.starting_y)

        outer_frame = self.outer_frame.winfo_height()
        scrollbar_height = self.scrollbar.winfo_height()

        min_value = 0
        max_value = outer_frame - scrollbar_height

        if new_y < min_value: new_y = min_value
        if new_y > max_value: new_y = max_value

        self.scrollbar.place(anchor = tk.NE, relx = 1, y = new_y)
        scroll_percentage = new_y / (outer_frame - scrollbar_height)
        self.update_inner_frame_position(scroll_percentage)

    def update_inner_frame_position(self, scroll_percentage = None):
        self.outer_frame.update()

        outer_height = self.outer_frame.winfo_height()
        inner_height = super().winfo_height()

        if scroll_percentage is None:
            scrollbar_y = self.scrollbar.winfo_y()
            scrollbar_height = self.scrollbar.winfo_height()
            scroll_percentage = scrollbar_y / (outer_height - scrollbar_height)

        new_y = scroll_percentage * (outer_height - inner_height)
        super().place(anchor = tk.NW, x = 0, y = new_y)

    def update_scrollbar_position(self, scroll_percentage = None):
        self.outer_frame.update()
        outer_height = self.outer_frame.winfo_height()
        scrollbar_height = self.scrollbar.winfo_height()

        if scroll_percentage is None:
            inner_y = super().winfo_y()
            inner_height = super().winfo_height()
            scroll_percentage = inner_y / (outer_height - inner_height)

        new_y = scroll_percentage * (outer_height - scrollbar_height)
        self.scrollbar.place(anchor = tk.NE, relx = 1, y = new_y)

    def winfo_width(self):
        return self.outer_frame.cget("width")
    
    def winfo_height(self):
        return self.outer_frame.cget("height")

    def on_scrollbar_enter(self, event):
        self.root.configure(cursor = "hand2")
        self.scrollbar.configure(bg = self.scrollbar_hover_color)
    
    def on_scrollbar_leave(self, event):
        if self.scrolling: return
        self.root.configure(cursor = "arrow")
        self.scrollbar.configure(bg = self.scrollbar_color)

    # Place self.outer_frame instead of self
    def place(self, *args, **kwargs):
        if self.border_frame:
            self.border_frame.place(*args, **kwargs)
        else:
            self.outer_frame.place(*args, **kwargs)

class SelectableFrame(tk.Frame):
    def __init__(self, parent, hover_color, selection_color = None, click_handler = None, root = window, *args, **kwargs):
        if "bg" not in kwargs and "background" not in kwargs:
            raise ValueError("Please specify a background parameter. ('bg' or 'background')")

        super().__init__(parent, *args, **kwargs)

        super().bind("<Enter>", self.on_mouse_enter)
        super().bind("<Leave>", self.on_mouse_leave)

        if click_handler is None:
            click_handler = lambda event: self.toggle_selection()
        self.set_click_handler(click_handler)

        self.root = root
        self.background_color = super().cget("bg")
        self.hover_color = hover_color
        self.selection_color = selection_color if selection_color else hover_color
        self.selected = False

        self.bg_event_funcs = []
    
    def set_click_handler(self, click_handler):
        super().bind("<Button-1>", click_handler)

    def add_bg_event_handler(self, bg_event_func):
        self.bg_event_funcs.append(bg_event_func)

    def notify_bg_change(self, new_bg = None):
        if new_bg is None:
            new_bg = super().cget("bg")

        for func in self.bg_event_funcs:
            func(new_bg)

    def on_mouse_enter(self, event):
        if self.selected: return
        super().configure(bg = self.hover_color)
        self.notify_bg_change(self.hover_color)
    
    def on_mouse_leave(self, event):
        if self.selected: return
        super().configure(bg = self.background_color)
        self.notify_bg_change(self.background_color)
    
    def select(self):
        self.selected = True
        super().configure(bg = self.selection_color)
        self.notify_bg_change(self.selection_color)

    def deselect(self):
        self.selected = False
        super().configure(bg = self.background_color)
        self.notify_bg_change(self.background_color)

    def toggle_selection(self):
        self.selected = not self.selected
        super().configure(bg = self.selection_color if self.selected else self.background_color)
        self.notify_bg_change(self.selection_color if self.selected else self.background_color)

class ImageButton():
    def __init__(self, master, button_img_path, hover_img_path, click_img_path, on_click, new_width=None, new_height=None, disabled=False):
        self.master = master

        self.button_img = ImageTk.PhotoImage(self.resize_with_aspect_ratio(Image.open(button_img_path), new_width, new_height))
        self.hover_img = ImageTk.PhotoImage(self.resize_with_aspect_ratio(Image.open(hover_img_path), new_width, new_height))
        self.click_img = ImageTk.PhotoImage(self.resize_with_aspect_ratio(Image.open(click_img_path), new_width, new_height))

        self.label = tk.Label(master, image = self.button_img, borderwidth=0)
        self.on_click = on_click
        self.mouse_hovered = False
        self.disabled = disabled

        if self.disabled:
            self.disable()

        # For Animations
        self.label.bind("<ButtonPress-1>", self.on_mouse_down)
        self.label.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.label.bind("<Enter>", self.on_enter)
        self.label.bind("<Leave>", self.on_leave)

    def winfo_x(self):
        self.master.update()
        return self.label.winfo_x()

    def winfo_y(self):
        self.master.update()
        return self.label.winfo_y()
    
    def winfo_width(self):
        self.master.update()
        return self.label.winfo_width()
    
    def winfo_height(self):
        self.master.update()
        return self.label.winfo_height()

    def resize_with_aspect_ratio(self, image, new_width, new_height):
        width, height = image.size
        ratio = width / height

        if new_width is not None:
            new_height = int(new_width / ratio)
        
        elif new_height is not None:
            new_width = int(new_height * ratio)
        
        else:
            return image
        
        return image.resize((new_width, new_height))

    def disable(self):
        self.disabled = True
        self.update_image(self.click_img)
    
    def enable(self):
        self.disabled = False
        self.update_image(self.button_img)

    def update_image(self, new_img):
        self.label.configure(image = new_img)
        self.label.image = new_img
    
    def on_mouse_down(self, *args):
        if self.disabled: return
        self.update_image(self.click_img)
    
    def on_mouse_up(self, *args):
        if self.disabled: return
        self.update_image(self.hover_img)
        if self.mouse_hovered == True:
            self.on_click()

    def on_enter(self, *args):
        if self.disabled:
            self.master.config(cursor="X_cursor")
            return
        self.mouse_hovered = True
        self.update_image(self.hover_img)
        self.master.config(cursor="hand2")
    
    def on_leave(self, *args):
        self.master.config(cursor="arrow")
        if self.disabled: return
        self.mouse_hovered = False
        self.update_image(self.button_img)
    
    def place(self, *args, **kwargs):
        self.label.place(*args, **kwargs)

class Dropdown():
    def __init__(self, master, dropdown_items, font, font_size,
                 font_color, item_font_color, background_color, border_size,
                 border_color, item_highlight_color, default_item = 0, root = window):
        self.root = root
        self.master = master
        self.font = font
        self.font_size = font_size
        self.font_color = font_color
        self.item_font_color = item_font_color
        self.dropdown_items = dropdown_items
        self.background_color = background_color
        self.item_highlight_color = item_highlight_color
        self.current_index = default_item

        self.dropdown_open = False
        self.item_clicked = False

        self.frame = tk.Frame(self.master, bg = border_color)
        self.label = tk.Label(self.frame,
                              text = dropdown_items[default_item] + "⮛", # Get the longest string form dropdown (temporarily)
                              font = (font, font_size),
                              bg = background_color,
                              fg = font_color)
        self.label.bind("<Enter>", self.on_enter)
        self.label.bind("<Leave>", self.on_leave)
        self.label.bind("<Button-1>", self.on_click)
        self.label.bind("<FocusOut>", self.close_dropdown)
        self.label.pack(padx = border_size, pady = border_size)

        # Create a label for each dropdown item
        self.dropdown_labels = []
        for index in range(len(self.dropdown_items)):
            lbl = tk.Label(self.root, # We need root to make the dropdown item visible no matter where it is
                           text = self.dropdown_items[index],
                           font = (font, font_size),
                           bg = background_color if index != self.current_index else item_highlight_color,
                           fg = item_font_color)

            lbl.bind("<Enter>", lambda *args, index = index: self.on_item_enter(index))
            lbl.bind("<Leave>", lambda *args, index = index: self.on_item_leave(index))
            lbl.bind("<ButtonPress-1>", lambda *args, index = index: self.on_item_click(index))

            self.dropdown_labels.append(lbl)

    def winfo_width(self):
        return self.frame.winfo_width()

    def value(self):
        return self.dropdown_items[self.current_index]

    def on_enter(self, *args):
        self.root.config(cursor = "hand2")
    
    def on_leave(self, *args):
        self.root.config(cursor = "arrow")
    
    def on_item_enter(self, item_index):
        self.root.config(cursor = "hand2")
        self.dropdown_labels[item_index].configure(bg = self.item_highlight_color)
    
    def on_item_leave(self, item_index):
        if self.item_clicked: # This is to prevent the double event calls after clicking the item
            return
        self.root.config(cursor = "arrow")
        self.dropdown_labels[item_index].configure(bg = self.background_color if item_index != self.current_index else self.item_highlight_color)
    
    def on_click(self, *args):
        if item_clicked:
            return
        if not self.dropdown_open:
            self.open_dropdown()
        else:
            self.close_dropdown()

    def set_selected_item_by_index(self, item_index):
        self.dropdown_labels[self.current_index].config(bg = self.background_color) # Unhighlight current selected item
        self.current_index = item_index # Change current selected item
        self.label.config(text = self.dropdown_items[item_index] + "⮛") # Update label's text

    def set_selected_item_by_value(self, item_value):
        try:
            item_index = self.dropdown_items.index(item_value)
            self.set_selected_item_by_index(item_index)
        except:
            raise ValueError(f"The given item value ({item_value}) is not in the dropdown's items.")

    def on_item_click(self, item_index):
        global item_clicked
        item_clicked = True # Ignore focus so that self.label doesn't freak the fuck out next time (took me 2 hours to realise this smh)

        self.item_clicked = True
        self.set_selected_item_by_index(item_index)
        self.close_dropdown() # Close the dropdown

    def open_dropdown(self):
        self.item_clicked = False
        self.label.config(text = self.dropdown_items[self.current_index] + "⮙") # Update label's text

        for index in range(len(self.dropdown_labels)):
            if index == 0:
                xy = get_x_y_from_widget(self.frame,
                                         anchor = tk.S,
                                         parent = self.root)

            else:
                xy = get_x_y_from_widget(self.dropdown_labels[index - 1],
                                         anchor = tk.S,
                                         parent = self.root)

            # Bring item's label on top of all other widgets
            self.dropdown_labels[index].lift()
            # Place item's label
            self.dropdown_labels[index].place(anchor = tk.N, x = xy[0], y = xy[1])
            self.master.update()
            # Sleep for animation
            sleep(0.01)
        self.dropdown_open = True
    
    def close_dropdown(self, *args):
        self.label.config(text = self.dropdown_items[self.current_index] + "⮛") # Update label text
        for label in self.dropdown_labels[::-1]:
            label.place_forget()
            self.master.update()
            # Sleep for animation
            sleep(0.01)
        self.dropdown_open = False

    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)
        self.placed = True

    def pack(self, *args, **kwargs):
        self.frame.pack(*args, **kwargs)
        self.placed = True

    def place(self, *args, **kwargs):
        self.frame.place(*args, **kwargs)
        self.placed = True

    def grid_forget(self):
        self.frame.grid_forget()
        for label in self.dropdown_labels:
            label.grid_forget()

    def destroy(self):
        self.frame.destroy()
        for label in self.dropdown_labels:
            label.destroy()

class DropdownEntry():
    def __init__(self, master, root = window, width = None, dropdown_items = None, dropdown_font_color = light_blue,
                 font = roller_font_name, font_size = 20, cursor_color = "white",
                 border_size = 2, border_color = entry_border_color, dropdown_border_color = entry_dropdown_border_color,
                 background_color = entry_color, font_color = "white", entry_dropdown_gap = 5, auto_update_gap_color = False,
                 default_item = 0, drop_down_item_font_color = gold_yellow, numeric_only = True,**kwargs):
        self.master = master
        self.root = root
        self.dropdown_items = dropdown_items
        self.current_item = default_item
        self.border_size = border_size

        # Frame that contains both the entry and its dropdown
        self.frame = tk.Frame(self.master, bg = self.master.cget("bg"))

        self.entry = tk.Entry(self.frame,
                              width = width,
                              validate = "key" if numeric_only else None,
                              validatecommand = numeric_vcmd if numeric_only else None,
                              font = (font, font_size),
                              borderwidth = 0,
                              highlightthickness = border_size, # Border size
                              highlightbackground = border_color, # Border color
                              highlightcolor = border_color, # Border color when highlighted
                              insertbackground = cursor_color,
                              fg = font_color,
                              bg = background_color,
                              **kwargs)

        self.entry.grid(row = 0, column = 0)
        # self.entry.place(anchor = tk.S, relx=0, rely=0) # To be able to get height later
        # self.parent.update()

        self.dropdown = None
        if self.dropdown_items: 
            # Check if dropdown_items was passed as a string
            if type(self.dropdown_items) == str:
                # Frame used for border color
                self.dropdown = tk.Frame(self.frame, bg = dropdown_border_color)
                self.dropdown_label = tk.Label(self.dropdown,
                                               text = self.dropdown_items,
                                               font = (font, font_size - 3),
                                               bg = background_color,
                                               fg = dropdown_font_color)
                self.dropdown_label.pack(padx = border_size, pady = border_size)
            
            # Check if dropdown_items was passed as a list of one element
            elif len(self.dropdown_items) == 1:
                # Frame used for border color
                self.dropdown = tk.Frame(self.frame, bg = dropdown_border_color)
                self.dropdown_label = tk.Label(self.dropdown,
                                               text = self.dropdown_items[0],
                                               font = (font, font_size - 3),
                                               bg = background_color,
                                               fg = dropdown_font_color)
                self.dropdown_label.pack(padx = border_size, pady = border_size)

            else:
                default = tk.StringVar(self.frame)
                default.set(self.dropdown_items[self.current_item])
                self.dropdown = Dropdown(self.frame,
                                         dropdown_items = dropdown_items,
                                         font = font,
                                         font_size = font_size - 3,
                                         font_color = dropdown_font_color,
                                         item_font_color = drop_down_item_font_color,
                                         background_color = background_color,
                                         border_size = border_size,
                                         border_color = dropdown_border_color,
                                         item_highlight_color = entry_highlight_color,
                                         default_item = default_item)

        if entry_dropdown_gap and auto_update_gap_color:
            # Pass update_gap_color to add_bg_event_handler method in parent so that
            # whenever its background color changes, update_gap_color gets called
            self.master.add_bg_event_handler(self.update_gap_color)

        if self.dropdown:
            self.dropdown.grid(row = 0, column = 1, padx = (entry_dropdown_gap, 0))

    def update_gap_color(self, new_bg):
        # Supposed to be called by self.master whenever its background color changes

        # self.master.update()
        self.frame.configure(bg = new_bg)

    def insert(self, *args, **kwargs):
        return self.entry.insert(*args, **kwargs)

    def winfo_width(self):
        self.frame.master.update()
        return self.frame.winfo_width()
    
    def winfo_height(self):
        self.frame.master.update()
        return self.frame.winfo_height()

    def winfo_x(self):
        self.frame.master.update()
        return self.frame.winfo_x()
    
    def winfo_y(self):
        self.frame.master.update()
        return self.frame.winfo_y()

    def dropdown_width(self):
        return self.dropdown.winfo_width()
    
    def entry_width(self):
        return self.entry.winfo_width()

    def text_value(self):
        return self.entry.get()

    def dropdown_value(self):
        return self.dropdown.value()
    
    def get_full_value(self):
        return self.text_value(), self.dropdown_value()

    def place(self, *args, **kwargs):
        self.frame.place(*args, **kwargs)
    
    def grid(self, *args, **kwargs):
        self.frame.grid(*args, **kwargs)

    def grid_forget(self):
        self.frame.grid_forget()

    def destroy(self):
        self.frame.destroy()

# Tkinter Functions
def get_root_coords(root, widget):
    x = y = 0
    while widget != root:
        x += widget.winfo_x()
        y += widget.winfo_y()
        widget = widget.master
    return x, y

def relx(px, parent = window):
    parent_width = parent.winfo_width()
    return px / parent_width

def rely(px, parent = window):
    parent_height = parent.winfo_height()
    return px / parent_height

def get_x_y_from_widget(widget, anchor, shift_x_px = 0, shift_y_px = 0, parent = window):
    parent.update()

    # Top Left coordinates
    x, y = get_root_coords(root = parent, widget = widget)
    width, height = widget.winfo_width(), widget.winfo_height()

    def part1():
        if anchor == "center":
            return x + width/2, y + height/2

        elif anchor == "e": # Right
            return x + width, y + height/2
        
        elif anchor == "w": # Left
            return x, y + height/2
        
        elif anchor == "sw": # Bottom Left
            return x , y + height
        
        elif anchor == "se": # Bottom Right
            return x + width, y + height

        elif anchor == "s": # Mid Bot
            return x + width/2, y + height

        else:
            raise ValueError(f"The specified anchor ({anchor}) is not available in the function definition.")
    
    temp = part1()
    return temp[0] + shift_x_px, temp[1] + shift_y_px

def update(scenario = False, miners = False, highlight_selected_miner = False, reset_y = True):
    global selected_miner

    if not (scenario or miners):
        raise ValueError("Neither `scenario` or `miners` is set to True.")

    if scenario:
        # Scenario Label
        scenario_label.configure(text=f"Scenario {current_scenario}")
        scenario_label.place(anchor = tk.CENTER, relx = 0.5, rely = 0.07)

        # Right Button
        xy = get_x_y_from_widget(scenario_label, "e", 30)
        right_button.place(anchor = tk.W, x = xy[0], y = xy[1])
        right_button.disable() if current_scenario == len(scenarios) else right_button.enable()

        # Left Button
        xy = get_x_y_from_widget(scenario_label, "w", -30)
        left_button.place(anchor = tk.E, x = xy[0], y = xy[1])
        left_button.disable() if current_scenario == 1 else left_button.enable()

        # Add Scenario Button
        xy = get_x_y_from_widget(scenario_label, "s", 15, 20)
        add_scenario_button.place(anchor = tk.NE, x = xy[0], y = xy[1])

        # Delete Scenario Button
        xy = get_x_y_from_widget(add_scenario_button, "e", 10)
        delete_scenario_button.place(anchor = tk.W, x = xy[0], y = xy[1])
        delete_scenario_button.disable() if len(scenarios) == 1 else delete_scenario_button.enable()

        # Draw Separator
        draw_scenario_separator()

    if miners:
        if not highlight_selected_miner:
            # Since we will clear all current miner frames,
            # we need to set selected_miner to None.
            selected_miner = None

        # Destroy current miner frames
        for frame in current_miner_frames:
            frame.destroy()
        current_miner_frames.clear()

        # Clear current miner entries
        current_scenario_entries.clear()

        # Add new miner frames
        for index, miner in enumerate(scenarios[current_scenario - 1]):
            miner_frame = create_miner_frame(hashrate = miner["hashrate"],
                                             bonus = miner["bonus"],
                                             price = miner["price"],
                                             index = index)

            if highlight_selected_miner and index == selected_miner:
                miner_frame.select()

            current_miner_frames.append(miner_frame)
        
        miners_container_frame.manual_height_update(reset_y = reset_y)

def create_miner_frame(hashrate, bonus, price, index):
    # Creates a miner frame and positions it in the given row index
    # inside miners_container_frame, and then it returns the Frame object

    # hashrate example: "15.7 Ph/s"
    # bonus example: "2"
    # price example: "5"

    # Frame that contains miner entries
    miner_frame = SelectableFrame(parent = miners_container_frame,
                                  hover_color = miner_frame_hover_color,
                                  selection_color = miner_frame_selection_color,
                                  bg = miners_container_frame_bg,
                                  click_handler = lambda event: select_miner(current_miner_frames.index(event.widget)))
    miner_frame.grid(row = index, column = 0)

    # Hashrate Entry
    hashrate_entry = DropdownEntry(miner_frame, auto_update_gap_color = True, width = 14, font_size = 15, border_size = 1, dropdown_items = power_units, default_item = 1)
    hashrate_entry.insert(0, hashrate.split(" ")[0]) if hashrate else None # Set entry text value
    hashrate_entry.dropdown.set_selected_item_by_value(hashrate.split(" ")[1]) if hashrate else None # Set dropdown value
    hashrate_entry.grid(row = 0, column = 0, padx = (10, 0), pady = 10)

    # Bonus Entry
    bonus_entry = DropdownEntry(miner_frame, auto_update_gap_color = True, width = 14, font_size = 15, border_size = 1, dropdown_items = "%")
    bonus_entry.insert(0, str(bonus)) if bonus else None
    bonus_entry.grid(row = 0, column = 1, padx = (hashrate_entry.dropdown_width() + 10, 0), pady = 10)

    # Price Entry
    price_entry = DropdownEntry(miner_frame, auto_update_gap_color = True, width = 14, font_size = 15, border_size = 1, dropdown_items = "RLT")
    price_entry.insert(0, str(price)) if price else None
    price_entry.grid(row = 0, column = 2, padx = (bonus_entry.dropdown_width() + 10, 50), pady = 10)

    current_scenario_entries.append({
        "hashrate_entry": hashrate_entry,
        "bonus_entry": bonus_entry,
        "price_entry": price_entry
    })

    return miner_frame

def convert_power_to_gh(power, unit):
    units =  ['Gh/s', 'Th/s', 'Ph/s', 'Eh/s']
    if unit not in units:
        raise ValueError("The given unit is not available.")
    return float(power) * 10 ** (3 * units.index(unit))

def save_current_scenario_conf():
    # This function loops through all entries in the current_scenario
    # and saves their values in the scenarios dictoinary

    current_scenario_data = []
    for miner in current_scenario_entries:
        hashrate_entry = miner["hashrate_entry"]
        bonus_entry = miner["bonus_entry"]
        price_entry = miner["price_entry"]

        hashrate_value, hashrate_unit = hashrate_entry.get_full_value()
        bonus_value = bonus_entry.text_value()
        price_value = price_entry.text_value()

        hashrate_value = hashrate_value + " " + hashrate_unit if hashrate_value != "" else None
        bonus_value = bonus_value if bonus_value != "" else None
        price_value = price_value if price_value != "" else None

        current_scenario_data.append({
            "hashrate": hashrate_value,
            "bonus": bonus_value,
            "price": price_value
        })
    
    scenarios[current_scenario - 1] = current_scenario_data

    return current_scenario_data

def get_distinct_colors(num_colors):
    cm = plt.get_cmap('gist_rainbow')
    return [cm(1.*i/num_colors) for i in range(num_colors)]

def get_time_from_days(duration_in_days):
    duration_in_seconds = duration_in_days * 24 * 3600
    hours = int(duration_in_seconds / 3600)
    minutes = int(duration_in_seconds % 3600 / 60)
    seconds = int((duration_in_seconds % 3600) % 60)
    return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)

def convertPower(power):
    units =  ['Gh/s', 'Th/s', 'Ph/s', 'Eh/s']
    i = 0
    while power >= 1000:
        power /= 1000
        i += 1
    unit = units[i]
    return f"{power:.3f} {unit}"

def set_annotation(sel, scenario_index, scenario_color,
                   unbonused_power_history, bonused_power_history,
                   bonus_history, reward_history):
    try:
        x, y = sel.target
        sel.annotation.set(ma = "left", ha = "left")
        sel.annotation.set_text(
            f"Scenario: {scenario_index + 1}\n" \
            f"Day: {int(x)}\n" \
            f"Time: {get_time_from_days(x - int(x))}\n" \
            f"Balance: {round(y, 4)} RLT\n" \
            f"Power (Without Bonus): {convertPower(unbonused_power_history[int(x)])}\n" \
            f"Power (With Bonus): {convertPower(bonused_power_history[int(x)])}\n" \
            f"Bonus Percentage: {round(bonus_history[int(x)] * 100, 2)} %\n"\
            f"Reward (Per 10 mins): {round(reward_history[int(x)], 6)} RLT"
        )
        sel.annotation.get_bbox_patch().set(fc = scenario_color, alpha = 0.9, boxstyle = "roundtooth")
        sel.annotation.set_color(mpl_background_color)
        sel.annotation.arrow_patch.set(arrowstyle = "-", color = scenario_color)
    except IndexError: # Happens when you hover at the edge of the graph
        sel.annotation.set_visible(False) # Hide default annotation box that shows up
        pass
    # print(dir(sel.annotation))

def generate_graph(balance, total_power, total_bonus, network_power, block_reward, days, miners_data):
    fig, ax = plt.subplots()

    # Change icon of window
    thismanager = plt.get_current_fig_manager()
    thismanager.window.wm_iconbitmap('assets/Icon/icon.ico')

    # Set Title of window
    fig.canvas.manager.set_window_title('Roller Prediction Graph')

    # Set Title of graph
    ax.set_title("RLT Prediction Over Time [" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "]")

    ax.set_ylabel("--- RLT -->") # Set name of Y axis
    ax.set_xlabel("--- Days -->") # Set name of X axis
    scenario_colors = get_distinct_colors(len(miners_data)) # Get distinct color for each plot
    ax.set_prop_cycle(color = scenario_colors) # Set color cycle

    for index, scenario in enumerate(miners_data):
        scenario_balance = balance
        scenario_bonus_pct = total_bonus / 100
        scenario_unbonused_power = total_power # Power from games and miners
        current_miner = 0 # Index of miner to buy
        graph_x = range(1, days + 1)
        balance_history = []
        unbonused_power_history = []
        bonused_power_history = []
        bonus_history = []
        reward_history = []

        for day in range(days):
            if current_miner < len(scenario):
                if scenario_balance >= scenario[current_miner]["price"]:
                    scenario_balance -= scenario[current_miner]["price"]
                    scenario_unbonused_power += scenario[current_miner]["hashrate"]
                    scenario_bonus_pct += scenario[current_miner]["bonus"] / 100
                    current_miner += 1
            
            bonused_power = scenario_unbonused_power * (1 + scenario_bonus_pct)
            reward_per_10_mins = bonused_power / network_power * block_reward

            scenario_balance += reward_per_10_mins * 6 * 24
            balance_history.append(scenario_balance)
            unbonused_power_history.append(scenario_unbonused_power)
            bonused_power_history.append(bonused_power)
            bonus_history.append(scenario_bonus_pct)
            reward_history.append(reward_per_10_mins)

        scenario_plot = ax.plot(graph_x, balance_history)
        cur = mplcursors.cursor(scenario_plot, hover = mplcursors.HoverMode.Transient)
        cur.connect("add",
        lambda sel,
               i = index,
               uph = unbonused_power_history,
               bph = bonused_power_history,
               bh = bonus_history,
               rh = reward_history: set_annotation(sel, i, scenario_colors[i], uph, bph, bh, rh))

    ax.legend([f"Scenario {i + 1}" for i in range(len(miners_data))], loc = "upper left")

    plt.show()

def show_error(title, message):
    ctypes.windll.user32.MessageBoxW(0, message, title, 16)

def on_generate_click():
    # Update put current_scenario's data in the scenarios dict
    save_current_scenario_conf()

    # Get all main parameters
    # Main parameters: RLT Balance, Total Power, Total Bonus,
    #                  RLT Network Power, RLT Block Reward,
    #                  Days.

    # RLT Balance
    balance = balance_entry.text_value()
    if balance == "":
        show_error("Field Required", "RLT Balance is not set.")
        return
    balance = float(eval(balance))

    # Total Power
    total_power, total_power_unit = total_power_entry.get_full_value()
    if total_power == "":
        show_error("Field Required", "Total Power is not set.")
        return
    total_power = convert_power_to_gh(eval(total_power), total_power_unit)

    # Total Bonus
    total_bonus = bonus_pct_entry.text_value()
    if total_bonus == "":
        show_error("Field Required", "Total Bonus is not set.")
        return
    total_bonus = float(eval(total_bonus))

    # RLT Network Power
    network_power, network_power_unit = network_power_entry.get_full_value()
    if network_power == "":
        show_error("Field Required", "RLT Network Power is not set.")
        return
    network_power = convert_power_to_gh(eval(network_power), network_power_unit)

    # RLT Block Reward
    block_reward = block_reward_entry.text_value()
    if block_reward == "":
        show_error("Field Required", "RLT Block Reward is not set.")
        return
    block_reward = float(eval(block_reward))

    # Days
    days = days_entry.text_value()
    if days == "":
        show_error("Field Required", "Duration is not set.")
        return
    days = int(float(eval(days)))

    # print("RLT Balance:      ", balance)
    # print("Total Power:      ", total_power)
    # print("Total Bonus:     ", total_bonus)
    # print("RLT Network Power:", network_power)
    # print("RLT Block Reward: ", block_reward)
    # print("Duration In Days: ", days)

    # Check if all miner infos are available, and convert powers to Gh/s
    miners_data = [] # Represents the converted version of scenarios
    for i in range(len(scenarios)):
        miners_data.append([]) # Add scenario to data
        for j in range(len(scenarios[i])):
            miner = scenarios[i][j]
            if miner["hashrate"] is None:
                show_error("Miner Info Incomplete", f"Hashrate of miner {j + 1} in scenario {i + 1} is not set.")
                return
            if miner["bonus"] is None:
                show_error("Miner Info Incomplete", f"Bonus of miner {j + 1} in scenario {i + 1} is not set.")
                return
            if miner["price"] is None:
                show_error("Miner Info Incomplete", f"Price of miner {j + 1} in scenario {i + 1} is not set.")
                return
            miner_hashrate_value, miner_hashrate_unit = miner["hashrate"].split(" ")
            miners_data[-1].append({
                "hashrate": convert_power_to_gh(eval(miner_hashrate_value), miner_hashrate_unit),
                "bonus": eval(miner["bonus"]),
                "price": eval(miner["price"])
            })

    p = multiprocessing.Process(target=generate_graph, kwargs = {
        "balance": balance,
        "total_power": total_power,
        "total_bonus": total_bonus,
        "network_power": network_power,
        "block_reward": block_reward,
        "days": days,
        "miners_data": miners_data
    })
    # print(total_power)
    # print(total_bonus)
    # print(network_power)
    # print(block_reward)
    # print(days)
    # print(miners_data)
    p.start()
        
scenarios = [] # [[{"price": miner1_price, "hashrate": miner1_hashrate, "bonus": miner1_bonus}, ...other miners in scenario], ...other scenarios]
current_scenario = None
scenario_separators = []
current_miner_frames = [] # Miner frames of current scenario
selected_miner = None # Index of selected miner frame
current_scenario_entries = [] # [{"hashrate_entry": hasrate_entry1, "bonus_entry": bonus_entry1, "price_entry": price_entry1}, ...other miners in current_scenario]

def add_new_scenario(_update = True):
    global current_scenario

    if current_scenario is not None:
        # Update current scenario data in the scenarios dict
        save_current_scenario_conf()

    scenarios.append([])
    current_scenario = len(scenarios)

    if _update:
        update(scenario = True, miners = True)

def delete_scenario():
    global current_scenario

    scenarios.pop(current_scenario - 1)

    if current_scenario > len(scenarios):
        current_scenario -= 1

    update(scenario = True, miners = True)

def add_miner():
    # Adds a miner to the list representing the current scenario inside the scenarios dict
    # This function has nothing to do with updating the display whatsoever
    scenarios[current_scenario - 1].append({"price": None, "hashrate": None, "bonus": None})
    return scenarios[current_scenario - 1][-1], len(scenarios[current_scenario - 1]) - 1 # Return the newly created miner and its index

def remove_miner(miner_index):
    # Remove a miner from the list representing the current scenario inside the scenarios dict
    # This function has nothing to do with updating the display whatsoever
    scenarios[current_scenario - 1].pop(miner_index)
    current_scenario_entries.pop(miner_index)

def select_miner(miner_index, highlight_selected_miner = True, unhighlight_previous_selection = True):
    global selected_miner
    
    print("Selecting miner:", miner_index)

    if miner_index == selected_miner:
        # Unselect miner
        current_miner_frames[miner_index].deselect()
        selected_miner = None
        # Disable buttons that need selection
        disable_selection_buttons()
        return

    if unhighlight_previous_selection and selected_miner is not None:
        # Unhighlight current miner
        current_miner_frames[selected_miner].deselect()
    
    if highlight_selected_miner:
        # Highlight miner
        current_miner_frames[miner_index].select()

    selected_miner = miner_index
    # Enable buttons that need selection
    enable_selection_buttons()

def left_button_on_click():
    global current_scenario

    # Update scenario data in the scenarios dict
    save_current_scenario_conf()

    current_scenario -= 1
    update(scenario = True, miners = True)

def right_button_on_click():
    global current_scenario

    # Update scenario data in the scenarios dict
    save_current_scenario_conf()

    current_scenario += 1
    update(scenario = True, miners = True)

def draw_scenario_separator():
    global scenario_separators

    scenario_count = len(scenarios)
    xy = get_x_y_from_widget(delete_scenario_button, "s", 0, 30)

    # Clean all previous separators
    for separator in scenario_separators:
        separator.destroy()
    scenario_separators = []

    sep_padding = 10 # px

    if scenario_count == 1:
        separator = tk.Frame(window, bd=10, relief='sunken', height=4, width=window_width - sep_padding * 2, bg=default_sep_color, borderwidth=0)
        separator.place(anchor = tk.NW, x = sep_padding, y = xy[1])
        scenario_separators.append(separator)
    else:
        sep_width = ( window_width - sep_padding * (scenario_count + 1) ) / scenario_count
        for i in range(scenario_count):
            sep_color = light_green if i == current_scenario - 1 else default_sep_color
            separator = tk.Frame(window, bd=10, relief='sunken', height=4, width=sep_width, bg=sep_color, borderwidth=0)
            x = i * sep_width + (i + 1) * sep_padding
            separator.place(anchor = tk.NW, x = x, y = xy[1])
            scenario_separators.append(separator)

def on_add_miner_click():
    # Add miner to the scenarios dictionary
    miner_dict, index = add_miner()
    # Update the display
    miner_frame = create_miner_frame(hashrate = miner_dict["hashrate"],
                                     bonus = miner_dict["bonus"],
                                     price = miner_dict["price"],
                                     index = index)
    current_miner_frames.append(miner_frame)
    miners_container_frame.manual_height_update(reset_y = False)

def on_remove_miner_click():
    global selected_miner

    # Remove miner from the scenarios dictionary and current_scenario_entries
    remove_miner(selected_miner)

    # Update the display
    # 1. Destroy the miner frame and remove it from the current_miner_frames list
    current_miner_frames[selected_miner].destroy()
    current_miner_frames.pop(selected_miner)
    
    # 2. Move all miner frames below it to fill the gap
    for i in range(selected_miner, len(current_miner_frames)):
        current_miner_frames[i].grid(row = i, column = 0)
    
    # 3. Update miner_container_frame's height, and set inner frame's y to 0 if scrollbar is invisible
    miners_container_frame.manual_height_update()
    if not miners_container_frame.scrollable:
        miners_container_frame.update_inner_frame_position(0)

    # 3. Highlight newly selected miner, if there's any
    if len(current_miner_frames) == 0:
        # No miner frame to select
        selected_miner = None
        disable_selection_buttons()
        return

    if len(current_miner_frames) >= selected_miner + 1:
        # We highlight the frame that was below the deleted one
        # In other words, the frame that's now in place of the deleted one
        current_miner_frames[selected_miner].select()
        return
    
    # We select and highlight the frame that was above the delete one
    selected_miner = len(current_miner_frames) - 1
    current_miner_frames[selected_miner].select()

def on_move_up_click():
    global selected_miner

    if selected_miner == 0:
        return
    
    # Update scenarios dict by flipping selected_miner and the one before it
    scenario = scenarios[current_scenario - 1]
    flip_list_indices(scenario, selected_miner - 1, selected_miner)

    # Update the display
    current_miner_frames[selected_miner].grid(row = selected_miner - 1, column = 0)
    current_miner_frames[selected_miner - 1].grid(row = selected_miner, column = 0)

    # Update current_miner_frames and current_scenario_entries
    flip_list_indices(current_miner_frames, selected_miner - 1, selected_miner)
    flip_list_indices(current_scenario_entries, selected_miner - 1, selected_miner)

    # Update selected_miner
    selected_miner -= 1

def on_move_down_click():
    global selected_miner

    if selected_miner == len(current_miner_frames) - 1:
        return
    
    # Update scenarios dict by flipping selected_miner and the one before it
    scenario = scenarios[current_scenario - 1]
    flip_list_indices(scenario, selected_miner, selected_miner + 1)

    # Update the display
    current_miner_frames[selected_miner].grid(row = selected_miner + 1, column = 0)
    current_miner_frames[selected_miner + 1].grid(row = selected_miner, column = 0)

    # Update current_miner_frames and current_scenario_entries
    flip_list_indices(current_miner_frames, selected_miner, selected_miner + 1)
    flip_list_indices(current_scenario_entries, selected_miner, selected_miner + 1)

    # Update selected_miner
    selected_miner += 1

def flip_list_indices(l, i1, i2):
    l[i1], l[i2] = l[i2], l[i1]

def disable_selection_buttons():
    # A function that disables all the buttons that need a frame to be selected
    remove_miner_button.disable()
    move_up_button.disable()
    move_down_button.disable()

def enable_selection_buttons():
    # A function that enables all the buttons that need a frame to be selected
    remove_miner_button.enable()
    move_up_button.enable()
    move_down_button.enable()

def NumericValidation(S):
    if S in "0123456789.-+*/ " or len(S) > 1: # The second condition is when backspace is clicked on a selection
        return True
    window.bell() # .bell() plays that ding sound telling you there was invalid input
    return False

# Main algorithm
if __name__ == "__main__":
    numeric_vcmd = (window.register(NumericValidation), '%S')

    add_new_scenario(_update = False)

    # Scenario Label
    scenario_label = tk.Label(window,
                            text = f"Scenario {current_scenario}",
                            font = (roller_font_name, 40),
                            bg = bg,
                            fg = light_green)
    scenario_label.place(anchor = tk.CENTER, relx = 0.5, rely = 0.07)

    # Right Button
    right_button = ImageButton(master = window,
                            button_img_path = "assets/Buttons/right_arrow.png",
                            hover_img_path = "assets/Buttons/right_arrow_hovered.png",
                            click_img_path = "assets/Buttons/right_arrow_clicked.png",
                            on_click = right_button_on_click,
                            new_width = 50,
                            disabled = True)
    xy = get_x_y_from_widget(scenario_label, "e", 30)
    right_button.place(anchor = tk.W, x = xy[0], y = xy[1])

    # Left Button
    left_button = ImageButton(master = window,
                            button_img_path = "assets/Buttons/left_arrow.png",
                            hover_img_path = "assets/Buttons/left_arrow_hovered.png",
                            click_img_path = "assets/Buttons/left_arrow_clicked.png",
                            on_click = left_button_on_click,
                            new_width = 50,
                            disabled = True)
    xy = get_x_y_from_widget(scenario_label, "w", -30)
    left_button.place(anchor = tk.E, x = xy[0], y = xy[1])

    # Add Scenario Button
    add_scenario_button = ImageButton(master = window,
                                    button_img_path = "assets/Buttons/new_scenario_button.png",
                                    hover_img_path = "assets/Buttons/new_scenario_button_hovered.png",
                                    click_img_path = "assets/Buttons/new_scenario_button_clicked.png",
                                    on_click = add_new_scenario,
                                    new_width = 150)
    xy = get_x_y_from_widget(scenario_label, "s", 15, 20)
    add_scenario_button.place(anchor = tk.NE, x = xy[0], y = xy[1])

    # Delete Scenario Button
    delete_scenario_button = ImageButton(master = window,
                                        button_img_path = "assets/Buttons/delete_button.png",
                                        hover_img_path = "assets/Buttons/delete_button_hovered.png",
                                        click_img_path = "assets/Buttons/delete_button_clicked.png",
                                        on_click = delete_scenario,
                                        new_height = add_scenario_button.winfo_height(),
                                        disabled = True)
    xy = get_x_y_from_widget(add_scenario_button, "e", 10)
    delete_scenario_button.place(anchor = tk.W, x = xy[0], y = xy[1])

    # Horizontal Separator
    draw_scenario_separator()

    # Balance Label
    balance_label = tk.Label(window,
                            text = f"RLT Balance:",
                            font = (roller_font_name, 20),
                            bg = bg,
                            fg = "white")
    xy = get_x_y_from_widget(delete_scenario_button, "s", 0, 70)
    balance_label.place(anchor = tk.NW, relx = 0.04, y = xy[1])

    # Balance Entry
    balance_entry = DropdownEntry(window, dropdown_items = "RLT")
    xy = get_x_y_from_widget(balance_label, "e", 10, 0)
    balance_entry.place(anchor = tk.W, relx = 0.41, y = xy[1])

    # Total Power Label
    total_power_label = tk.Label(window,
                                text = f"Power (No Bonus):",
                                font = (roller_font_name, 20),
                                bg = bg,
                                fg = "white")
    xy = get_x_y_from_widget(balance_label, "sw", 0, 20)
    total_power_label.place(anchor = tk.NW, relx = 0.04, y = xy[1])

    # Total Power Entry
    total_power_entry = DropdownEntry(window, dropdown_items = power_units, default_item = 1)
    xy = get_x_y_from_widget(total_power_label, "e", 10, 0)
    total_power_entry.place(anchor = tk.W, relx = 0.41, y = xy[1])

    # Total Bonus Label
    bonus_pct_label = tk.Label(window,
                                text = f"Bonus Percentage:",
                                font = (roller_font_name, 20),
                                bg = bg,
                                fg = "white")
    xy = get_x_y_from_widget(total_power_label, "sw", 0, 20)
    bonus_pct_label.place(anchor = tk.NW, relx = 0.04, y = xy[1])

    # Total Bonus Entry
    bonus_pct_entry = DropdownEntry(window, dropdown_items = "%", default_item = 1)
    xy = get_x_y_from_widget(bonus_pct_label, "e", 10, 0)
    bonus_pct_entry.place(anchor = tk.W, relx = 0.41, y = xy[1])

    # Network Power Label
    network_power_label = tk.Label(window,
                                text = f"RLT Network Power:",
                                font = (roller_font_name, 20),
                                bg = bg,
                                fg = "white")
    xy = get_x_y_from_widget(bonus_pct_label, "sw", 0, 20)
    network_power_label.place(anchor = tk.NW, relx = 0.04, y = xy[1])

    # Network Power Entry
    network_power_entry = DropdownEntry(window, dropdown_items = power_units, default_item = 3)
    xy = get_x_y_from_widget(network_power_label, "e", 10, 0)
    network_power_entry.place(anchor = tk.W, relx = 0.41, y = xy[1])

    # Block Reward Label
    block_reward_label = tk.Label(window,
                                text = f"RLT Block Reward:",
                                font = (roller_font_name, 20),
                                bg = bg,
                                fg = "white")
    xy = get_x_y_from_widget(network_power_label, "sw", 0, 20)
    block_reward_label.place(anchor = tk.NW, relx = 0.04, y = xy[1])

    # Block Reward Entry
    block_reward_entry = DropdownEntry(window, dropdown_items = "RLT")
    xy = get_x_y_from_widget(block_reward_label, "e", 10, 0)
    block_reward_entry.place(anchor = tk.W, relx = 0.41, y = xy[1])

    # Miners Label
    miners_label = tk.Label(window,
                            text = f"Scenario Miners",
                            font = (roller_font_name, 20),
                            bg = bg,
                            fg = "white")
    xy = get_x_y_from_widget(block_reward_label, "sw", 0, 20)
    miners_label.place(anchor = tk.N, relx = 0.5, y = xy[1])

    # Miner's hashrate label
    hashrate_label = tk.Label(window,
                            text = f"Hashrate",
                            font = (roller_font_name, 15),
                            bg = bg,
                            fg = "#6a668a")
    xy = get_x_y_from_widget(miners_label, "sw", 0, 10)
    hashrate_label.place(anchor = tk.NW, relx = 0.14, y = xy[1])

    # Miner's bonus label
    bonus_label = tk.Label(window,
                            text = f"Bonus",
                            font = (roller_font_name, 15),
                            bg = bg,
                            fg = "#6a668a")
    xy = get_x_y_from_widget(hashrate_label, "e", 110, 0)
    bonus_label.place(anchor = tk.W, x = xy[0], y = xy[1])

    # Miner's price label
    price_label = tk.Label(window,
                        text = f"Price",
                        font = (roller_font_name, 15),
                        bg = bg,
                        fg = "#6a668a")
    xy = get_x_y_from_widget(bonus_label, "e", 110, 0)
    price_label.place(anchor = tk.W, x = xy[0], y = xy[1])

    # Miners Container Frame
    miners_container_frame = ScrollableFrame(window,
                                            root = window,
                                            width = window_width * (1 - 2 * 0.04),
                                            height = 150,
                                            bg = miners_container_frame_bg,
                                            border_size = 2,
                                            border_color = miners_container_frame_border_color)
    xy = get_x_y_from_widget(hashrate_label, "sw", 0, 10)
    miners_container_frame.place(anchor = tk.NW, relx = 0.04, y = xy[1])

    # Add Miner Button
    add_miner_button = ImageButton(master = window,
                                button_img_path = "assets/Buttons/plus_button.png",
                                hover_img_path = "assets/Buttons/plus_button_hovered.png",
                                click_img_path = "assets/Buttons/plus_button_clicked.png",
                                on_click = on_add_miner_click,
                                new_width = 50)
    xy = get_x_y_from_widget(miners_container_frame, "sw", 0, 10)
    add_miner_button.place(anchor = tk.NW, x = xy[0], y = xy[1])

    # Remove Miner Button
    remove_miner_button = ImageButton(master = window,
                                    button_img_path = "assets/Buttons/minus_button.png",
                                    hover_img_path = "assets/Buttons/minus_button_hovered.png",
                                    click_img_path = "assets/Buttons/minus_button_clicked.png",
                                    on_click = on_remove_miner_click,
                                    new_height = add_miner_button.winfo_height(),
                                    disabled = True)
    xy = get_x_y_from_widget(add_miner_button, "e", 5)
    remove_miner_button.place(anchor = tk.W, x = xy[0], y = xy[1])

    # Move Up Button
    move_up_button = ImageButton(master = window,
                                button_img_path = "assets/Buttons/up_arrow.png",
                                hover_img_path = "assets/Buttons/up_arrow_hovered.png",
                                click_img_path = "assets/Buttons/up_arrow_clicked.png",
                                on_click = on_move_up_click,
                                new_height = add_miner_button.winfo_height(),
                                disabled = True)
    xy = get_x_y_from_widget(miners_container_frame, "se", 0, 10)
    move_up_button.place(anchor = tk.NE, x = xy[0], y = xy[1])

    # Move Down Button
    move_down_button = ImageButton(master = window,
                                button_img_path = "assets/Buttons/down_arrow.png",
                                hover_img_path = "assets/Buttons/down_arrow_hovered.png",
                                click_img_path = "assets/Buttons/down_arrow_clicked.png",
                                on_click = on_move_down_click,
                                new_height = move_up_button.winfo_height(),
                                disabled = True)
    xy = get_x_y_from_widget(move_up_button, "w", -5)
    move_down_button.place(anchor = tk.E, x = xy[0], y = xy[1])

    # Days Label
    days_label = tk.Label(window,
                        text = f"Duration In Days:",
                        font = (roller_font_name, 20),
                        bg = bg,
                        fg = "white")
    days_label.place(anchor = tk.SW, relx = 0.04, rely = 1 - rely(20))

    # Days Entry
    days_entry = DropdownEntry(window, width = 12)
    xy = get_x_y_from_widget(days_label, "e", 10, 0)
    days_entry.place(anchor = tk.W, relx = 0.41, y = xy[1])

    # Generate Button
    generate_button = ImageButton(master = window,
                                button_img_path = "assets/Buttons/generate_button.png",
                                hover_img_path = "assets/Buttons/generate_button_hovered.png",
                                click_img_path = "assets/Buttons/generate_button_clicked.png",
                                on_click = on_generate_click,
                                new_height = 40,
                                disabled = False)
    xy = get_x_y_from_widget(days_entry, "e")
    generate_button.place(anchor = tk.E, relx = 1 - relx(20), y = xy[1])

    update(scenario = False, miners = True)

    window.mainloop()