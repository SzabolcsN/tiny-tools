import os
import random
from tkinter import Tk, filedialog, messagebox, Button, Label, Entry, StringVar, Frame
from PIL import Image, ImageFilter, ImageDraw
import numpy as np
import json

def select_folder_and_process(num_outputs, folder=None):
    if folder is None:
        root = Tk()
        root.withdraw()
        folder_selected = filedialog.askdirectory(title="Select Folder with Images")
        if not folder_selected:
            messagebox.showinfo("No folder selected", "Please select a folder.")
            return
        folder = folder_selected
    process_images(folder, num_outputs)

def process_images(folder, num_outputs=None):
    output_folder = os.path.join(folder, "output")
    os.makedirs(output_folder, exist_ok=True)
    supported_exts = (".png", ".jpg", ".jpeg")
    images = [f for f in os.listdir(folder) if f.lower().endswith(supported_exts)]
    if not images:
        messagebox.showinfo("No images found", "No PNG/JPG images found in the selected folder.")
        return
    # Load all images and resize to the size of the first image
    first_img = Image.open(os.path.join(folder, images[0])).convert("RGB")
    base_size = first_img.size
    loaded_images = [first_img]
    for img_name in images[1:]:
        img = Image.open(os.path.join(folder, img_name)).convert("RGB")
        if img.size != base_size:
            img = img.resize(base_size, Image.LANCZOS)
        loaded_images.append(img)
    if len(loaded_images) < 2:
        messagebox.showinfo("Not enough images", "Need at least 2 images.")
        return
    # Determine number of outputs
    try:
        num_outputs = int(num_outputs)
        if num_outputs < 1:
            num_outputs = 5
    except (TypeError, ValueError):
        num_outputs = 5
    feather_radius = 16
    num_layers = 10  # More layers for large cutouts
    for idx in range(num_outputs):
        new_img = Image.new("RGBA", base_size, (0, 0, 0, 0))
        # Estimate number of cutouts for a tiling pass
        tile_cutouts = tile_image_with_random_rects(base_size, feather_radius=feather_radius, overlap=feather_radius*2)
        n_cutouts = len(tile_cutouts) * num_layers
        for _ in range(n_cutouts):
            # Random size
            w = random.randint(100, 350)
            h = random.randint(100, 350)
            # Random center
            cx = random.randint(0, base_size[0] - 1)
            cy = random.randint(0, base_size[1] - 1)
            x1 = cx - w // 2
            y1 = cy - h // 2
            x2 = x1 + w
            y2 = y1 + h
            # Calculate intersection with image bounds
            ix1 = max(x1, 0)
            iy1 = max(y1, 0)
            ix2 = min(x2, base_size[0])
            iy2 = min(y2, base_size[1])
            if ix1 >= ix2 or iy1 >= iy2:
                continue  # Cutout is outside image
            # Crop region from source image
            src_img = random.choice(loaded_images)
            region = src_img.crop((ix1, iy1, ix2, iy2))
            # Create full feathered mask
            mask = Image.new("L", (w, h), 0)
            draw = ImageDraw.Draw(mask)
            draw.rectangle([
                feather_radius,
                feather_radius,
                w - feather_radius,
                h - feather_radius
            ], fill=255)
            mask = mask.filter(ImageFilter.GaussianBlur(radius=feather_radius))
            # Crop mask to intersection
            mask_cropped = mask.crop((ix1 - x1, iy1 - y1, ix2 - x1, iy2 - y1))
            region_rgba = region.convert("RGBA")
            region_rgba.putalpha(mask_cropped)
            temp = Image.new("RGBA", base_size, (0, 0, 0, 0))
            temp.paste(region_rgba, (ix1, iy1), region_rgba)
            new_img = Image.alpha_composite(new_img, temp)
        # Final tiling pass to fill any remaining gaps
        for (x1, y1, x2, y2) in tile_cutouts:
            src_img = random.choice(loaded_images)
            region = src_img.crop((x1, y1, x2, y2))
            w, h = x2 - x1, y2 - y1
            mask = Image.new("L", (w, h), 0)
            draw = ImageDraw.Draw(mask)
            draw.rectangle([
                feather_radius,
                feather_radius,
                w - feather_radius,
                h - feather_radius
            ], fill=255)
            mask = mask.filter(ImageFilter.GaussianBlur(radius=feather_radius))
            region_rgba = region.convert("RGBA")
            region_rgba.putalpha(mask)
            temp = Image.new("RGBA", base_size, (0, 0, 0, 0))
            temp.paste(region_rgba, (x1, y1), region_rgba)
            new_img = Image.alpha_composite(new_img, temp)
        # After all cutouts, composite onto white background
        final_img = Image.new("RGB", base_size, (255, 255, 255))
        final_img.paste(new_img, mask=new_img.split()[-1])
        out_path = os.path.join(output_folder, f"mixed_{idx+1}.png")
        final_img.save(out_path)
    print(f"Produced {num_outputs} images. Output in: {output_folder}")

