import os

"""
### download image from url
url = "dfdfd"
os.system("wget -P ./garconsdata/JPEGImages")
"""
### generate readable data format from image
os.system("python3 image_process.py")

### detect face from image and save data
os.system('python3 test.py')

### detect the angle of each face
os.system("python code/test_hopenet.py")
"""
### remove tested image
filepath = "./garconsdata/JPEGImages"
filenamelist = os.listdir(filepath)
filename = filenamelist[0]
os.system("rm garconsdata/JPEGImages/%s" % filename)
"""
### return angle, xmax, ymax, ymin points for each face
os.system("python read.py")


### 2018.01 JAEHONG KIM
