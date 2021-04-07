import os
import sys
from PIL import Image

# rotates images by 90, 180, and 270 degrees and saves it.
def main(path):
    files = os.listdir(path)
    files = [file for file in files if file[-4:] == ".jpg"]

    images = []
    for file in files:
        try:
            image = Image.open(os.path.join(path, file))
            if not "_90" in file and not "_180" in file and not "_270" in file:
                for i in range(1,4):
                    fn = file.replace(".jpg", "_" + str(i*90) + ".jpg")
                    if not os.path.isfile(os.path.join(path, fn)):
                        rotate_img = image.rotate(i * 90)
                        rotate_img.save(os.path.join(path, fn), "JPEG")

        except OSError:
            pass

if __name__ == "__main__":
    main(sys.argv[1])
