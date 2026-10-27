import gc
import os
import sys

APP_DIR = "/system/apps/slideshow"
sys.path.insert(0, APP_DIR)
os.chdir(APP_DIR)

badge.mode(HIRES | VSYNC)

screen.font = font.nope
screen.antialias = image.X2

SLIDE_MS = 7000  # time each photo stays on screen

# list the photo PNGs, skipping macOS sidecar files and dotfiles
image_files = [
    file for file in os.listdir("images")
    if not file.startswith(("__", ".")) and file.endswith(".png")
]
total_files = len(image_files)

if total_files == 0:
    fatal_error("No photos found!", "Enter disk mode and copy PNGs to /apps/slideshow/images")


def clamp_index(i):
    return i % total_files


# only one decoded image is ever held in memory at a time, since the full set
# is too big to preload on a badge with this many (or this large) photos
current_image = None
index = 0
paused = False
slide_started_at = badge.ticks


def show(i):
    global index, current_image, slide_started_at

    index = clamp_index(i)
    current_image = None
    gc.collect()

    current_image = image.load(f"images/{image_files[index]}")
    slide_started_at = badge.ticks


show(index)


def update():
    global paused, slide_started_at

    if badge.pressed(BUTTON_LEFT):
        show(index - 1)

    if badge.pressed(BUTTON_RIGHT):
        show(index + 1)

    if badge.pressed(BUTTON_SELECT):
        paused = not paused

    if not paused and (badge.ticks - slide_started_at) > SLIDE_MS:
        show(index + 1)

    screen.blit(current_image, rect(0, 0, current_image.width, current_image.height), rect(0, 0, screen.width, screen.height))

    if paused:
        label = "PAUSED"
        w, _ = screen.measure_text(label)
        screen.pen = color.rgb(0, 0, 0, 120)
        screen.shape(shape.rounded_rectangle((screen.width / 2) - (w / 2) - 8, screen.height - 22, w + 16, 20, 6))
        screen.pen = color.rgb(255, 210, 60)
        screen.text(label, (screen.width / 2) - (w / 2), screen.height - 20)


run(update)
