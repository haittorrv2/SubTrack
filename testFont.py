import tkinter as tk
import tkinter.font as tkfont

root = tk.Tk()

available_fonts = sorted(tkfont.families(root))

for font_name in available_fonts:
    if "SPACE" in font_name.upper() or "GROTESK" in font_name.upper():
        print(repr(font_name))

root.destroy()