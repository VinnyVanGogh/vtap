import re, time, requests, shutil

from pathlib import Path
from pytube import YouTube as youtube
from urllib.parse import urlparse

from core.logger import log, print_log

@log('main')
def get_video_id(url):
    url = re.sub(r'\\', '', url)
    url = re.sub(r'/', '', url)
    url = re.sub(r'\'', '', url)
    url = url.split('v=')[-1]
    formatted_url = 'https://www.youtube.com/watch?v=' + url
    return formatted_url

@log('main')
def download_video(url):
    formatted_url = get_video_id(url)
    yt = youtube(formatted_url)
    author = yt.author
    video_id = yt.video_id

    safe_author = re.sub(r'[\\/*?:"<>|]', "", author.lower().replace(' ', '_'))
    safe_title = re.sub(r'[\\/*?:"<>|]', "", yt.title.lower().replace(' ', '_'))

    video_dir = Path(__file__).resolve().parent / "videos" / safe_author
    video_dir.mkdir(parents=True, exist_ok=True)

    filename = video_dir / f"{safe_title}_{video_id}.mp4"

    if not filename.exists():
        yt.streams.filter(progressive=True, file_extension='mp4') \
            .order_by('resolution').desc().first() \
            .download(output_path=video_dir, filename=f"{safe_title}_{video_id}.mp4")
        print_log(f"Downloaded: {filename}", level="info")
        time.sleep(1)
    else:
        print_log(f"Video already downloaded: {filename}", level="info")
        time.sleep(1)

    return str(filename)

@log('main')
def download_picture(image_path):
    parsed_url = urlparse(image_path)
    if parsed_url.scheme in ('http', 'https'):
        domain = parsed_url.netloc
        path = parsed_url.path

        safe_author = re.sub(r'[\\/*?:"<>|]', "", domain.lower().replace(' ', '_'))
        filename = Path(path).name
        safe_filename = re.sub(r'[\\/*?:"<>|]', "", filename)[:20]  
        print_log(f"safe_filename: {safe_filename}", level="info")
        safe_filename = safe_filename + ".jpg" if not safe_filename.endswith(".jpg") else safe_filename
        print_log(f"safe_filename after add .jpg: {safe_filename}", level="info")

        image_dir = Path(__file__).resolve().parent / "images" / safe_author
        image_dir.mkdir(parents=True, exist_ok=True)
        image_file = image_dir / safe_filename

        if not image_file.exists():
            print_log(f"Downloading image to: {image_file}", level="info")
            response = requests.get(image_path)
            if response.status_code == 200:
                image_file.write_bytes(response.content)
                print_log(f"Image downloaded: {image_file}", level="info")
            else:
                print_log(f"Failed to download image: {image_path}", level="error")
        else:
            print_log(f"Image already downloaded: {image_file}", level="info")

        return str(image_file)
    else:
        image_path = Path(image_path)
        if image_path.exists():
            author = image_path.parent.name or "unknown_author"
            safe_author = re.sub(r'[\\/*?:"<>|]', "", author.lower().replace(' ', '_'))
            safe_filename = re.sub(r'[\\/*?:"<>|]', "", image_path.name)

            image_dir = Path(__file__).resolve().parent / "images" / safe_author
            image_dir.mkdir(parents=True, exist_ok=True)
            new_image_path = image_dir / safe_filename

            if not new_image_path.exists():
                print_log(f"Copying image to: {new_image_path}", level="info")
                shutil.copy2(image_path, new_image_path)
                print_log(f"Image copied: {new_image_path}", level="info")
            else:
                print_log(f"Image already exists: {new_image_path}", level="info")

            return str(new_image_path)
        else:
            print_log(f"Image file does not exist: {image_path}", level="error")
            return None
