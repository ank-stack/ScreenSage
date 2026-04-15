import os
from screenshot import capture_screen

data_list = os.listdir("data")

if len(data_list) == 0:
    data_num = 0
else:
    data_name = list(data_list[-1])
    data_num = int(data_name[11])

capture_screen(data_num+1)