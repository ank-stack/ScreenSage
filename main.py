import os
import time
from screenshot import capture_screen,image_to_base64
from ai_clients import get_response_b64,get_response_img

data_list = os.listdir("data")

if len(data_list) == 0:
    data_num = 0
else:
    data_name = list(data_list[-1])
    data_num = int(data_name[11])

time.sleep(10)

imgage_path = capture_screen(data_num+1)
print(f"STATUS: Screenshot done \nImage Path: {imgage_path}")

b64 = image_to_base64(img_path=imgage_path)
print("STATUS: Image to Base64 done")

response = get_response_b64(img_b64=b64)
print("STATUS: Getting response done")

# Doesnt work with local files
# response = get_response_img(img=imgage_path)
# print("STATUS: Getting response done")

print(response)