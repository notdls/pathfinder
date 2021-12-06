import requests
import sys
import traceback
import argparse
from urllib.parse import urlparse
from urllib3.exceptions import InsecureRequestWarning

def verify_if_up(url, s):
    try:
        s.get(url, verify=False, timeout=5, allow_redirects=False)
        return True
    except Exception as e:
        return False

def extract_dir_paths(url):
    paths = set()
    url = urlparse(url)
    path = url.path
    sub_paths = path.split("/")[1:-1]
    last_path = ""
    for sub_path in sub_paths:
        last_path = last_path+sub_path+"/"
        new_url = url.scheme+"://"+url.netloc+"/"+last_path
        paths.add(new_url)
    return paths

def get_paths_from_robots(url, s):
    urls = []
    url = urlparse(url)
    result = s.get(url.scheme+"://"+url.netloc+"/robots.txt", verify=False, allow_redirects=False, timeout=10)
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
    # setup argparse
    parser = argparse.ArgumentParser(description="Parses a list of URLs from stdin and breaks down all of the directories")
    parser.add_argument('-r','--robots', type=bool, action="store", dest="robots", help="Attempt to grab the hosts robots.txt", default=False)
    parser.add_argument('--up', type=bool, action="store", dest="verify_up", help="Verify if a host is up", default=False)
    args = parser.parse_args()
    # intiate vars and sets
    try_robots = args.robots
    verify_up = args.verify_up
    bad_hosts = set()
    good_hosts = set()
    base_domains = set()
    all_paths = {}
    # setup session for verification
    base_session = requests.Session()
    a = requests.adapters.HTTPAdapter(max_retries=0)
    base_session.mount('http://', a)
    base_session.mount('https://', a)
    base_session.headers.update({"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"})
    requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
    # do the hax
    if not sys.stdin.isatty():
        for line in sys.stdin:
            line = line.strip()
            try:
                if line.startswith("http"):
                    temp_url = urlparse(line)
                    # try and clean up unnecessary port numbers in urls
                    if temp_url.netloc.endswith(":80") and temp_url.scheme == "http":
                        temp_url._replace(netloc=temp_url.netloc.replace(":80",""))
                        line = line.replace(":80","")
                    elif temp_url.netloc.endswith(":443") and temp_url.scheme == "https":
                        temp_url._replace(netloc=temp_url.netloc.replace(":443",""))
                        line = line.replace(":443","")
                    base_url = "{}://{}".format(temp_url.scheme, temp_url.netloc)
                    # create set inside dict for faster sorting
                    if base_url not in all_paths:
                        all_paths[base_url] = set()
                    # verify the host is up before grabbing anything
                    if verify_up:
                        if base_url not in good_hosts and base_url not in bad_hosts:
                            result = verify_if_up(line, base_session)
                            if result == False:
                                bad_hosts.add(base_url)
                            else:
                                good_hosts.add(base_url)
                        if base_url in bad_hosts:
                            continue
                    temp_paths = extract_dir_paths(line)
                    if try_robots: # try and get paths from robots.txt
                        base_domain = temp_url.netloc
                        if base_domain not in base_domains:
                            base_domains.append(base_domain)
                            robots = get_paths_from_robots(line, base_session)
                            for robot in robots:
                                robot_paths = extract_dir_paths(robot)
                                for rpath in robot_paths:
                                    if rpath not in all_paths:
                                        all_paths.add(rpath)
                                        print(rpath)
                    for path in temp_paths:
                        if path not in all_paths[base_url]:
                            all_paths[base_url].add(path)
                            print(path)
            except Exception as e:
                print(traceback.format_exc())
