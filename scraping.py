import datetime
import urllib.request
import urllib.error
import os
import time
import requests # pip install requests
import bs4 # pip install beautifulsoup4

import connectDB # connectDB.py

db = connectDB.connectDB()

def getDateTime():
    UTC_Now = datetime.datetime.utcnow()
    month = '%02d'%UTC_Now.month
    day = '%02d'%UTC_Now.day
    hour = '%02d'%UTC_Now.hour
    minute = '%02d'%UTC_Now.minute

    return str(UTC_Now.year) + month + day + '_' + hour + minute

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
def __getLastNumberOfArticle(nanagogoUrl, urlPrefixOfMember):

    # Connect 755 page
    response = requests.get(nanagogoUrl + urlPrefixOfMember)
    while response.status_code != 200:
        print('Request retry')
        response = requests.get(nanagogoUrl + urlPrefixOfMember)

    # Get HTML
    html = bs4.BeautifulSoup(response.text , "html.parser" )

    # Get article numbers in 755 page
    numbersOfArticles = html.select('._1GqgG5a-._2T3KLkN-.Link')

    # Get last number
    for numbersOfArticle in numbersOfArticles:
        lastNumber = numbersOfArticle.get('href').replace('/' + urlPrefixOfMember + '/', '')

    print('lastNumber is ' + lastNumber)
    print('The number of last article is ' + repr(lastNumber))
    return int(lastNumber) + 1


# -----------------------
# Main Process
# -----------------------

nanagogoUrl = 'https://7gogo.jp/'

# Get Member List
memberInfos = db.getSelectAll(['id', 'name', 'url_prefix', 'folder_name'], 'members')
# for memberInfo in  memberInfos:
#     print(memberInfo)

limitNumberOfExecutions = int(input('Enter a limit number of execution : '))
countNumberOfExecution = 0

# Loop Members
for memberInfo in memberInfos:

    IdOfMember = memberInfo[0]
    theNameOfMember = memberInfo[1]
    print('Member\'s name : ' + theNameOfMember)
    urlPrefixOfMember = memberInfo[2]
    folderName = memberInfo[3]
    savingFolderPath = './' + folderName

    lastNumberOfArticle = __getLastNumberOfArticle(nanagogoUrl, urlPrefixOfMember)

    # Get last number of previous processing
    lastNumberOfPreviousProcessing = db.getSelectOne(['last_number'], 'article_numbers', 'member_id = ' + repr(IdOfMember))

    # Skip if a new article doesn'n exist.
    if lastNumberOfPreviousProcessing == lastNumberOfArticle :
        continue

    # Set start number
    startNumberOfArticle = lastNumberOfPreviousProcessing + 1

    for numberOfArticle in range(startNumberOfArticle, lastNumberOfArticle):

        # Limit number of executions
        if limitNumberOfExecutions == countNumberOfExecution :
            print('Stop process. ' + repr(countNumberOfExecution) + 'times execution.')
            exit()

        print('Member : ' + repr(IdOfMember) + ' ' + theNameOfMember + ' / The processing article number : ' + repr(numberOfArticle) + \
            ' / The last article\'s number : ' + repr(lastNumberOfArticle - 1))

        # Check folder exists for saving
        isDir = os.path.isdir(savingFolderPath)

        # Create the folder if it doesn't exist.
        if isDir == False :
            os.mkdir(savingFolderPath)

        # Init try count
        retryCount = 1
        while (True) :
            # request WEB page
            response = requests.get(nanagogoUrl + urlPrefixOfMember + '/' + repr(numberOfArticle))

            # Confirmation status
            print('Request result : ' + repr(response.status_code))

            # Stop when except status 200
            responseResult = response.status_code
            if responseResult != 200 :
                print('Request status is not 200. Article number is ' + repr(numberOfArticle) + '.')
                print('Retry count : ' + repr(retryCount))

                if retryCount == 10 :
                    print('Skip Article. Article number is ' + repr(numberOfArticle) + '.')
                    break
                else :
                    retryCount += 1
                    time.sleep(5)
                    continue
            elif responseResult == 200 :
                break

            print('Stop process. While process is an error. responseResult is : ' + repr(responseResult))
            exit()

        # Skip if the article that 10times of requests failed.
        if retryCount == 10 :
            # Saving last number
            db.updateData('article_numbers', 'last_number = ' + repr(numberOfArticle), 'member_id = ' + repr(IdOfMember))
            continue

        # Get HTML
        html = bs4.BeautifulSoup(response.text , "html.parser" )

        # Get certain class elements in analisys HTML
        bodyOfArticle = html.select('._3DSDHo6-._2icsf9K-')

        # Skip if reference article
        if bodyOfArticle == [] :
            # The execution count increasing
            countNumberOfExecution += 1
            continue

        # Set CSS
        CssCode = '<head><link rel="stylesheet" href="./_app.css" data-reactid="11"></head><br><br><br><br><br><br><br>'

        # Set Download filename
        saveFilename = folderName + '_' + repr(numberOfArticle) + '_DL_at_' + getDateTime()

        # Create file
        with open(savingFolderPath + '/' + saveFilename + '.html', 'w') as file:
            for elem in bodyOfArticle:
                # print(str(elem))

                # Write text into file
                file.write(CssCode + str(elem))

        # Get video Tag element in certain class elements in analisys HTML
        videos = html.select('._3ii6YrF- video')
        if len(videos) != 0:
            for video in videos:
                videoUrl = video.get('src')

                __media_download(videoUrl, savingFolderPath + '/' + saveFilename + '.mp4')


        # Get img Tag element in certain class elements in analisys HTML
        imgs = html.select('.AlTY-23- img')
        if len(imgs) != 0:
            for img in imgs:
                imgUrl = img.get('data-src')

                __media_download(imgUrl, savingFolderPath + '/' + saveFilename + '.jpg')

        # Saving last number
        db.updateData('article_numbers', 'last_number = ' + repr(numberOfArticle), 'member_id = ' + repr(IdOfMember))

        # The execution count increasing
        countNumberOfExecution += 1

        time.sleep(5)