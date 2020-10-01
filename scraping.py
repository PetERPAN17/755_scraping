import requests # pip install requests
import bs4 # pip install beautifulsoup4

# request WEB page
response = requests.get('https://7gogo.jp/tanaka-miku/32070')

# Confirmation status
print(response.status_code)

# Stop except status 200
response.raise_for_status()

# Analisys HTML
soup = bs4.BeautifulSoup(response.text , "html.parser" )

# print(soup.main)

# Get certain class elements in analisys HTML
# elem = soup.select('._3DSDHo6-._2icsf9K-')

# Get video Tag element in certain class elements in analisys HTML
videos = soup.select('._3DSDHo6-._2icsf9K- video')
#for video in videos:
    #print(video.get('src'))

# Get img Tag element in certain class elements in analisys HTML
imgs = soup.select('._3DSDHo6-._2icsf9K- img')
for img in imgs:
    #print(img)git
    print(img.get('data-src'))

# Create file
#with open('./miku.html', 'w') as file:
    #for elem in elems:
        #print(str(elem))
        # Write text into file
        #file.write(str(elem))

    #file.write(str(elem)) # Write text into file