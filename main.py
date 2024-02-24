import tkinter as tk
from tkinter import messagebox
from PIL import ImageGrab, ImageTk, ImageDraw
import os
import ctypes
import traceback
import sys
import asyncio


class ScreenCaptureApp:
    def __init__(self, master):
        self.master = master
        master.title("Screen Capture Tool")
        # Make the application DPI aware (Windows-specific)
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        # Button to start screen capture
        self.capture_btn = tk.Button(
            master, text="Capture Screen", command=self.start_capture
        )

        self.captureFull_btn = tk.Button(
            master,
            text="Capture Full Screen",
            command=lambda: asyncio.run(self.capture_full_screen()),
        )
        self.captureFull_btn.pack()
        self.capture_btn.pack()

        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        self.screen_width = user32.GetSystemMetrics(0)  # Width
        self.screen_height = user32.GetSystemMetrics(1)  # Height
        self.is_capturing = False

    def report_callback_exception(self, exc, val, tb):
        error_message = "".join(traceback.format_exception(exc, val, tb))
        messagebox.showerror(
            "Application Error", "An error occurred: \n" + error_message
        )
        # Optionally, log the error message to a file or application log

    def start_capture(self):
        self.is_capturing = True
        self.master.withdraw()  # Hide the window
        self.capture_win = tk.Toplevel(self.master)
        self.capture_win.attributes("-fullscreen", True)  # Fullscreen
        # For some configurations, explicitly setting the window size might help
        self.capture_win.geometry(f"{self.screen_width}x{self.screen_height}+0+0")

        # Maximizing the window to ensure it covers the entire screen
        self.capture_win.state("zoomed")
        self.capture_win.attributes("-alpha", 0.3)  # Make the window transparent
        self.capture_win.overrideredirect(True)  # Remove window decorations

        # Create a full-screen canvas in the capture window for drawing
        self.canvas = tk.Canvas(self.capture_win, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Initialize the rectangle
        self.rect = None
        self.start_x = None
        self.start_y = None

        # Bind mouse events to the canvas
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def on_button_press(self, event):
        # Convert canvas coordinates to global screen coordinates
        self.start_x = self.capture_win.winfo_rootx() + event.x
        self.start_y = self.capture_win.winfo_rooty() + event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x,
            self.start_y,
            self.start_x,
            self.start_y,
            outline="red",
            width=2,
        )

    def on_move_press(self, event):
        curX, curY = (event.x, event.y)
        # Update the rectangle's coordinates on the canvas
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def on_button_release(self, event):
        # Finalize the rectangle (Optional: You can capture or save the screenshot here)
        self.end_x = self.capture_win.winfo_rootx() + event.x
        self.end_y = self.capture_win.winfo_rooty() + event.y
        print(
            f"Rectangle coordinates: {self.start_x}, {self.start_y}, {self.end_x}, {self.end_y}"
        )
        # Close the capture window and return to the main application window
        self.capture_win.destroy()
        self.capture_screen_area(self.start_x, self.start_y, self.end_x, self.end_y)
        self.master.deiconify()

    def capture_screen_area(self, x1, y1, x2, y2):
        # Adjust coordinates if necessary
        bbox = (min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))

        # Check for a valid rectangle (non-zero and positive width and height)
        if bbox[0] < bbox[2] and bbox[1] < bbox[3]:
            # Capture the selected screen area
            image = ImageGrab.grab(bbox=bbox)
            self.show_screenshot_for_annotation(image)

            # Save the image
            try:
                image.save(os.path.join(os.getcwd(), "screenshot.png"))
            except Exception as e:
                print(f"Error saving the screenshot: {e}")

        else:
            print("Invalid screenshot dimensions. Please try again.")

    async def capture_full_screen(self):
        self.master.withdraw()  # Hide the window

        await asyncio.sleep(0.3)
        # Capture the entire screen
        image = ImageGrab.grab(bbox=(0, 0, self.screen_width, self.screen_height))
        self.show_screenshot_for_annotation(image)

        self.master.deiconify()
        # Save the image
        image.save("screenshot_2k.png")

    def show_screenshot_for_annotation(self, screenshot):
        annotation_win = tk.Toplevel(self.master)
        annotation_win.title("Annotate Screenshot")

        # Convert the screenshot to a Tkinter-compatible image format
        self.tk_screenshot = ImageTk.PhotoImage(image=screenshot)

        canvas = tk.Canvas(
            annotation_win,
            width=self.tk_screenshot.width(),
            height=self.tk_screenshot.height(),
        )
        canvas.pack()

        # Display the screenshot on the canvas
        canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_screenshot)

        # Bind mouse events for drawing bounding boxes
        self.start_x = None
        self.start_y = None
        app = self.AnnotationApp(self.master)
        canvas.bind("<ButtonPress-1>", lambda event: app.on_button_press(event, canvas))
        canvas.bind("<B1-Motion>", lambda event: app.on_move_press(event, canvas))
        canvas.bind(
            "<ButtonRelease-1>",
            lambda event: app.on_button_release(event, screenshot, annotation_win),
        )

    class AnnotationApp:
        def __init__(self, master):
            self.master = master

        def on_button_press(self, event, canvas):
            self.start_x = event.x
            self.start_y = event.y
            self.rect = canvas.create_rectangle(
                self.start_x, self.start_y, self.start_x, self.start_y, outline="red"
            )

        def on_move_press(self, event, canvas):
            curX, curY = event.x, event.y
            canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

        def on_button_release(self, event, screenshot, annotation_win):
            # Save the screenshot and annotations
            bbox = (self.start_x, self.start_y, event.x, event.y)
            # annotated_area = screenshot.crop(bbox)
            # annotated_area.save(os.path.join(os.getcwd(), "annotated_screenshot.png"))
            # annotation_win.destroy()
            # self.master.deiconify()


if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenCaptureApp(root)
    try:
        root.mainloop()
    except Exception as e:
        # Handle exceptions that occur before entering or during the main loop
        exc_type, exc_value, exc_traceback = sys.exc_info()
        messagebox.showerror(
            "Application Error",
            "An unexpected error occurred: \n"
            + "".join(traceback.format_exception(exc_type, exc_value, exc_traceback)),
        )
