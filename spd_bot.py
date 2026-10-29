import subprocess
import os
import cv2
import numpy as np
import time

# Optional: specify device if multiple are connected
DEVICE = "AYAV6R3717009392"  # e.g., "ABC123456789"
ADB_PATH = "..\\adb.exe"  # Adjust if adb is not in PATH
DEBUG = True

# Temporary path on the device
DEVICE_TMP_PATH = "/sdcard/temp_screenshot.png"

ATTACK_ICON_POSITION = (1062, 2023)  # Position for attack icon
ENEMY_IN_SIGHT_ICON_POSITION = (1000, 200)  # Position for enemy in sight icon
ATTACK_ICONS_COLOR = (154, 45, 45)

CLOCK_ICON_POSITION = (55, 2285)  # Position for clock icon
CLOCK_ICON_COLOR = (226, 230, 219)

LOW_HEALTH_POSITION = (265, 20)
HEALTH_COLOR = (153, 46, 46)

FOOD_POSITION = (555, 2289)
FOOD_COLOR = (217, 175, 200)

SATIETY_ICON_POSITION = (259, 77)  # Position for satiation icon
STARVING_ICON_COLOR = (204, 12, 12)  # Color for starving icon
HUNGRY_ICON_COLOR = (242, 115, 24)  # Color for hungry icon



