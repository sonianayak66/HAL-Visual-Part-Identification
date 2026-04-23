import cv2
import numpy as np
import os
import random

input_folder = "bracket"
output_folder = "dataset_aug/bracket"

os.makedirs(output_folder, exist_ok=True)

def rotate_with_white_bg(image, angle):
    h, w = image.shape[:2]
    
    # rotation matrix
    M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1)

    # create white background
    rotated = cv2.warpAffine(
        image,
        M,
        (w, h),
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255,255,255)
    )

    return rotated


def change_lighting(image):
    alpha = random.uniform(0.8,1.2)   # contrast
    beta = random.randint(-20,20)     # brightness
    new = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
    return new


for file in os.listdir(input_folder):

    image_path = os.path.join(input_folder, file)
    image = cv2.imread(image_path)

    if image is None:
        continue

    name = file.split(".")[0]

    for i in range(10):

        angle = random.randint(0,360)
        aug = rotate_with_white_bg(image, angle)

        aug = change_lighting(aug)

        output_path = os.path.join(output_folder, f"{name}_aug{i}.jpg")
        cv2.imwrite(output_path, aug)

print("Augmentation completed")