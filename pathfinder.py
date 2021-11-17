import requests
import sys
import traceback
import argparse
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser


def extract_dir_paths(url):
    paths = []
    url = urlparse(url)
    path = url.path
    sub_paths = path.split("/")[1:-1]
    last_path = ""
    for sub_path in sub_paths:
        last_path = last_path+sub_path+"/"
        new_url = url.scheme+"://"+url.netloc+"/"+last_path
        paths.append(new_url)
    return paths

def get_paths_from_robots(url):
    urls = []
    rp = RobotFileParser()
    url = urlparse(url)
    s = requests.Session()
    s.headers.update({"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"})
    result = s.get(url.scheme+"://"+url.netloc+"/robots.txt", verify=False, allow_redirects=False, timeout=10, max_retries=0)
    if result.status_code == 200:
        for line in result.text.splitlines():
            if line.startswith("Allow:") or line.startswith("Disallow:"):
                path = line.split(" ")
                if len(path) > 1:
                    temp_url = url.scheme+"://"+url.netloc+path[1].replace("*","")
                    if temp_url not in urls:
                        urls.append(temp_url)
    return urls


if __name__ == '__main__':
    try_robots = False
    base_domains = []
    all_paths = []
    if not sys.stdin.isatty():
        for line in sys.stdin:
            try:
                if line.startswith("http"):
                    temp_paths = extract_dir_paths(line)
                    temp_url = urlparse(line)
                    if try_robots:
                    # simplify paths if port included for no real reason, avoids doubling up requests
                        if temp_url.netloc.endswith(":80") and temp_url.scheme == "http":
                            temp_url._replace(netloc=temp_url.netloc[:-3])
                        elif temp_url.netloc.endswith(":443") and temp_url.scheme == "https":
                            temp_url._replace(netloc=temp_url.netloc[:-4])
                        base_domain = temp_url.netloc
                        if base_domain not in base_domains:
                            base_domains.append(base_domain)
                            robots = get_paths_from_robots(line)
                            for robot in robots:
                                robot_paths = extract_dir_paths(robot)
                                for rpath in robot_paths:
                                    if rpath not in all_paths:
                                        all_paths.append(rpath)
                                        print(rpath)
                    for path in temp_paths:
                        if path not in all_paths:
                            all_paths.append(path)
                            print(path)
            except Exception as e:
                print(traceback.format_exc())
                print(line)
                print(str(e))
                #exit()