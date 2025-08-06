import os
import sys
import threading
import configparser
import webbrowser
from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk

# ==== BASE_DIR ====
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# ==== Paths ====
assets_dir = os.path.join(base_dir, 'GUI', 'Assets')
pictures_dir = os.path.join(assets_dir, 'Pictures')
banners_dir = os.path.join(assets_dir, 'Banners')

image_path = os.path.join(pictures_dir, '1.png')
banner_singleplayer = os.path.join(banners_dir, 'SINGLEPLAYER.png')
banner_console = os.path.join(banners_dir, 'CONSOLE.png')
banner_prisoner = os.path.join(banners_dir, 'PRISONER.png')
banner_flagzones = os.path.join(banners_dir, 'FLAGZONES.png')
banner_supportmywork = os.path.join(banners_dir, 'SUPPORTMYWORK.png')
banner_buymeacoffee = os.path.join(banners_dir, 'BUYMEACOFFEE.png')

data_path = os.path.join(base_dir, 'data.ini')
data_config = configparser.ConfigParser()

MAX_LINES = 64


# ==== Import logiky ====
from Modules.Singleplayer.SaveItems.v32 import logic


class App(Tk):
    def __init__(self):
        super().__init__()
        self.title("SCUM Quality of Life v0.3.3.2 beta")
        self.geometry("520x820")
        self.configure(bg="#242424")
        self.resizable(False, False)

        self.images = []  # prevent garbage collection of PhotoImage

        # ==== UI Layout ====
        self.build_ui()

        # ==== Timers ====
        self.after(1000, self.update_from_data_file)

        # ==== Logika ====
        self.log("SCUM Quality of Life", color="orange")
        self.update_from_data_file()

        self.stop_event = threading.Event()
        self.logic_thread = threading.Thread(target=logic.logic_main_loop, args=(self, self.stop_event), daemon=True)
        self.logic_thread.start()

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def load_image(self, path, size=None):
        try:
            img = Image.open(path)
            if size:
                img = img.resize(size, Image.ANTIALIAS)
            tk_img = ImageTk.PhotoImage(img)
            self.images.append(tk_img)
            return tk_img
        except Exception:
            return None

    def build_ui(self):
        pady = 4

        # Obrázok
        img = self.load_image(image_path, (500, 300))
        Label(self, image=img, bg="#242424").pack(pady=pady)

        # Banner: SINGLEPLAYER
        banner = self.load_image(banner_singleplayer, (520, 40))
        Label(self, image=banner, bg="#242424").pack(pady=pady)

        # Banner + text: Prisoner
        frame1 = Frame(self, bg="#242424")
        frame1.pack(fill=X, padx=8, pady=pady)
        prisoner_img = self.load_image(banner_prisoner, (100, 20))
        Label(frame1, image=prisoner_img, bg="#242424").pack(side=LEFT)
        self.prisoner_value = Label(frame1, text="Loading...", fg="#CCCCCC", bg="#242424", font=("Arial", 14))
        self.prisoner_value.pack(side=LEFT, padx=10)

        # Banner + text: Flagzones
        frame2 = Frame(self, bg="#242424")
        frame2.pack(fill=X, padx=8, pady=pady)
        flagzones_img = self.load_image(banner_flagzones, (100, 20))
        Label(frame2, image=flagzones_img, bg="#242424").pack(side=LEFT)
        self.flagzones_value = Label(frame2, text="0", fg="#FF9900", bg="#242424", font=("Arial", 14))
        self.flagzones_value.pack(side=LEFT, padx=10)

        # Banner: CONSOLE
        console_img = self.load_image(banner_console, (520, 40))
        Label(self, image=console_img, bg="#242424").pack(pady=pady)

        # Console Text Area
        self.console = ScrolledText(self, height=15, bg="black", fg="#20FF20", insertbackground="white", wrap=WORD)
        self.console.pack(fill=BOTH, expand=False, padx=8, pady=pady)
        self.console.config(state=DISABLED)

        # Banner: SUPPORTMYWORK
        support_img = self.load_image(banner_supportmywork, (520, 40))
        Label(self, image=support_img, bg="#242424").pack(pady=pady)

        # Buy me a coffee
        frame3 = Frame(self, bg="#242424")
        frame3.pack(pady=pady)
        coffee_img = self.load_image(banner_buymeacoffee, (120, 28))
        Label(frame3, image=coffee_img, bg="#242424").pack(side=LEFT)
        Button(frame3, text="☕ Buy me a coffee", command=self.open_coffee_link,
               bg="#FFDD00", fg="black", font=("Arial", 12, "bold"),
               relief=RAISED, bd=2, padx=10, pady=2).pack(side=LEFT, padx=12)

    def log(self, text, color="#20FF20"):
        self.console.config(state=NORMAL)
        self.console.insert(END, f"{text}\n")
        self.console.see(END)
        self.console.config(state=DISABLED)

    def thread_safe_log(self, text, color="#20FF20"):
        self.after(0, lambda: self.log(text, color))

    def update_prisoner_name(self, name: str):
        self.prisoner_value.config(text=name)

    def update_flag_zones(self, count):
        self.flagzones_value.config(text=str(count))
        self.thread_safe_log(f"[GUI] Zmenený počet základní: {count}", color="#FFFF00")

    def open_coffee_link(self):
        webbrowser.open("https://www.buymeacoffee.com/jastronit")

    def update_from_data_file(self):
        if not os.path.exists(data_path):
            self.after(1000, self.update_from_data_file)
            return
        try:
            data_config.read(data_path)

            if 'prisoner' in data_config:
                name = data_config['prisoner'].get('name', 'Unknown')
                self.update_prisoner_name(name)

            if 'flagzones' in data_config:
                count = data_config['flagzones'].getint('count', 0)
                self.update_flag_zones(count)

            log_path = os.path.join(base_dir, 'log.txt')
            if os.path.exists(log_path):
                with open(log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-MAX_LINES:]
                    self.console.config(state=NORMAL)
                    self.console.delete(1.0, END)
                    for line in lines:
                        self.console.insert(END, line.strip() + "\n")
                    self.console.config(state=DISABLED)
                    self.console.see(END)
        except Exception as e:
            self.thread_safe_log(f"[GUI] Chyba pri čítaní data.ini: {e}", color="red")

        self.after(1000, self.update_from_data_file)

    def on_close(self):
        self.stop_event.set()
        self.logic_thread.join()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()

def run_gui():
    app = App()
    app.mainloop()


