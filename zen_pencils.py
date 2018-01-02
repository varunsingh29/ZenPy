import requests
import os
import shutil
from bs4 import BeautifulSoup

def fetch(item):

    ''' Fetches a URL using Requests '''

    try:
        r = requests.get(item)
    except HTTPError:
        print("Oops ! An HTTP error occured")
        exit()
    except ConnectionError:
        print("Oops ! Connection Error")
        exit()
    except :
        print("Yikes !! Something went wrong")
        exit()

    return r


def crawl_archive():

    ''' Crawls all URL's from the Archive section and maintains a dictionary '''

    print("Fetching list of lastest comics for you...")
    print("This can take some time... Grab a Snickers!!")
    base_url = "https://zenpencils.com/archives/"
    result_set = {}

    r = fetch(base_url)
    soup = BeautifulSoup(r.content, "lxml")
    parent = soup.find("div", class_="comic-archive-list-wrap")
    children = parent.children

    key = 1;
    for child in children:
        new_url = child.find("a")
        result_set[key] = new_url["href"]
        key += 1

    return result_set


def download_file(img_name, img_tag, path):

    img_response = requests.get(img_tag["src"])

    if img_response.status_code == 200:
        with open(path+img_name, 'wb') as f:
            f.write(img_response.content)
    else:
        print("Oops ! An error occured ")




def fetch_img_tags(master):

    global img_tag_list
    global names_tags # Dictionary of img names and image tags
    for item in master:
        r = fetch(item)
        soup = BeautifulSoup(r.content, "lxml")
        obj = soup.find("div", {"id":"comic"})
        img = obj.find("img")  # Fix multiple images bug here - 1
        filename = img["title"]

        # If file name is not available, fetch from title of post
        if filename == "":
            post_title = soup.find("h2", class_="post-title")
            filename = post_title.string

        img_tag_list.append(img)
        names_tags[filename] = img

    print("Done.")


def option_1():

    print("Aye Captain !")
    path = os.getcwd()+"/ZenPencils/"

    # Remove old directory if exists
    if os.path.exists(path):
        # print("Deleted old comics!!")
        shutil.rmtree(path)

    os.mkdir("ZenPencils")

    count = 1
    for k,v in names_tags.items():
        download_file(k,v,path)
        print("Done #%d of %d" %(count,total_comics) + "\r",end="")  # Progress Bar
        count +=1

def option_2():

    ''' Download missing comics or new comics '''

    existing = []
    missing = {}
    path = input("Enter path to Local Collection: ")
    path += "/"

    if os.path.exists(path):
        dir_listing = os.listdir(path)

        # Check for missing files
        for item in dir_listing:
            existing.append(item)
        # print(existing)

        if(len(existing) == total_comics):
            print("No missing comics !")
        else:

            set2 = set(existing)
            for x,y in names_tags.items():
                if x not in set2:
                    missing[x] = y;

            count = 1
            missing_count = len(missing)
            for k,v in missing.items():
                download_file(k,v,path)
                print("Done #%d of %d" %(count,missing_count) + "\r",end="")  # Progress Bar
                count += 1

    else:
        print("Sorry, No such directory found.")


def option_3():

    try:
        comic_num = int(input("Enter comic number: "))
        if comic_num > total_comics:
            print("No such comic exists")
            return
    except ValueError:
        print("Not a valid comic number !!")
        return

    path = input("Enter path to Local Collection: ")
    path += "/"
    # print(path)
    url = crawled[int(comic_num)]
    r = fetch(url)
    soup = BeautifulSoup(r.content, "lxml")
    obj = soup.find("div", {"id":"comic"})  # Fix multiple images bug here - 2
    img = obj.find("img")
    filename = img["title"]

    # If file name is not available, fetch from title of post
    if filename == "":
        post_title = soup.find("h2", class_="post-title")
        filename = post_title.string
    download_file(filename, img, path)


if __name__ == "__main__":

    prompt = "1) Download all Zen Pencil comics \n2) Download all comics missing from local collection\
            \n3) Download comics by number \n4) Exit"

    img_tag_list, crawled = [],[]
    names_tags = {}
    crawled = crawl_archive()
    master = list(crawled.values())
    total_comics = len(master)
    fetch_img_tags(master)

    flag = True
    while(flag):
        print(prompt)
        choice = int(input("Enter choice: "))
        if choice == 1:
            option_1()
        elif choice == 2:
            option_2()
        elif choice == 3:
            option_3()
        elif choice == 4:
            flag = False
            break
        else:
            print("Incorrect choice")
