import pyautogui, os

def capture_screen(count):
    folder = "data"
    os.makedirs(folder,exist_ok=True)

    img = pyautogui.screenshot()

    filename = f"screenshot_{count}.png"
    path = os.path.join(folder,filename)

    img.save(path)

if __name__ == "__main__":
    capture_screen(1)