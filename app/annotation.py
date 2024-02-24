# annotation.py
import os
from tkinter import Canvas, Toplevel
from PIL import Image, ImageDraw, ImageFont


class AnnotationTool:
    def __init__(self, master: Toplevel, canvas: Canvas, screenshot_path: str):
        self.canvas = canvas
        self.master = master
        self.screenshot_path = screenshot_path
        self.image = Image.open(screenshot_path)
        self.draw = ImageDraw.Draw(self.image)
        self.annotations = []
        canvas.update()

    def add_rectangle(
        self, start_x, start_y, end_x, end_y, label="aaa", outline="red", width=2
    ):
        """
        Draws a rectangle on the screenshot with an optional label.
        """
        # Draw rectangle on the image
        self.draw.rectangle(
            [start_x, start_y, end_x, end_y], outline=outline, width=width
        )

        if label:
            self.add_text((start_x + end_x) // 2, start_y - 10, label, fill=outline)

        self.annotations.append(
            {
                "type": "rectangle",
                "coordinates": [start_x, start_y, end_x, end_y],
                "label": label,
            }
        )

    def add_text(self, x, y, text, fill="black", font=None):
        """
        Adds text annotation at the specified coordinates.
        """
        if not font:
            font = ImageFont.load_default()

        # Adjusting text position for better visibility
        # For simplicity, we'll assume the text starts at (0, 0) to get its dimensions
        # bbox = self.draw.textbbox((x, y), text, font=font)
        # text_x = bbox[2] - bbox[0]
        # text_y = bbox[3] - bbox[1]

        self.draw.text((x, y), text, fill=fill, font=font)
        self.annotations.append({"type": "text", "position": [x, y], "text": text})

    def save_annotated_image(self, save_path):
        """
        Saves the annotated image to a specified path.
        """
        self.image.save(save_path)
        return save_path

    def on_button_press(self, event):
        # Implement on_button_press logic for annotation start
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, outline="red"
        )

    def on_move_press(self, event):
        # Implement on_move_press logic for updating annotation drawing
        curX, curY = event.x, event.y
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def on_annotation_release(self, event, win: Toplevel):
        # Handle the finalization of an annotation (e.g., saving the annotated image)
        end_x, end_y = event.x, event.y
        self.add_rectangle(
            self.start_x, self.start_y, end_x, end_y, label="Your Label Here"
        )
        annotated_image_path = self.save_annotated_image("annotated_screenshot.png")
        print(f"Annotated image saved at {annotated_image_path}")
        os.remove(self.screenshot_path)  # Cleanup
        self.master.destroy()
        win.deiconify()
