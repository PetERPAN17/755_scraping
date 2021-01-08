import urllib.request
import urllib.error
import os
import time
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

# Get last number of Article
def __getLastNumberOfArticle(nanagogoUrl, theNameOfMember):

    # Connect 755 page
    response = requests.get(nanagogoUrl + theNameOfMember)

    # Get HTML
    html = bs4.BeautifulSoup(response.text , "html.parser" )

    # Get article numbers in 755 page
    numbersOfArticles = html.select('._1GqgG5a-._2T3KLkN-.Link')

    # Get last number
    for numbersOfArticle in numbersOfArticles:
        lastNumber = numbersOfArticle.get('href').replace('/' + theNameOfMember + '/', '')
    return int(lastNumber)


# -----------------------
# Main Process
# -----------------------

limitNumberOfExecutions = int(input('Enter a limit number of execution : '))
startNumberOfExecution = 0

nanagogoUrl = 'https://7gogo.jp/'

# Get Member List
memberInfos = db.getSelectAll(['id', 'name', 'url_prefix', 'folder_name'], 'members')
# for memberInfo in  memberInfos:
#     print(memberInfo)

# Loop Members
for memberInfo in memberInfos:

    IdOfMember = memberInfo[0]
    theNameOfMember = memberInfo[2]
    folderName = memberInfo[3]

    savingFolderPath = './' + folderName

    # Check folder exists for saving
    isDir = os.path.isdir(savingFolderPath)

    # Create the folder if it doesn't exist.
    if isDir == False :
        os.mkdir(savingFolderPath)

    lastNumberOfArticle = __getLastNumberOfArticle(nanagogoUrl, theNameOfMember)

    # Get last number of previous processing
    lastNumberOfPreviousProcessing = db.getSelectOne(['last_number'], 'article_numbers', 'member_id = ' + repr(IdOfMember))

    # Skip if a new article doesn'n exist.
    if lastNumberOfPreviousProcessing == lastNumberOfArticle :
        continue

    # Set start number
    startNumberOfArticle = lastNumberOfPreviousProcessing + 1

    for numberOfArticle in range(startNumberOfArticle, lastNumberOfArticle):

        # Limit number of executions
        if limitNumberOfExecutions == startNumberOfExecution :
            print('Stop process. ' + repr(startNumberOfExecution) + 'times execution.')
            exit()

        print('Article number : ' + repr(numberOfArticle))

        # request WEB page
        response = requests.get(nanagogoUrl + theNameOfMember + '/' + repr(numberOfArticle))

        # Confirmation status
        print('Request result : ' + repr(response.status_code))

        # Stop when except status 200
        # response.raise_for_status()
        if response.status_code != 200 :
            print('Request status is not 200. Article number is ' + repr(numberOfArticle) + '.')
            exit()

        # Get HTML
        html = bs4.BeautifulSoup(response.text , "html.parser" )

        # Get certain class elements in analisys HTML
        bodyOfArticle = html.select('._3DSDHo6-._2icsf9K-')

        # Skip if reference article
        if bodyOfArticle == [] :
            # Start the number of execution increasing
            startNumberOfExecution += 1
            continue

        # Set CSS
        CssCode = '<head><link rel="stylesheet" href="./_app.css" data-reactid="11"></head><br><br><br><br><br><br><br>'

        # Create file
        with open(savingFolderPath + '/' + repr(numberOfArticle) + '.html', 'w') as file:
            for elem in bodyOfArticle:
                # print(str(elem))

                # Write text into file
                file.write(CssCode + str(elem))

        # Get video Tag element in certain class elements in analisys HTML
        videos = html.select('._3ii6YrF- video')
        if len(videos) != 0:
            for video in videos:
                videoUrl = video.get('src')

                saveFilename = repr(numberOfArticle) + '.mp4'

                __media_download(videoUrl, savingFolderPath + '/' + saveFilename)


        # Get img Tag element in certain class elements in analisys HTML
        imgs = html.select('.AlTY-23- img')
        if len(imgs) != 0:
            for img in imgs:
                imgUrl = img.get('data-src')

                saveFilename = repr(numberOfArticle) + '.jpg'

                __media_download(imgUrl, savingFolderPath + '/' + saveFilename)

        # Saving last number
        db.updateData('article_numbers', 'last_number = ' + repr(numberOfArticle), 'member_id = ' + repr(IdOfMember))

        # Start the number of execution increasing
        startNumberOfExecution += 1

        time.sleep(5)