# Tints a grayscale image with a hex color
from PIL import Image
import sys

def tint_image(image_path, tint_color, alpha):
    """
    Tint an image using per-channel multiplication with a given color.

    :param image_path: Path to the input image.
    :param tint_color: Tuple (R, G, B) for the tint color.
    :param alpha: Float between 0 and 1 for the tint strength.
    :return: Tinted image (Pillow Image object).
    """
    # Open the original image
    original = Image.open(image_path).convert("RGBA")
    r, g, b, a = original.split()  # Split into channels
    
    # Normalize tint color to 0-1 range and adjust by alpha
    tint_r, tint_g, tint_b = [c / 255 * alpha for c in tint_color]
    
    # Multiply each channel by the tint color
    r = r.point(lambda i: i * tint_r)
    g = g.point(lambda i: i * tint_g)
    b = b.point(lambda i: i * tint_b)
    
    # Merge channels back together
    tinted = Image.merge("RGBA", (r, g, b, a))
    
    return tinted

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python colorizer.py <image> <color>")
        sys.exit(1)
    image_path = sys.argv[1]
    color = sys.argv[2]
    print(f"Colorizing {image_path} with color {color}")
    # Convert hex color to RGB tuple
    color = tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
    print(f"RGB: {color}")
    # Tint the image
    tinted = tint_image(image_path, color, 1)
    # Save the tinted image in the same directory with "_tinted" appended to the filename
    tinted.save(image_path.replace(".png", "_tinted.png"))
