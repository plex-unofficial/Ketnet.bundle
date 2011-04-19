import re

####################################################################################################

TITLE      = 'Ketnet'
PREFIX     = '/video/ketnet'
ART        = 'art-default.jpg'
ICON       = 'icon-default.png'
BASE_URL   = 'http://video.ketnet.be'
VIDEO_HOME = '%s/cm/ketnet/ketnet-mediaplayer' % BASE_URL

####################################################################################################

def Start():
  Plugin.AddPrefixHandler(PREFIX, MainMenu, TITLE, ICON, ART)
  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
  Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')

  MediaContainer.title1 = TITLE
  MediaContainer.viewGroup = 'List'
  MediaContainer.art = R(ART)

  DirectoryItem.thumb = R(ICON)
  RTMPVideoItem.thumb  = R(ICON)

  HTTP.CacheTime = CACHE_1HOUR
  HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13'

####################################################################################################

def MainMenu():
  dir = MediaContainer()

  content = HTML.ElementFromURL(VIDEO_HOME, errors='ignore')
  for category in content.xpath('//div[@id="mediaTabs"]//a[contains(@href,"view")]'):
    title = category.get('title')
    id = category.get('id')
    # Check the number of subcategories
    num = len(content.xpath('//div[@id="sub' + id + '"]//a[contains(@href,"view")]'))
    if num > 0:
    	dir.Append(Function(DirectoryItem(Category, title=title), id=id))
    else:
    	url = BASE_URL + category.get('href')
    	dir.Append(Function(DirectoryItem(Videos, title=title), url=url))

  return dir

####################################################################################################

def Category(sender, id):
  dir = MediaContainer(title2=sender.itemTitle)

  content = HTML.ElementFromURL(VIDEO_HOME, errors='ignore')
  for category in content.xpath('//div[@id="sub' + id + '"]//a[contains(@href,"view")]'):
    title = category.get('title')
    url = BASE_URL + category.get('href')
    dir.Append(Function(DirectoryItem(Videos, title=title), url=url))

  return dir

####################################################################################################

def Videos(sender, url):
  dir = MediaContainer(title2=sender.itemTitle, viewGroup='InfoList')

  content = HTML.ElementFromURL(url, errors='ignore')
  for video in content.xpath('//div[@class="mediaItem"]/span[@class="title"]/a'):
    title = video.text.strip()
    url = video.get('href')

    details = HTTP.Request(url, cacheTime=CACHE_1DAY).content

    video_details = HTML.ElementFromString(details)

    try:
      subtitle = video_details.xpath('//div[@id="videoMetaData"]//span[@class="source"]')[0].text.strip()
    except:
      subtitle = ''

    try:
      summary = video_details.xpath('//div[@id="videoMetaData"]//div[@class="longdesc"]/p')[0].text
    except:
      summary = ''

    thumb = re.search("\['thumb'\].+?'([^']+)", details).group(1)

    rtmpServer = re.search("\['rtmpServer'\].+?'([^']+)", details).group(1)
    rtmpPath = re.search("\['rtmpPath'\].+?'([^']+)", details).group(1)
    rtmpPath = re.sub('\.flv$', '', rtmpPath)

    dir.Append(RTMPVideoItem(url=rtmpServer, clip=rtmpPath, title=title, subtitle=subtitle, summary=summary, thumb=Function(Thumb, url=thumb) ) )

  return dir

####################################################################################################

def Thumb(url):
  if url != None:
    try:
      data = HTTP.Request(url, cacheTime=CACHE_1WEEK).content
      return DataObject(data, 'image/jpeg')
    except:
      pass

  return Redirect(R(ICON))
