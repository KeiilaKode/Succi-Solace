import os
from PIL import Image

# --- CONFIGURATION ---
INPUT_FOLDER = r"C:\Users\yungh\Pictures\Succi Solace Game Mats\merch\merchant 3 frames"
OUTPUT_FOLDER = r"C:\Users\yungh\Pictures\Succi Solace Game Mats\merch\resized_transparent_m3"

TARGET_WIDTH = 810
TARGET_HEIGHT = 1080


def fit_and_make_transparent():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
        print(f"Created output directory: {OUTPUT_FOLDER}")

    valid_extensions = ('.png', '.jpg', '.jpeg')
    files = [f for f in os.listdir(INPUT_FOLDER) if f.lower().endswith(valid_extensions)]

    if not files:
        print(f"No image files found in {INPUT_FOLDER}!")
        return

    print(f"Processing {len(files)} frames with transparency...")

    count = 0
    for filename in files:
        input_path = os.path.join(INPUT_FOLDER, filename)
        output_path = os.path.join(OUTPUT_FOLDER, filename)

        try:
            with Image.open(input_path) as img:
                orig_width, orig_height = img.size

                # Scale proportionally to fit inside 810x1080
                ratio = min(TARGET_WIDTH / orig_width, TARGET_HEIGHT / orig_height)
                new_width = int(orig_width * ratio)
                new_height = int(orig_height * ratio)

                resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                # Create a blank RGBA canvas with full transparency (0 alpha)
                new_canvas = Image.new("RGBA", (TARGET_WIDTH, TARGET_HEIGHT), (0, 0, 0, 0))

                # Center the image on the canvas
                x_offset = (TARGET_WIDTH - new_width) // 2
                y_offset = (TARGET_HEIGHT - new_height) // 2

                # Paste using the image as its own mask to preserve transparency cleanly
                new_canvas.paste(resized_img, (x_offset, y_offset))

                # Save as PNG to retain the transparent channels
                out_file_png = os.path.splitext(output_path)[0] + ".png"
                new_canvas.save(out_file_png, "PNG")

                count += 1
                print(f"Processed transparent ({count}/{len(files)}): {filename}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print("All frames processed with transparency!")


if __name__ == "__main__":
    fit_and_make_transparent()