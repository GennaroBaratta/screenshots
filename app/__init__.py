import sys
import tkinter
from tkinter import messagebox
import traceback

from main import ScreenCaptureApp


if __name__ == "__main__":
    root = tkinter.Tk()
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