def run_adb_cmd(cmd):
    """
    Runs an ADB command with the specified arguments.

    Args:
        cmd (list): List of command arguments to pass to adb.

    Returns:
        str: The standard output from the adb command.
    """
    full_cmd = ADB_PATH + " " + cmd
    result = subprocess.run(ADB_PATH + " " + cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    if result.returncode != 0:
        raise RuntimeError(f"ADB command failed: {result.stderr.strip()}")
    
    return result.stdout.strip()

def take_screenshot(filename: str):
    """
    Takes a screenshot from the connected Android device via USB
    and saves it as `filename` on the PC.
    
    Args:
        filename (str): Name of the screenshot file to save (e.g., 'screen.png')
    """
    # 1. Take screenshot on the device
    run_adb_cmd("shell screencap -p " + DEVICE_TMP_PATH)

    # 2. Pull screenshot to PC
    run_adb_cmd("pull " + DEVICE_TMP_PATH + " " + filename)

    # 3. Remove screenshot from device
    run_adb_cmd("shell rm " + DEVICE_TMP_PATH)

    # # 4. Verify file exists
    # if os.path.exists(filename):
    #     if DEBUG: print(f"Screenshot saved successfully as {filename}!")
    # else:
    #     if DEBUG: print(f"Failed to save screenshot as {filename}.")
    # if DEBUG: print(f"Screenshot saved successfully as '{filename}'")

def click(x: int, y: int):
    """
    Simulates a tap on the connected Android device at the specified coordinates.

    Args:
        x (int): X coordinate for the tap.
        y (int): Y coordinate for the tap.
    """
    run_adb_cmd(f"shell input tap {x} {y}")

def find(icon_path: str, screenshot_path: str, threshold: float = 0.8):
    """
    Finds the icon in the screenshot and returns the center coordinates (x, y).
    
    Args:
        icon_path (str): Path to the small template image (icon) to find.
        screenshot_path (str): Path to the screenshot image.
        threshold (float): Matching threshold (0-1), default is 0.8.
        
    Returns:
        tuple: (x, y) coordinates of the center of the found icon, or None if not found.
    """
    # Load images
    screenshot = cv2.imread(screenshot_path)
    icon = cv2.imread(icon_path)
    
    if screenshot is None:
        raise FileNotFoundError(f"Screenshot not found: {screenshot_path}")
    if icon is None:
        raise FileNotFoundError(f"Icon image not found: {icon_path}")
    
    # Convert to grayscale for better matching
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    icon_gray = cv2.cvtColor(icon, cv2.COLOR_BGR2GRAY)
    
    # Template matching
    res = cv2.matchTemplate(screenshot_gray, icon_gray, cv2.TM_CCOEFF_NORMED)
    
    # Find the best match location
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    
    if max_val < threshold:
        # Not found
        return None
    
    top_left = max_loc
    h, w = icon_gray.shape
    center_x = top_left[0] + w // 2
    center_y = top_left[1] + h // 2
    
    return (center_x, center_y)

def check_position(image_path: str, max_width: int = 1200, max_height: int = 800):
    """
    Opens an image and allows the user to click on it.
    Prints the coordinates of the clicked point in the original image.

    Args:
        image_path (str): Path to the image to check.
        max_width (int): Maximum width of displayed window.
        max_height (int): Maximum height of displayed window.
    """
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Image not found: {image_path}")
        return

    orig_height, orig_width = img.shape[:2]

    # Compute scaling factor to fit screen
    scale = min(max_width / orig_width, max_height / orig_height, 1.0)
    display_img = cv2.resize(img, (int(orig_width * scale), int(orig_height * scale)))

    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # Map back to original image coordinates
            orig_x = int(x / scale)
            orig_y = int(y / scale)
            b, g, r = img[orig_y, orig_x]
            print(f"Clicked at: ({orig_x}, {orig_y}) with color (R:{r}, G:{g}, B:{b})")
            # Draw a circle on display image
            cv2.circle(display_img, (x, y), 5, (0, 0, 255), -1)
            cv2.imshow("Image", display_img)

    cv2.imshow("Image", display_img)
    cv2.setMouseCallback("Image", click_event)

    print("Click anywhere on the image to get coordinates. Press ESC to exit.")

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break

    cv2.destroyAllWindows()

def is_enemy_in_sight(image_path: str = "screenshot.png"):
    img = cv2.imread(image_path)
    b, g, r = img[ENEMY_IN_SIGHT_ICON_POSITION[1], ENEMY_IN_SIGHT_ICON_POSITION[0]]
    if (r, g, b) == ATTACK_ICONS_COLOR:
        if DEBUG: print("Enemy is in sight.")
        return True
    else:
        if DEBUG: print("Enemy is not in sight.")
        return False

def is_attack_ready(image_path: str = "screenshot.png"):
    img = cv2.imread(image_path)
    b, g, r = img[ATTACK_ICON_POSITION[1], ATTACK_ICON_POSITION[0]]
    if (r, g, b) == ATTACK_ICONS_COLOR:
        if DEBUG: print("Attack is ready.")
        return True
    else:
        if DEBUG: print("Attack is not ready.")
        return False

def is_low_health(image_path: str = "screenshot.png"):
    img = cv2.imread(image_path)
    b, g, r = img[LOW_HEALTH_POSITION[1], LOW_HEALTH_POSITION[0]]
    if (r, g, b) != HEALTH_COLOR:
        if DEBUG: print("Low health detected.")
        return True
    else:
        if DEBUG: print("Health is good.")
        return False

def is_our_turn(image_path: str = "screenshot.png"):
    img = cv2.imread(image_path)
    b, g, r = img[CLOCK_ICON_POSITION[1], CLOCK_ICON_POSITION[0]]
    if (r, g, b) == CLOCK_ICON_COLOR:
        if DEBUG: print("It's our turn.")
        return True
    else:
        if DEBUG: print("It's not our turn.")
        return False
    
def is_starving(image_path: str = "screenshot.png"):
    img = cv2.imread(image_path)
    b, g, r = img[SATIETY_ICON_POSITION[1], SATIETY_ICON_POSITION[0]]
    if (r, g, b) == STARVING_ICON_COLOR:
        if DEBUG: print("Character is starving.")
        return True
    else:
        if DEBUG: print("Character is not starving.")
        return False

def is_food_available(image_path: str = "screenshot.png"):
    img = cv2.imread(image_path)
    b, g, r = img[FOOD_POSITION[1], FOOD_POSITION[0]]
    if (r, g, b) == FOOD_COLOR:
        if DEBUG: print("Food is available.")
        return True
    else:
        if DEBUG: print("Food is not available.")
        return False

def is_hungry(image_path: str = "screenshot.png"):
    img = cv2.imread(image_path)
    b, g, r = img[SATIETY_ICON_POSITION[1], SATIETY_ICON_POSITION[0]]
    if (r, g, b) == HUNGRY_ICON_COLOR:
        if DEBUG: print("Character is hungry.")
        return True
    else:
        if DEBUG: print("Character is not hungry.")
        return False

def skip_turn():
    click(CLOCK_ICON_POSITION[0], CLOCK_ICON_POSITION[1])
    if DEBUG: print("Skipped turn.")

def attack():
    click(ATTACK_ICON_POSITION[0], ATTACK_ICON_POSITION[1])
    if DEBUG: print("Attacked.")

def sleep():
    run_adb_cmd(f"shell input swipe {CLOCK_ICON_POSITION[0]} {CLOCK_ICON_POSITION[1]} {CLOCK_ICON_POSITION[0]} {CLOCK_ICON_POSITION[1]} 1000")
    if DEBUG: print("Fallen asleep.")

def eat():
    click(FOOD_POSITION[0], FOOD_POSITION[1])
    if DEBUG: print("Ate food.")

def wait_for_our_turn():
    if DEBUG: print("Waiting for our turn...")
    while True:
        take_screenshot("screenshot.png")
        if is_our_turn("screenshot.png"):
            break

def attack_until_done():
    while True:
        wait_for_our_turn()
        take_screenshot("screenshot.png")
        if not is_enemy_in_sight("screenshot.png"):
            if DEBUG: print("Enemy no longer in sight. Ending attack.")
            break
        if not is_attack_ready("screenshot.png"):
            if DEBUG: print("Attack not ready. Waiting...")
            sleep()
        else:
            attack()


def eat_if_needed():
    take_screenshot("screenshot.png")
    if is_low_health("screenshot.png") and (is_starving("screenshot.png")):
        if DEBUG: print("Low health detected! Eating...")
        eat()
        time.sleep(1)  # Wait for eating action to complete
        take_screenshot("screenshot.png")
        if not is_food_available("screenshot.png"):
            if DEBUG: print("Food is no longer available after eating!")
            return False
    return True

def manual_ROW_farm():
    while True:
        print()
        print()
        print()
        print()
        print("Starting new cycle...")
        take_screenshot("screenshot.png")
        while not is_enemy_in_sight("screenshot.png"):
            sleep()
            wait_for_our_turn()
            take_screenshot("screenshot.png")
        print("Enemy in sight! Starting attack sequence...")
        attack_until_done()
        print("Attack sequence complete.")
        eat_if_needed()

def ghost_ROW_farm():
    while True:
        print()
        print()
        print()
        print()
        print("Starting new cycle...")
        take_screenshot("screenshot.png")
        while not is_enemy_in_sight("screenshot.png"):
            sleep()
            wait_for_our_turn()
            eat_if_needed()
            take_screenshot("screenshot.png")
        print("Enemy in sight! Starting attack sequence...")
        attack_until_done()
        print("Attack sequence complete.")
        take_screenshot("screenshot.png")
        eat_if_needed()


# Example usage
if __name__ == "__main__":
    
    ghost_ROW_farm()

    # take_screenshot("screenshot.png")
    # check_position("screenshot.png")
    # is_starving("screenshot.png")
    # is_attack_ready("screenshot.png")
    # is_our_turn("screenshot.png")
    # is_enemy_in_sight("screenshot.png")
    # is_low_health("screenshot.png")
    # is_hungry("screenshot.png")
    # is_food_available("screenshot.png")
    