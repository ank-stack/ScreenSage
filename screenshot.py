import pyautogui
import os
import base64

def capture_screen(count):
    folder = "data"
    os.makedirs(folder,exist_ok=True)

    img = pyautogui.screenshot()

    filename = f"screenshot_{count}.png"
    path = os.path.join(folder,filename)

    img.save(path)

    return path

def image_to_base64(img_path):
    with open(img_path,"rb") as img_file:
        encoded_string = base64.b64encode(img_file.read())
        return encoded_string.decode("utf-8")
    
def base64_to_image(b64_string, output):
    with open(output,"wb") as img_file:
        img_file.write(base64.b64decode(b64_string))

if __name__ == "__main__":
    img_1 = capture_screen(1)
    base = image_to_base64(img_1)
    base64_to_image(base, "output.png")