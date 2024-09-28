from pathlib import Path
from pytube import YouTube as youtube
import re
import time
import requests
import shutil
from urllib.parse import urlparse

def get_video_id(url):
    url = re.sub(r'\\', '', url)
    url = re.sub(r'/', '', url)
    url = re.sub(r'\'', '', url)
    url = url.split('v=')[-1]
    formatted_url = 'https://www.youtube.com/watch?v=' + url
    return formatted_url

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
        print(f"Downloaded: {filename}")
        time.sleep(1)
    else:
        print(f"Video already downloaded: {filename}")
        time.sleep(1)

    return str(filename)

def download_picture(image_path):
    parsed_url = urlparse(image_path)
    if parsed_url.scheme in ('http', 'https'):
        # It's a URL
        # Use domain and path to construct author and filename
        domain = parsed_url.netloc
        path = parsed_url.path

        # Sanitize the author and filename
        safe_author = re.sub(r'[\\/*?:"<>|]', "", domain.lower().replace(' ', '_'))
        filename = Path(path).name
        safe_filename = re.sub(r'[\\/*?:"<>|]', "", filename)[:20]  
        print(f"safe_filename: {safe_filename}")
        safe_filename = safe_filename + ".jpg" if not safe_filename.endswith(".jpg") else safe_filename
        print(f"safe_filename 2: {safe_filename}")

        image_dir = Path(__file__).resolve().parent / "images" / safe_author
        image_dir.mkdir(parents=True, exist_ok=True)
        image_file = image_dir / safe_filename

        if not image_file.exists():
            print(f"Downloading image: {image_file}")
            response = requests.get(image_path)
            if response.status_code == 200:
                image_file.write_bytes(response.content)
                print(f"Image downloaded: {image_file}")
            else:
                print(f"Failed to download image: {image_path}")
        else:
            print(f"Image already downloaded: {image_file}")

        return str(image_file)
    else:
        # It's a local file path
        image_path = Path(image_path)
        if image_path.exists():
            # Use the file's parent directory name as author
            author = image_path.parent.name or "unknown_author"
            safe_author = re.sub(r'[\\/*?:"<>|]', "", author.lower().replace(' ', '_'))
            safe_filename = re.sub(r'[\\/*?:"<>|]', "", image_path.name)

            image_dir = Path(__file__).resolve().parent / "images" / safe_author
            image_dir.mkdir(parents=True, exist_ok=True)
            new_image_path = image_dir / safe_filename

            if not new_image_path.exists():
                print(f"Copying image to: {new_image_path}")
                shutil.copy2(image_path, new_image_path)
                print(f"Image copied: {new_image_path}")
            else:
                print(f"Image already exists: {new_image_path}")

            return str(new_image_path)
        else:
            print(f"Image file does not exist: {image_path}")
            return None
