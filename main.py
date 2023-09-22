import tkinter as tk
from tkinter import filedialog, Scale, ttk, messagebox
from pdf2image import convert_from_path
from PIL import ImageTk
from PyPDF2 import PdfReader, PdfWriter
import threading
import queue


class PDFManager:
    def __init__(self):
        self.pages = []
        self.pdf = None

    def load_pdf(self, file_path):
        self.pages = convert_from_path(file_path)
        self.pdf = PdfReader(open(file_path, 'rb'))

    def save_pdf(self, selected_pages, save_path):
        output = PdfWriter()
        for idx in selected_pages:
            output.add_page(self.pdf.pages[idx])

        with open(save_path, 'wb') as f:
            output.write(f)


class ThumbnailManager:
    def __init__(self, slider):
        self.slider = slider
        self.pages = []
        self.page_imgs = []

    def update_images(self, pages):
        self.pages = pages
        self.page_imgs = []
        size = self.slider.get()

        for img in self.pages:
            img_width = img.width
            img_height = img.height
            img_resized = img.resize((size, size * int(img_height / img_width)))
            self.page_imgs.append(img_resized)


class PDFExtractor(tk.Tk):
    def __init__(self):
        super().__init__()
        self.selected_pages = []
        self.queue = queue.Queue()
        self.after(100, self.check_queue)

        self.pdf_manager = PDFManager()
        self.setup_ui()
        self.thumbnail_manager = ThumbnailManager(self.slider)

    def setup_ui(self):
        self.load_btn = ttk.Button(self, text="Load PDF", command=self.load_pdf)
        self.load_btn.pack(pady=20)

        self.slider = Scale(self, from_=50, to=500, orient="horizontal", label="Thumbnail Size")
        self.slider.pack(pady=20)
        self.slider.bind("<Motion>", self.update_images)

        self.canvas = tk.Canvas(self)
        self.canvas.pack(side="left", fill=tk.BOTH, expand=True)

        self.canvas_frame = ttk.Frame(self.canvas)  # Frame inside canvas to hold thumbnails
        self.canvas_window = self.canvas.create_window((0, 0), window=self.canvas_frame, anchor="nw")

        # Add Vertical Scrollbar
        self.v_scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.v_scrollbar.pack(side="right", fill="y")

        # Add Horizontal Scrollbar
        self.h_scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.h_scrollbar.pack(side="bottom", fill="x")

        self.canvas.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas_frame.bind("<Configure>", self.on_frame_configure)

        # Binding mouse scroll wheel to the canvas
        self.canvas.bind("<MouseWheel>", self.on_mouse_scroll)

        self.save_entry = ttk.Entry(self)
        self.save_entry.pack(pady=20)
        self.save_entry.insert(0, "output.pdf")

        self.status_label = ttk.Label(self, text="")
        self.status_label.pack(pady=20)

        self.save_btn = ttk.Button(self, text="Extract Selected Pages", command=self.save_pdf)
        self.save_btn.pack(pady=20)

    def check_queue(self):
        try:
            task = self.queue.get(0)
            task()
        except queue.Empty:
            pass

        self.after(100, self.check_queue)

    def on_mouse_scroll(self, event):
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    def load_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not file_path:
            return

        # Clear the current thumbnails
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        # Reset the selected pages list
        self.selected_pages = []

        # Disable the load button to prevent multiple clicks while loading
        self.load_btn.config(state=tk.DISABLED)

        # Start the thread to load the PDF
        threading.Thread(target=self.load_pdf_thread, args=(file_path,)).start()

    def load_pdf_thread(self, file_path):
        self.pdf_manager.load_pdf(file_path)
        self.thumbnail_manager.update_images(self.pdf_manager.pages)

        # Add the task to re-enable the load button to the queue
        self.queue.put(self.re_enable_load_button)

        # Add the task to show thumbnails to the queue
        self.queue.put(self.show_thumbnails)

    def re_enable_load_button(self):
        self.load_btn.config(state=tk.NORMAL)

    def update_images(self, event=None):
        self.thumbnail_manager.update_images(self.pdf_manager.pages)
        self.show_thumbnails()

    def show_thumbnails(self):
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        for idx, img in enumerate(self.thumbnail_manager.page_imgs):
            img_tk = ImageTk.PhotoImage(image=img)
            btn = ttk.Checkbutton(self.canvas_frame, image=img_tk, command=lambda i=idx: self.toggle_page(i))
            btn.image = img_tk
            btn.grid(row=idx // 4, column=idx % 4, padx=5, pady=5)

            # Bind the mouse scroll event to each button
            btn.bind("<MouseWheel>", self.on_mouse_scroll)

    def toggle_page(self, idx):
        if idx in self.selected_pages:
            self.selected_pages.remove(idx)
        else:
            self.selected_pages.append(idx)

    def save_pdf(self):
        self.save_btn.config(state=tk.DISABLED)  # Disable the button
        self.status_label.config(text="Extracting pages... Please wait.")
        self.update_idletasks()  # Force the GUI to update
        threading.Thread(target=self.save_pdf_thread).start()

    def save_pdf_thread(self):
        self.pdf_manager.save_pdf(self.selected_pages, self.save_entry.get())
        self.queue.put(self.on_extraction_complete)

    def on_extraction_complete(self):
        self.status_label.config(text="")
        self.save_btn.config(state=tk.NORMAL)  # Enable the button
        messagebox.showinfo("Info", "Extraction complete!")

    def on_canvas_configure(self, event):
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_frame_configure(self, event):
        '''Reset the canvas size to encompass inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("window", self.canvas_window))

app = PDFExtractor()
app.mainloop()
