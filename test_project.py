import project
import pytest
import argparse
from PIL import Image
from unittest import mock


@mock.patch("argparse.ArgumentParser.parse_args")
def test_check_photo_directories_and_sizes(mock_parse_args):
    """
    Test that the function returns the directories of four images if they exist.

    :param mock_parse_args: The mocked parse_args function, which is used to manipulate user input.
    :type mock_parse_args: MagicMock

    """
    mock_parse_args.return_value = argparse.Namespace(firstPhoto='S1.jpg', secondPhoto='S2.jpg', thirdPhoto='S3.jpg', forthPhoto='S4.jpg')
    with mock.patch("os.path.exists", return_value=True):
        with mock.patch("PIL.Image.open") as mock_open:
            fake_photo_size = [(1108, 1477), (1108, 1477), (1477, 1108), (1477, 1108)]
            mock_open.side_effect = [Image.new("RGBA", size) for size in fake_photo_size]
            assert project.check_photo_directories_and_sizes() == ('S1.jpg', 'S2.jpg', 'S3.jpg', 'S4.jpg')


@mock.patch("argparse.ArgumentParser.parse_args")
def test_check_photo_directories_and_sizes_fileNotExist(mock_parse_args):
    """
    Test that SystemExit is raised if any of the director of the four images doesn't exist.

    :param mock_parse_args: The mocked directories of the four images.
    :type mock_parse_args: MagicMock

    """
    mock_parse_args.return_value = argparse.Namespace(firstPhoto='S1.jpg', secondPhoto='S2.jpg', thirdPhoto='S3.jpg', forthPhoto='S4.jpg')
    with mock.patch("os.path.exists", return_value=False):
        with pytest.raises(SystemExit):
            project.check_photo_directories_and_sizes()


def test_check_photo_directories_and_sizes_imageSizeTooSmall():
    """
    Test that SystemExit is raised if any of the image area smaller than 94950 (pixel*pixel).

    """
    with mock.patch("PIL.Image.open") as mock_open:
        fake_photo_size = [(308, 308), (1108, 1477), (400, 400), (1477, 1108)]
        mock_open.side_effect = [Image.new("RGBA", size) for size in fake_photo_size]
        with pytest.raises(SystemExit):
            project.check_photo_directories_and_sizes()


def test_set_font_size():
    """
    Test that the function returns the font size.
    This test ensures that the font size is correctly calculated based on the width and height of the image.

    """
    assert project.set_font_size(150, 150) == 6
    assert project.set_font_size(1108, 1477) == 52
    assert project.set_font_size(2000, 3000) == 100


def test_get_description_texts_chinese():
    """
    Test that within the character limit, the function returns a list of description texts, each containing non-ASCII characters.

    """
    with mock.patch("builtins.input", side_effect=['新加坡旅行', '新加坡的捷運', '簡單清楚的道路標示', '漂亮且舒適的新加坡國家圖書館']):
        assert project.get_description_texts(1108, 1108, 45) == ['新加坡旅行', '新加坡的捷運', '簡單清楚的道路標示', '漂亮且舒適的新加坡國家圖書館']


def test_get_description_texts_english():
    """
    Test that within the character limit, the function returns a list of description texts, each containing ASCII characters.

    """
    with mock.patch("builtins.input", side_effect=['THIS', 'IS', 'CS50P', 'PROJECT']):
        assert project.get_description_texts(1108, 1108, 45) == ['THIS', 'IS', 'CS50P', 'PROJECT']


def test_get_description_texts_empty():
    """
    Test that the function returns a list of description texts even if each description text is empty.

    """
    with mock.patch("builtins.input", side_effect=['', '', '', '']):
        assert project.get_description_texts(1108, 1108, 45) == ['', '', '', '']


def test_get_description_texts_small_images():
    """
    Test that the function returns a list of description texts within the character limit even if the image size is small.

    """
    with mock.patch("builtins.input") as mock_input:
        mock_input.side_effect = ["CS50", "Python", "今天", "Python"]
        assert project.get_description_texts(192, 240, 9) == ["CS50", "Python", "今天", "Python"]


def test_get_new_image_name_only_alphabet_number():
    """
    Test that the function returns a string of texts if the input texts contain only alphabelt, number and underscore.

    """
    with mock.patch("builtins.input", return_value="cs50p_"):
        assert project.get_new_image_name() == "cs50p_"


def test_get_new_image_name_only_alphabet_number_underscore_allowed():
    """
    Test that the function returns a string containing only alphabet, number and underscore.
    If the text contains characters other than alphabet, number and underscore, the function shouldn't accept it and should continue to prompt the user until a valid file name is input.

    """
    with mock.patch("builtins.input", side_effect=["", "@@", "A!","test test", "!A", "cs50_p"]):
        assert project.get_new_image_name() == "cs50_p"


def test_get_min_sizes():
    """
    Test that the function returns a tuple containing the minimum width and minimum height among the four image objects provided in the directories.

    """
    fake_directories = ["fake_1", "fake_2", "fake_3", "fake_4"]
    with mock.patch("PIL.Image.open") as mock_open:
        fake_photo_sizes = [(150, 1477), (1108, 1477), (1477, 150), (1477, 1108)]
        mock_open.side_effect = [Image.new("RGBA", size) for size in fake_photo_sizes]
        assert project.get_min_sizes(fake_directories) == (150, 150)


def test_adjust_image_sizes_check_adjusted_sizes():
    """
    Test that the function correctly adjusts the sizes of image objects based on the minimum width and minimum height.

    """
    fake_directories = ["fake_1", "fake_2", "fake_3", "fake_4"]
    with mock.patch("PIL.Image.open") as mock_open:
        mock_open.side_effect = [
            Image.new("RGBA", (150, 1477)),
            Image.new("RGBA", (1108, 1477)),
            Image.new("RGBA", (1477, 150)),
            Image.new("RGBA", (1477, 1108))
        ]
        adjusted_photos = project.adjust_image_sizes(fake_directories, 150, 150)

        for photo in adjusted_photos:
            assert photo.size == (150, 150)


def test_combine_image_descriptions():
    """
    Test that the function correctly combines the cropped images with their corresponding descriptions.

    """
    cropped_images = [mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock()]
    descriptions = [mock.Mock(), mock.Mock(), mock.Mock(), mock.Mock()]
    combined = project.combine_image_descriptions(cropped_images, descriptions, 200)

    for i in range(4):
        cropped_images[i].paste.assert_called_once_with(descriptions[i], (0, 160), mask=descriptions[i])

    assert combined == cropped_images


def test_connect_images():
    """
    Test that the function correctly connect each combined object, composed of the cropped image and the corresponding descriptions.
    The size of the connected image should be ((minHeight+1)x4, minHeight)

    """
    combined = [
        Image.new("RGB", (150, 150), color="red"),
        Image.new("RGB", (150, 150), color="green"),
        Image.new("RGB", (150, 150), color="blue"),
        Image.new("RGB", (150, 150), color="yellow")
    ]

    mock_connected = project.connect_images(combined, 150, 150)

    # Verify the size of connected images
    assert mock_connected.size == (604, 150)
    # Verify the four images are pasted
    assert mock_connected.getpixel((75, 75)) == (255, 0, 0)
    assert mock_connected.getpixel((226, 75)) == (0, 128, 0)
    assert mock_connected.getpixel((377, 75)) == (0, 0, 255)
    assert mock_connected.getpixel((528, 75)) == (255, 255, 0)
