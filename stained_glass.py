import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from skimage.segmentation import slic
from skimage.segmentation import mark_boundaries
from skimage.measure import regionprops


# converts a picture to a stained glass effect using SLIC, with a customisable number of colours
def stain_glass(img, num_segments, compactness):
    # convert to float
    img = img.astype(np.float32)
    # apply SLIC and extract (approximately) the supplied number of segments
    segments = slic(
        img, n_segments=num_segments, compactness=compactness, enforce_connectivity=True
    )
    output = img.copy().astype(np.uint8)
    # make whole segment the same colour
    for i in range(3):
        regions = regionprops(segments, img[:, :, i])
        for r in regions:
            pixels = r.coords
            output[pixels[:, 0], pixels[:, 1], i] = int(r.mean_intensity)
    return output


if __name__ == "__main__":
    # load the image and show it
    image = plt.imread("test_photo.jpg")
    # apply SLIC and extract (approximately) the supplied number of segments
    stained_glass = stain_glass(image, 500, 10)
    plt.imshow(stained_glass)
    plt.axis("off")
    plt.show()
    # save image
