import urllib.request
import urllib.error
import requests # pip install requests
import bs4 # pip install beautifulsoup4

import connectDB # connectDB.py

db = connectDB.connectDB()

# Media download
def __media_download(downloadUrl, saveFilename):
    try:
        urllib.request.urlretrieve(downloadUrl,"{0}".format(saveFilename))
    except urllib.error.HTTPError as e:
        print('raise HTTPError')
        print(e.code)
        print(e.reason)
    except urllib.error.URLError as e:
        print('raise URLError')
        print(e.reason)
    except FileNotFoundError:
        print('No such file or directory')
    else:
        urllib.request.urlcleanup() # Delete tmp file from urllib.request.urlretrieve


# -----------------------
# Main Process
# -----------------------

nanagogoUrl = 'https://7gogo.jp/'

# Get Member List
memberInfos = db.getSelectAll(['id', 'name', 'url_prefix'], 'members')
# for memberInfo in  memberInfos:
#     print(memberInfo)

# Loop Members
for memberInfo in  memberInfos:

    # Get last number processed
    lastNumber = db.getSelectOne(['last_number'], 'article_numbers', 'member_id = ' + repr(memberInfo[0]))

    # Set now number
    nowNumber = lastNumber + 1

    # request WEB page
    response = requests.get(nanagogoUrl + memberInfo[2] + '/' + repr(nowNumber))

    # Confirmation status
    print(response.status_code)

    # Stop except status 200
    response.raise_for_status()

    # Analisys HTML
    soup = bs4.BeautifulSoup(response.text , "html.parser" )

    # print(soup.main)

    # Get certain class elements in analisys HTML
    # elem = soup.select('._3DSDHo6-._2icsf9K-')

    # Create file
    #with open('./miku.html', 'w') as file:
        #for elem in elems:
            #print(str(elem))
            # Write text into file
            #file.write(str(elem))

        #file.write(str(elem)) # Write text into file

    # Get video Tag element in certain class elements in analisys HTML
    videos = soup.select('._3DSDHo6-._2icsf9K- video')
    if len(videos) != 0:
        for video in videos:
            videoUrl = video.get('src')

            saveFilename = repr(nowNumber) + '.mp4'

            __media_download(videoUrl, saveFilename)


    # Get img Tag element in certain class elements in analisys HTML
    imgs = soup.select('._3DSDHo6-._2icsf9K- img')
    if len(imgs) != 0:
        for img in imgs:
            imgUrl = img.get('data-src')

            saveFilename = repr(nowNumber) + '.jpg'

            __media_download(imgUrl, saveFilename)