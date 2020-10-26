from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
binary = r'C:\Program Files\Mozilla Firefox\firefox.exe'
options = Options()
options.set_headless(headless=True)
options.binary = binary
cap = DesiredCapabilities().FIREFOX
cap["marionette"] = True #optional
driver = webdriver.Firefox(firefox_options=options, capabilities=cap, executable_path="C:\\python\\geckodriver.exe")

LOCAL_PARENT_FOLDER = "D:/temp/nyyyy"
LOG_LINE_LEN = 140
global_rejected = []

""" ---------------------------------------------- Business logic ---------------------------------------------- """

def getPinUrls(board_url):
  from lxml import html
  import requests

  page = requests.get(board_url)
  tree = html.fromstring(page.content)
  pins = tree.xpath('//div[@class="zI7 iyn Hsu"]//@href')

  page.close()
  del page, tree
  return [s for s in pins if s.startswith('/pin/')]


def getOriginalsImgSrcFromPin(pin_url):
  driver.get(pin_url)
  images = driver.find_elements_by_xpath('//img[contains(@src, "originals")]')
  if len(images) == 1:
    return images[0].get_attribute("src")
  elif len(images) > 1:
    print("more than one original")


def getBoardOriginals(board_url):
  approved_imgs, rejected_pins = [], []
  pin_pages =  getPinUrls(board_url)

  print("Found pins:", len(pin_pages))
  print("Their urls:", pin_pages, "\n")
  print("Fetching...")
  print("-" * LOG_LINE_LEN)
  print("  #  \t\t     single pin url     \t\t                             original img url")
  print("-" * LOG_LINE_LEN)
  
  for i, single_pin in enumerate(pin_pages):
    original_imgs = getOriginalsImgSrcFromPin("https://www.pinterest.com" + single_pin)

    print("%3d" % (i+1), ")\t\t", single_pin, "\t\t", original_imgs)
    
    if original_imgs is None:
      rejected_pins.append(single_pin)
    else:
      approved_imgs.append(original_imgs)
  
  print("-" * LOG_LINE_LEN, "\n")
  return approved_imgs, rejected_pins


def generateFilenameFromURL(img_url):
  return img_url.split('/')[-1]


def downloadImg(img_url, folder_path):
  import urllib
  full_filename = folder_path + "/" + generateFilenameFromURL(img_url) 
  output = open(full_filename, "wb")
  try:
    resource = urllib.request.urlopen(img_url)
    output.write(resource.read())
  finally:
    output.close()


def downloadBoard(board_url, folder_path):
  img_urls, rejected_pins = getBoardOriginals(board_url)
  global_rejected.append(rejected_pins)

  print("Fetching done. Success:", len(img_urls), " rejected:", len(rejected_pins))
  print("Downloading into", folder_path)
  
  for img_url in img_urls:
    print("\t", img_url, end=' ')
    downloadImg(img_url, folder_path)
    print("\t done.")
  
  print("\n", "-" * LOG_LINE_LEN)


def generateFolderName(board_name):
  split_board_name = board_name.split('/')
  if board_name[-1] == '/':
    return split_board_name[-2]
  else:
    return split_board_name[-1]


def prepareFolder(folder_name):
  import os
  if not os.path.exists(folder_name):
    prepareFolder(os.path.dirname(folder_name))
    os.makedirs(folder_name)


def download(board_name):
  print("\n\n\n\ndownloading", board_name, "\n")
  folder_name = LOCAL_PARENT_FOLDER + ("" if LOCAL_PARENT_FOLDER[-1]=='/' else "/") + generateFolderName(board_name)
  prepareFolder(folder_name)
  downloadBoard(board_name, folder_name)

""" --------------------------------------------------- MAIN --------------------------------------------------- """
def main(board_names):
  try:
    for board_name in board_names:
      download(board_name)
  finally:
    print("\n\n", sum(len(x) for x in global_rejected), "rejected:")
    print("[")
    for rej in global_rejected:
      print(" ", rej)
    print("]")
    driver.quit()


""" --------------------------------------------------- INPUT --------------------------------------------------- """

pinterest_prefix = "https://www.pinterest.com/"
def makeFullBoardURL(board_name, username="michaelpruglo"):
  return pinterest_prefix + username + "/" + board_name + "/"

def makeFullSubsectionURL(parent_board_name, subsection, username="michaelpruglo"):
  return pinterest_prefix + username + "/" + parent_board_name + "/" + subsection + "/"

input_test_set = [
  "misc-awesome-stuff",
  "test",
]
input_test_boardnames = [makeFullBoardURL(s) for s in input_test_set]

input_real_set = [
  "tits",
  "earrings",
  "ahegao",
  "legsfeet",
  "poses",
  "makeup",
  "strapscutout",
  "eyes",
  "nails",
  "butt",
  "headwear",
  "mouthtongue",
  "fit",
  "overknee-socks",
  "glasses",
  "hairstyles",
  "stilettos",
  "faces",
  "outfits",
]
input_real_boardnames = [
  *[makeFullSubsectionURL("girls", s) for s in input_real_set],
  makeFullBoardURL("girls")
]

""" --------------------------------------------------- ---- --------------------------------------------------- """

with open("urls.txt") as url_file:
  main([url.rstrip('\n') for url in url_file])