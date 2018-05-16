import os
import re
import time
import fire
import hashlib
import requests
from PIL import Image

GIST_BASE_URL = 'https://gist.github.com'
DRIVER_WIDTH, DRIVER_HEIGHT = 1200, 1373


def generate_hexhash(content):
    """Generate string representation of MD5 sum of given data

    Parameters
    ----------
    content : dict
        A python dictionary representing gist's content

    Returns
    -------
    hexhash : str. e.g. "c0e14a771bac3b4944318b430efe2884"
    """

    data = bytearray(str(content))
    md5 = hashlib.md5()
    md5.update(data)
    hexhash = md5.hexdigest()
    return hexhash


def get_gist_hash(github_user, gist_name):
    """Acquire the raw content of the given `gist_name` and return string repr of the MD5 sum.

    Parameters
    ----------
    github_user : str
        String representing valid Github account. e.g. "leemengtaiwan"

    gist_name : str
        Valid gist identifier appear in url

    Returns
    -------
    hash: str

    References
    ----------
    Get the permalink to the gist:
        - https://stackoverflow.com/a/47175630/3859572

    """
    # TODO update example for gist_name

    gist_raw_url = '/'.join((GIST_BASE_URL, github_user, gist_name, 'raw'))
    res = requests.request(
        method='GET',
        url=gist_raw_url
    )
    assert res.status_code == requests.codes.ok, "Problem occurred when requesting raw gist."
    try:
        data = res.json()
    except ValueError:
        data = res.content

    return generate_hexhash(data)


def fullpage_screenshot(driver, file):
    """Take multiple screenshots of already-opened webpage and save the concatenated image

    Parameters
    ----------
    driver : selenium.webdriver
        The current active web driver staying in the page to take screenshots
    file : str
        The file path to save concatenated image

    Returns
    -------
    bool

    Notes
    -----
    Generate Fullpage Screenshot in Chrome
        http://seleniumpythonqa.blogspot.jp/2015/08/generate-full-page-screenshot-in-chrome.html

    """
    image_id = re.findall(r'/([0-9a-zA-Z]+).', file)[0]


    print("Starting chrome full page screenshot workaround ...")
    total_width = driver.execute_script("return document.body.offsetWidth")
    total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
    viewport_width = driver.execute_script("return document.body.clientWidth")
    viewport_height = driver.execute_script("return window.innerHeight")
    print("Total: ({0}, {1}), Viewport: ({2},{3})".format(total_width, total_height,viewport_width,viewport_height))
    rectangles = []

    i = 0
    while i < total_height:
        ii = 0
        top_height = i + viewport_height

        if top_height > total_height:
            top_height = total_height

        while ii < total_width:
            top_width = ii + viewport_width

            if top_width > total_width:
                top_width = total_width

            print("Appending rectangle ({0},{1},{2},{3})".format(ii, i, top_width, top_height))
            rectangles.append((ii, i, top_width,top_height))

            ii = ii + viewport_width

        i = i + viewport_height

    previous = None
    part = 0
    screenshots = [] # list of dict with 'file_name' and 'offset' fields
    total_width, total_height = 0, 0

    for rectangle in rectangles:
        if not previous is None:
            driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
            print("Scrolled To ({0},{1})".format(rectangle[0], rectangle[1]))
            time.sleep(.2)

        file_name = "{0}_part_{1}.png".format(image_id, part)
        print("Capturing {0} ...".format(file_name))

        driver.get_screenshot_as_file(file_name)
        screenshot = Image.open(file_name)
        img_width, img_height = screenshot.size


        screenshots.append({
            'file_name': file_name, 'offset': (0, img_height * part)
        })
        total_width = img_width
        total_height += img_height

        del screenshot
        part = part + 1
        previous = rectangle

    # concatenate all partial images
    print(total_width, total_height)
    stitched_image = Image.new('RGB', (total_width, total_height))

    for screenshot in screenshots:
        file_name, offset = screenshot['file_name'], screenshot['offset']
        print("Adding to stitched image with offset ({0}, {1})".format(offset[0], offset[1]))
        image = Image.open(file_name)
        stitched_image.paste(image, offset)
        os.remove(file_name)

    stitched_image.save(file)
    print("Finishing chrome full page screenshot workaround...")
    return True


def create_chrome_driver(mode="headless", width=DRIVER_WIDTH, height=DRIVER_HEIGHT):
    """Create a headless/visible Chrome driver.

    Parameters
    ----------
    mode : str, optional
        "headless" for creating a headless Chrome driver.
        Otherwise the driver will be visible.

    width : int, optional
        Width of the web driver window

    height : int, optional
        Height of the web driver window

    Returns
    -------
    driver
    """
    from selenium import webdriver
    options = webdriver.ChromeOptions()
    if mode == 'headless':
        options.add_argument("headless")
    else:
        pass
    driver = webdriver.Chrome(chrome_options=options)
    driver.get('https://github.com/')
    driver.set_window_size(width, height)
    return driver


if __name__ == '__main__':
    fire.Fire()