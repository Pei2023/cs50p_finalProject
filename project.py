import argparse
import textwrap
import sys
import re
import inflect
from os import path
from PIL import Image, ImageDraw, ImageFont

indexes = ["first", "second", "third", "forth"]


def main():
    directories = check_photo_directories_and_sizes()
    width, height = get_min_sizes(directories)
    font_size = set_font_size(width, height)
    texts = get_description_texts(width, height, font_size)
    file_name = get_new_image_name()
    descriptions = create_description_objects(texts, width, height, font_size)
    cropped_photos = adjust_image_sizes(directories, width, height)
    combined = combine_image_descriptions(cropped_photos, descriptions, height)
    connected = connect_images(combined, width, height)
    connected.save(f"{file_name}.jpg")


def check_photo_directories_and_sizes():
    """
    Ensure user specify the directory/filename of images when executing the program. Verify that the specified directory exists and that the images meet the required size.

    :raise FileNotFoundError: If the directory/filename of image doesn't exist.
    :return: A tuple containing the four directories of images.
    :rtype: tuple of str
    """
    global indexes
    parser = argparse.ArgumentParser()
    parser.add_argument(f"{indexes[0]}Photo", help=f"The directory of the {indexes[0]} photo")
    parser.add_argument(f"{indexes[1]}Photo", help=f"The directory of the {indexes[1]} photo")
    parser.add_argument(f"{indexes[2]}Photo", help=f"The directory of the {indexes[2]} photo")
    parser.add_argument(f"{indexes[3]}Photo", help=f"The directory of the {indexes[3]} photo")
    args = parser.parse_args()

    p = inflect.engine()
    # Check whether the image directories or file names are valid
    invalid = []
    for photoKey in vars(args):
        if not path.exists(vars(args)[photoKey]):
            invalid.append(photoKey)

    if len(invalid) > 0:
        sys.exit(f"The directory of the {p.join(invalid)} {p.plural_verb('was', len(invalid))} not correct.")

    # Check whether the image size filfilled.
    unfulfilled = []
    for photoKey in vars(args):
        with Image.open(vars(args)[photoKey]) as img:
            if not img.width*img.height >= int(23737.5*4):
                unfulfilled.append(photoKey)

    if len(unfulfilled) > 0:
        sys.exit(f"The area of image should be at least {int(23737.5*4)} pixels, but the {p.join(unfulfilled)} did not meet.")

    return (getattr(args, f"{indexes[0]}Photo"), getattr(args, f"{indexes[1]}Photo"), getattr(args, f"{indexes[2]}Photo"), getattr(args, f"{indexes[3]}Photo"))


def set_font_size(width, height):
    """
    Set the font size.
    To ensure proportionality between the image size and font size, the ratio between the image and font is set to 593.4. This means that the size of images is 593.4 times larger than the size of one character.

    :param width: Width of the unified image size.
    :param height: Height of the unified image size.
    :type width: int
    :type height: int
    :return: The font size of each character
    :rtype: int

    """
    font_size = ((width*height)/593.4)**0.5
    return int(font_size)


def get_description_texts(width, height, font_size):
    """
    Prompt user for entering the description of each image and verify the word number doesn't exceed the limitation.

    :param width: Width of unified image size.
    :param height: Height of unified image size.
    :type width: int
    :type height: int
    :return: A list containing four description texts.
    :rtype: list of str
    """
    global indexes
    word_limit = (width*height/5)/(font_size**2)
    descriptions = []
    for i in range(4):
        while True:
            description = input(f"Please fill in the description for the {indexes[i]} photo (number of characters <= {int(word_limit)}):\n")
            if len(description) > word_limit:
                print(f"There are {len(description)} characters. Please enter fewer words.")
            else:
                print("Accepted")
                descriptions.append(description)
                break
    return descriptions


def get_new_image_name():
    """
    Prompt user for naming the new image file. Only alphabet, number and underscore are allowed.

    :return: The name of the new output image.
    :rtype: str

    """
    while True:
        name = input("Name the new image file (only alphabet, number and underscore are accepted): ")
        if  re.search(r"^[\w_]+$", name):
            return name


def get_min_sizes(directories):
    """
    Find the minimum width and minimum height among the four images.

    :param directories: A tuple containing the four directories of images.
    :type directories: tuple
    :return: A tuple containing the minimum width and minimum height.
    :rtype: tuple of int
    """
    widthes = []
    heights = []

    for directory in directories:
        with Image.open(directory) as img:
            width, height = img.size
            widthes.append(width)
            heights.append(height)
    min_width = min(widthes)
    min_height = min(heights)
    return (min_width, min_height)


def create_description_objects(texts, img_width, img_height, font_size):
    """
    Create four description objects for text regions, each of wich composef of transparent black background and white text.

    :param texts: A list containing four description texts.
    :param img_width: The unified width of the images, and it's used to define the width of the text region.
    :param img_height: The unified height of the images, and it's used to define the height of the text region.
    :type texts: list of str
    :type img_width: int
    :type img_height: int
    :return: A list containing four description objects for the text region.
    :rtype: list of description objects

    """
    contents = []
    font = ImageFont.truetype("GenYoGothic-B.ttc", font_size)
    text_margin = font_size/4

    for text in texts:
        background = Image.new("RGBA",(img_width, int(img_height/5)), (0, 0, 0, 175))
        content = ImageDraw.Draw(background)

        if len(text) > 0:
            text_length = font.getlength(text)
            charsize = text_length / len(text)
            lines = textwrap.wrap(text, width=int((img_width/charsize)-2))

            y = font_size/4
            for line in lines:
                content.multiline_text((font_size/2, y), line, font=font, fill=(255, 255, 255))
                y += font.size + font_size/4
        contents.append(background)

    return contents


def adjust_image_sizes(directories, min_width, min_height):
    """
    Crop each image into the unified size.

    :param directories: A tuple containing the four directories of images.
    :param min_width: The minimum width among four images. It's used to unify the width of four images.
    :param min_height: The minium height among four images. It's used to unify the height of of four images.
    :type directories: tuple of str
    :type min_width: int
    :type min_height: int
    :return: A list containing four images which size are unified.
    :rtype: list of image objects

    """
    cropped_photos = []

    for directory in directories:
        with Image.open(directory) as img:
            left = (img.width - min_width) / 2
            upper = (img.height - min_height) / 2
            right = left + min_width
            lower = upper + min_height
            cropped_photo = img.crop((left, upper, right, lower))
            cropped_photos.append(cropped_photo)
    return cropped_photos


def combine_image_descriptions(cropped, descriptions, unified_height):
    """
    Paste the text regions onto the images.

    :param cropped: A list containing four images with unified sizes.
    :param descriptions: A list containing four description objects for the text regions.
    :param unified_height: The unified height of the images.
    :type cropped: list of image objects
    :type descriptions: list of description objects
    :type unified_height: int
    :return: A list containing four image objects composed of images and text regions.
    :rtype: list of image objects

    """
    for i in range(4):
        cropped[i].paste(descriptions[i], (0, int(unified_height*4/5)), mask=descriptions[i])
    return cropped


# Connect the image up
def connect_images(combined, width, height):
    """
    Connect four image objects composed of images and text regions.

    :param combined: A list containing four image objects composed of images and text regions.
    :param width: The unified width of each image object
    :param height: The unified height of each image object
    :type combined: list of image objects
    :type width: int
    :type height: int
    :return: The final combined image object
    :rtype: image object

    """
    connected = Image.new("RGB", ((width+1)*4, height))
    for i in range(4):
        connected.paste(combined[i], (i*(width+1), 0))
    return connected


if __name__ == "__main__":
    main()
