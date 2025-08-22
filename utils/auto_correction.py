#!/usr/bin/env python3
import os
import sys
import time
import math

# --- Configuration ---
CANVAS_WIDTH = 80
CANVAS_HEIGHT = 40
ASPECT_CORRECTION = 2.1  # Corrects for non-square character pixels
ROTATION_SPEED = 2.5     # Degrees to rotate per frame
FRAME_DELAY = 0.04       # Seconds between frames

# --- NEW: Character set for rendering density ---
# Represents coverage from 0% to 100%. Unicode block elements work best.
# You can customize these symbols for different artistic effects!
# For example: [' ', '.', ':', '-', '=', '#', '@']
DENSITY_CHARS = [' ', '░', '▒', '▓', '█']
SUB_SAMPLES = 2 # Check a 2x2 grid within each character cell (2*2=4 total samples)

def clear_screen():
    """Clears the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    """Main function to generate art and run the animation loop."""

    # 1. Define the original art
    text_block = [
        "H   H  GGG   CCC   AAA   L      ",
        "H   H G     C     A   A  L      ",
        "HHHHH G  GG C     AAAAA  L      ",
        "H   H G   G C     A   A  L      ",
        "H   H  GGG   CCC  A   A  LLLLL  "
    ]
    text_height = len(text_block)
    text_width = len(text_block[0])

    # 2. Find the geometric center of the art for rotation
    center_x = text_width / 2
    center_y = text_height / 2
    
    # 3. Initialize animation variables
    angle_deg = 0

    try:
        while True:
            canvas = [[' ' for _ in range(CANVAS_WIDTH)] for _ in range(CANVAS_HEIGHT)]
            
            # Pre-calculate sine and cosine for the *inverse* rotation
            angle_rad = math.radians(-angle_deg) # Negative angle for inverse
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            # --- NEW RASTERIZATION LOGIC ---
            # Scan every cell of the canvas
            for screen_y in range(CANVAS_HEIGHT):
                for screen_x in range(CANVAS_WIDTH):
                    
                    hits = 0
                    # Sub-sample within the cell for anti-aliasing
                    for i in range(SUB_SAMPLES):
                        for j in range(SUB_SAMPLES):
                            # Calculate the precise sub-sample coordinate
                            sub_x = screen_x + (i + 0.5) / SUB_SAMPLES
                            sub_y = screen_y + (j + 0.5) / SUB_SAMPLES

                            # --- Apply Inverse Transformations ---
                            # A. Translate to canvas center
                            cx = sub_x - CANVAS_WIDTH / 2
                            cy = sub_y - CANVAS_HEIGHT / 2
                            
                            # B. Correct aspect ratio (inverse)
                            cx /= ASPECT_CORRECTION

                            # C. Apply inverse rotation
                            rotated_x = cx * cos_a - cy * sin_a
                            rotated_y = cx * sin_a + cy * cos_a

                            # D. Translate back relative to the text's center
                            original_x = rotated_x + center_x
                            original_y = rotated_y + center_y

                            # Check if the inverse-mapped point falls on a character
                            # in the original text_block
                            if 0 <= original_y < text_height and 0 <= original_x < text_width:
                                if text_block[int(original_y)][int(original_x)] != ' ':
                                    hits += 1

                    # Choose a character based on the number of hits
                    if hits > 0:
                        total_samples = SUB_SAMPLES**2
                        density_index = math.ceil((hits / total_samples) * (len(DENSITY_CHARS) - 1))
                        canvas[screen_y][screen_x] = DENSITY_CHARS[density_index]

            # Render the final frame
            clear_screen()
            rendered_frame = "\n".join("".join(row) for row in canvas)
            print(rendered_frame, flush=True)
            # print(f"Location: Meyrin, CH | Angle: {angle_deg:.1f}° | Rasterizer: Sub-sample AA")

            angle_deg = (angle_deg + ROTATION_SPEED) % 360
            time.sleep(FRAME_DELAY)

    except KeyboardInterrupt:
        print("\n HET BELANGRIJKE SCRIPT IS HIERBIJ AFGEROND. FIJNE MIDDAG TOEGEWENST")
        sys.exit(0)

if __name__ == "__main__":
    main()