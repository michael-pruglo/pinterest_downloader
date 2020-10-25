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

rejected = []

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
  images = driver.find_elements_by_tag_name("img")
  for img in images:
    img_src = img.get_attribute("src")
    if "originals" in img_src:
      return img_src

def getBoardOriginals(board_url):
  total_imgs = []
  pin_pages =  getPinUrls(board_url)
  print("size:", len(pin_pages))
  print(pin_pages)
  for i, single_pin in enumerate(pin_pages):
    original_imgs = getOriginalsImgSrcFromPin("https://www.pinterest.com" + single_pin)
    print("%3d" % (i+1), ")\t\t", single_pin, "\t\t", original_imgs)
    if original_imgs is None:
      rejected.append(single_pin)
    else:
      total_imgs.append(original_imgs)
  return total_imgs

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
  img_urls = getBoardOriginals(board_url)
  print("\nFetching", len(img_urls), "picture(s) done. Downloading...")
  for img_url in img_urls:
    if img_url is not None:
      print("\t", img_url, end=' ')
      downloadImg(img_url, folder_path)
      print("done.")

def generateFolderName(board_name):
  split_board_name = board_name.split('/')
  if board_name[-1] == '/':
    return split_board_name[-2]
  else:
    return split_board_name[-1]

def prepareFolder(folder_name):
  import os
  if not os.path.exists(folder_name):
      os.makedirs(folder_name)

def download(board_name):
  print("\n\n\n")
  print("downloading", board_name, "\n")
  folder_name = "D:/temp/real/" + generateFolderName(board_name)
  prepareFolder(folder_name)
  downloadBoard(board_name, folder_name)


try:
  for board_name in [
    "https://www.pinterest.com/michaelpruglo/misc-awesome-stuff/",
    "https://www.pinterest.com/michaelpruglo/test/"
  ]:
    download(board_name)
finally:
  print("\n\n", len(rejected), "rejected:")
  print(rejected)
  driver.quit()