# This function will fill the image with non-overlapping random rectangles, covering the whole area
def tile_image_with_random_rects(img_size, min_w=120, max_w=175, min_h=120, max_h=175, feather_radius=8, overlap=None):
    if overlap is None:
        overlap = feather_radius * 2
    width, height = img_size
    cutouts = []
    y = 0
    while y < height:
        x = 0
        row_h = None
        while x < width:
            max_w_actual = min(max_w, width - x)
            min_w_actual = min(min_w, max_w_actual)
            if max_w_actual <= 0 or min_w_actual <= 0:
                break
            w = random.randint(min_w_actual, max_w_actual) if max_w_actual > min_w_actual else max_w_actual
            max_h_actual = min(max_h, height - y)
            min_h_actual = min(min_h, max_h_actual)
            if max_h_actual <= 0 or min_h_actual <= 0:
                break
            h = random.randint(min_h_actual, max_h_actual) if max_h_actual > min_h_actual else max_h_actual
            x2 = min(x + w, width)
            y2 = min(y + h, height)
            cutouts.append((x, y, x2, y2))
            if row_h is None or (y2 - y) < row_h:
                row_h = y2 - y
            # Overlap by 'overlap' px
            x = x2 - overlap if (x2 - overlap) > x else x2
        # Overlap by 'overlap' px
        y += row_h - overlap if row_h and (y + row_h - overlap) > y else (row_h if row_h else 1)
    return cutouts

def generate_random_cutouts(img_size, min_cuts=3, max_cuts=8):
    width, height = img_size
    num_cuts = random.randint(min_cuts, max_cuts)
    cutouts = []
    attempts = 0
    max_attempts = 1000
    while len(cutouts) < num_cuts and attempts < max_attempts:
        w = random.randint(width // 8, width // 3)
        h = random.randint(height // 8, height // 3)
        x1 = random.randint(0, width - w)
        y1 = random.randint(0, height - h)
        x2 = x1 + w
        y2 = y1 + h
        rect = (x1, y1, x2, y2)
        if not any(rects_overlap(rect, c) for c in cutouts):
            cutouts.append(rect)
        attempts += 1
    return cutouts

def rects_overlap(a, b):
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return not (ax2 <= bx1 or ax1 >= bx2 or ay2 <= by1 or ay1 >= by2)

def main():
    root = Tk()
    root.title("Cut Images Together")
    root.geometry("500x220")
    Label(root, text="Cut random feathered parts from images\nand create new mixed images.", pady=10).pack()

    # Remember last folder
    config_path = os.path.join(os.path.expanduser("~"), ".cut_images_together_config.json")
    last_folder = ""
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                last_folder = json.load(f).get("last_folder", "")
        except Exception:
            last_folder = ""

    # Folder selection
    folder_frame = Frame(root)
    folder_frame.pack(pady=5)
    Label(folder_frame, text="Image folder:").pack(side="left")
    folder_var = StringVar(value=last_folder)
    folder_entry = Entry(folder_frame, textvariable=folder_var, width=40)
    folder_entry.pack(side="left", padx=5)
    def browse_folder():
        folder_selected = filedialog.askdirectory(title="Select Folder with Images")
        if folder_selected:
            folder_var.set(folder_selected)
    Button(folder_frame, text="Browse", command=browse_folder).pack(side="left")

    # Number of outputs
    Label(root, text="Number of output images:").pack()
    num_outputs_var = StringVar(value="5")
    num_outputs_entry = Entry(root, textvariable=num_outputs_var)
    num_outputs_entry.pack(pady=5)

    def start_mixing():
        folder = folder_var.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Error", "Please select a valid folder.")
            return
        # Save last folder
        try:
            with open(config_path, "w") as f:
                json.dump({"last_folder": folder}, f)
        except Exception:
            pass
        root.destroy()
        select_folder_and_process(num_outputs_var.get(), folder)

    Button(root, text="Start Mixing", command=start_mixing).pack(pady=20)
    root.mainloop()

if __name__ == "__main__":
    main()
