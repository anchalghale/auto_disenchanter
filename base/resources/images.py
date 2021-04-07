'''Module for parsing resources'''
import os
from functools import lru_cache
from glob import glob

try:
    import cv2
except ImportError:
    pass

__all__ = [
    'get_image_by_path',
    'get_image',
    'get_images_from_directory',
]


@lru_cache()
def get_image_by_path(file_path):
    '''Parses an image'''
    return cv2.imread(file_path, cv2.IMREAD_UNCHANGED)


@lru_cache()
def get_image(label):
    '''Parses an image'''
    return get_image_by_path(os.path.join('assets', 'images', f'{label}.png'))


@lru_cache()
def get_images_from_directory(directory_path):
    '''Parses all images inside a directory'''
    wildcard = os.path.join(directory_path, '*.png')
    images = {}
    for file_path in glob(wildcard):
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        images[file_name] = get_image(file_path)
    return images
