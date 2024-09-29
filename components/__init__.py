from components.downloader import download_video, download_picture
from components.ascii_video import play_ascii_video
from components.audio_player import play_audio
from components.ascii_picture import display_picture
from components.demo_setup import demo_playbacks

__all__ = ['download_video', 'download_picture', 'play_ascii_video', 'play_audio', 'display_picture', 'demo_playbacks']

# to use the components, import them from the package
# from components import download_video, download_picture, play_ascii_video, play_audio, display_picture, demo_playbacks
# or import the package and use the components
# import components
# components.download_video()
# or from components import *
