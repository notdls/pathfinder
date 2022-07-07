import sys
import traceback
from urllib.parse import urlparse

def extract_dir_paths(url):
    paths = set()
    url = urlparse(url)
    # add base url to paths)
    paths.add("{}://{}/".format(url.scheme, url.netloc))
    path = url.path
    sub_paths = path.split("/")[1:-1]
    last_path = ""
    for sub_path in sub_paths:
        last_path = last_path+sub_path+"/"
        new_url = url.scheme+"://"+url.netloc+"/"+last_path
        paths.add(new_url)
    return paths

if __name__ == '__main__':
    # intiate vars and sets
    all_paths = {}
    # do the hax
    if not sys.stdin.isatty():
        for line in sys.stdin:
            line = line.strip()
            try:
                # if the line is a url, extract the paths
                if line.startswith("http"):
                    line = line.replace(":80","").replace(":443","") # get rid of port numbers from getallurls
                    temp_url = urlparse(line)
                    # try and clean up unnecessary port numbers in urls
                    base_url = "{}://{}".format(temp_url.scheme, temp_url.netloc)
                    # create set inside dict for faster sorting
                    if base_url not in all_paths:
                        all_paths[base_url] = set()
                    # extract the paths
                    temp_paths = extract_dir_paths(line)
                    for path in temp_paths:
                        if path not in all_paths[base_url]:
                            all_paths[base_url].add(path)
                            print(path)
            except Exception as e:
                print(traceback.format_exc())