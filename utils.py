import ffmpeg
import os
import random
from tqdm import tqdm

# Créez un dossier "input" et mettez-y vos vidéos
TEMP = r"temp"

# ICI, on peut changer les mots clés pour les vidéos
# Ces mots clés seront pris au hasard (5 mots clés par vidéo)
# Ils seront insérés dans le titre, la description et les tags de la vidéo (metadata)
KEYWORDS = [
    "makemoneyonline",
    "sidehustle",
    "makemoney",
    "makemoneyfromhome",
    "makemoneyonlinefree",
    "makemoneyfast",
    "makemoneyonlinefast",
    "hustle",
    "business",
    "entrepreneur",
    "entrepreneurship",
    "entrepreneurlife",
    "entrepreneurmindset",
    "entrepreneurquotes",
]


def get_metadata_dict(video_keywords_str):
    metadata_title = video_keywords_str.replace("_", " ")
    metadata_description = "#" + video_keywords_str.replace("_", " #")
    metadata_keywords = video_keywords_str.replace("_", ",")

    metadata_dict = {
        "metadata:g:0": f"title={metadata_title}",
        "metadata:g:1": f"description={metadata_description}",
        "metadata:g:2": f"keywords={metadata_keywords}",
    }
    return metadata_dict


def get_unique_name_and_metadata(str_effect=""):
    """Generate a unique name for the video

    Args:
        str_effect (str, optional): String to append to the name related to the effect. Defaults to "".

    Returns:
        str: Unique name for the video
    """

    video_keywords = random.sample(KEYWORDS, 5)
    unique_hash = random.randint(10000000, 99999999)
    video_keywords_str = "_".join(video_keywords)
    file_name = f"{unique_hash}_{video_keywords_str}_{str_effect}.mp4"

    metadata_dict = get_metadata_dict(video_keywords_str)

    return file_name, metadata_dict


def get_video_dimensions(path):
    """Get the dimensions of the video

    Args:
        path (str): Path to the video

    Returns:
        tuple: Height, Width dimensions of the video
    """
    probe = ffmpeg.probe(path)
    video_stream = next(
        (stream for stream in probe["streams"] if stream["codec_type"] == "video"), None
    )
    width = int(video_stream["width"])
    height = int(video_stream["height"])
    return width, height


def get_temp_video_path():
    """Gets the path to the video in the temp folder"""
    files = os.listdir(TEMP)
    if len(files) == 0:
        return None
    return os.path.join(TEMP, files[0])


def zoom_video(factor_percent=110):
    """Zoom in the video by a factor of factor_percent

    Args:
        factor_percent (int, optional): Zoom factor. Defaults to 110.

    Returns:
        bool: True if the video was successfully processed, False otherwise
    """

    path = get_temp_video_path()
    if not path:
        return False

    factor_str = str(factor_percent)
    video_name, metadata = get_unique_name_and_metadata(f"z_{factor_str}")
    res_file_name = os.path.join(TEMP, video_name)
    try:
        width, height = get_video_dimensions(path)
        (
            ffmpeg.input(path)
            .filter("scale", w=width * (factor_percent / 100), h=-1)
            .filter("crop", w=width, h=height)
            .output(
                res_file_name,
                loglevel="quiet",
                map_metadata=-1,
                map="0:a",  # map all audio streams
                **metadata,
            )
            .run()
        )
        os.remove(path)
        return True
    except ffmpeg.Error as e:
        print(e.stderr)
        return False


def flip_video():
    """Flip the video horizontally

    Returns:
        bool: True if the video was successfully processed, False otherwise
    """

    path = get_temp_video_path()
    if not path:
        return False

    # Flip is done after zooming, so we take the original video name and append the effect
    processed_video_name = os.path.basename(path)
    processed_video_effect = processed_video_name.split("_")[-1].split(".")[0]
    video_name, metadata = get_unique_name_and_metadata(f"{processed_video_effect}_f")
    res_file_name = os.path.join(TEMP, video_name)
    try:
        (
            ffmpeg.input(path)
            .filter("hflip")
            .output(
                res_file_name,
                loglevel="error",
                map_metadata=-1,
                map="0:a",  # map all audio streams
                **metadata,
            )
            .run()
        )
        os.remove(path)
        return True
    except ffmpeg.Error as e:
        print("Error while flipping video")
        print(e)
        return False


def copy_video():
    """Copy the video

    Returns:
        bool: True if the video was successfully processed, False otherwise
    """

    path = get_temp_video_path()
    if not path:
        return False
    video_name, metadata = get_unique_name_and_metadata("o")
    res_file_name = os.path.join(TEMP, video_name)
    try:
        (
            ffmpeg.input(path)
            .output(
                res_file_name,
                loglevel="quiet",
                map_metadata=-1,
                **metadata,
            )
            .run()
        )
        os.remove(path)
        return True
    except ffmpeg.Error as e:
        print(e.stderr)
        return False


def cleanup():
    """Delete all videos in the temp folder"""
    print("Cleaning up temp folder...")
    files = os.listdir(TEMP)
    for file in files:
        os.remove(os.path.join(TEMP, file))


def init():
    """Create the output folder if it doesn't exist"""
    if not os.path.exists(TEMP):
        os.mkdir(TEMP)

