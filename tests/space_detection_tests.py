import pytest
import image_processing
import cv2
def test_main(cmdopt):
    assert True
    image = cv2.imread("box.png", 0)

    result = image_processing.thresholding(image)

    assert result is not None and result != image
