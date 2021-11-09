import wget

download_path = './data'
def download_images(images_list):
    for i in images_list:
        wget.download(i['url'], out=download_path)
