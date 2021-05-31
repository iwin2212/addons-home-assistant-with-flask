# encoding: utf-8

##=== Read news: dantri, vietnamnet, genk ===#
##=== exlab, Jan. 11, 2019 ===#
##=== version 1.0 ===#
##==================#

## Config in configuration.yaml file for Home Assistant
## read_news:

## Code script:
##read_news:
##  sequence:
##    - service: read_news.get
##      data:
##        news_name: 'vietnamnet' # ('dantri', 'dantri_all', 'vietnamnet', 'genk')
##        tts_service: tts.google_say
##        entity_id: 'media_player.room_player'
##        cache: false # optional, default = false
##==================#

import requests
from bs4 import BeautifulSoup

## config
DOMAIN = 'read_news'
SERVICE_GETINFO = 'get'

## data service
CONF_NEWS_NAME= 'news_name'
CONF_TTS_SERVICE = 'tts_service'
CONF_ENTITY_ID = 'entity_id'
## 'tts.google_translate_say'
CONF_CACHE = 'cache'

## 
source_url = {'dantri': 'https://dantri.com.vn', 'dantri_all': 'https://dantri.com.vn', 'vietnamnet': 'https://vietnamnet.vn', 'genk': 'http://genk.vn'}

def setup(hass, config):

    ##----------------------------
    REMOVE_FREFIX = '(Dân trí) - '
    def get_contents (url_):
        res = requests.get(url_).text
        soup = BeautifulSoup(res, 'lxml')
        title = (soup.title.text).split('|')[0].strip() + '. '
        # print(title)
        content = soup.find('meta', attrs = {'name': 'description'}).get("content")
        content = content.replace(REMOVE_FREFIX, "").strip()
        res_content = title +  content
        return res_content
    ##----------------------------

    def get_text_news(data_call):
        ## Get data
        news_name = data_call.data.get(CONF_NEWS_NAME)
        tts_service = data_call.data.get(CONF_TTS_SERVICE)
        entity_id = data_call.data.get(CONF_ENTITY_ID)
        if tts_service == 'tts.google_translate_say':
            cache = data_call.data.get(CONF_CACHE, 'false')

        ## begin
        CONF_NO = 'Tin số '
        i = 0
        res_text = []
        
        ## scrape website data
        pre_link = source_url.get(news_name)
        res = requests.get(pre_link).text
        soup = BeautifulSoup(res, 'lxml')
        
        ## dantri
        ## get dantri news-events
        if news_name == 'dantri':
            ultag = soup.find('ul', {'class': 'ul1 ulnew'})
            for litag in ultag.find_all('li'):
                i += 1
                atag = litag.find('a', href = True)
                link = pre_link + atag['href']
                ## get content from link
                itext = CONF_NO + str(i) + ': ' + get_contents(link)
                res_text.append(itext)
            res_text.append("Nguồn Dân trí")
            text_news = ' '.join(res_text)
            print(text_news)
                
        ## get dantri all news        
        elif news_name == 'dantri_all':
            pre_match = ['/xa-hoi/','/the-gioi/','/the-thao/','/giao-duc-khuyen-hoc/','/kinh-doanh/','/bat-dong-san/','/van-hoa/','/giai-tri/','/phap-luat/','/suc-khoe/','/suc-manh-so/','/o-to-xe-may/','/khoa-hoc-cong-nghe/']
            name_match = {'/xa-hoi/': 'xã hội','/the-gioi/': 'thế giới','/the-thao/': 'thể thao','/giao-duc-khuyen-hoc/': 'giáo dục','/kinh-doanh/': 'kinh doanh','/bat-dong-san/': 'bất động sản','/van-hoa/': 'văn hóa','/giai-tri/': 'giải trí','/phap-luat/': 'pháp luật','/suc-khoe/': 'sức khỏe','/suc-manh-so/': 'sức mạnh số','/o-to-xe-may/': 'ô tô xe máy','/khoa-hoc-cong-nghe/': 'khoa học công nghệ'}
            for divtag in soup.findAll('div', attrs = {'class': 'mt1 clearfix'}):
                atag = divtag.find('a', href = True)
                link = pre_link + atag['href']
                for pre_m in pre_match:
                    if link.find(pre_m) > 0:
                        itext = 'Tin ' + name_match.get(pre_m) + ': ' + get_contents(link)
                        res_text.append(itext)
                        break
            text_news = ' '.join(res_text)
                   
        ## vietnamnet
        elif news_name == 'vietnamnet':
            ultag = soup.find('ul', {'class': 'height-list'})
            for litag in ultag.find_all('li'):
                i += 1
                atag = litag.find('a', href=True)
                link = pre_link + atag['href']
                ## get content from link
                itext = CONF_NO + str(i) + ': ' + get_contents(link)
                res_text.append(itext)
            text_news = ' '.join(res_text)

        elif news_name == 'genk':
            arr_link = []
            ## 2 first links
            ichk = 0
            for divtag in soup.find_all('div', {'class': 'gfn-postion', 'data-boxtype': 'homenewsposition'}):
                if ichk < 2:
                    atag = divtag.find_all('a', href=True)
                    ilink = pre_link + (atag[0])['href']
                    arr_link.append(ilink)
                    ichk += 1
            ## 3 next links
            ichk = 0
            for litag in soup.find_all('li', {'class': 'klwfnswn swiper-slide', 'data-boxtype': 'homenewsposition'}):
                if ichk < 3:
                    atag = litag.find_all('a', href=True)
                    ilink = pre_link + (atag[0])['href']
                    arr_link.append(ilink)
                    ichk += 1
            ## 5 next links
            ichk = 0
            for h4tag in soup.find_all('h4', {'class': 'knswli-title'}):
                if ichk < 5:
                    atag = h4tag.find_all('a', href=True)
                    ilink = pre_link + (atag[0])['href']
                    arr_link.append(ilink)
                    ichk += 1            
            ## get content from link
            for link in arr_link:
                i += 1
                itext = CONF_NO + str(i) + ': ' + get_contents(link)
                itext = itext.replace('\n', ' ').replace('<br />', ' ')
                res_text.append(itext)
                text_news = ' '.join(res_text)
                text_news = ' '.join(text_news.splitlines())

        ## result: text_news             
        ## service data
        # print(text_news)
        if tts_service == 'tts.google_translate_say':
            service_data = {'entity_id': entity_id, 'message': text_news, 'cache': cache}
        ## call service on Home assistant
        hass.services.call(tts_service.split('.')[0], tts_service.split('.')[1], service_data)
        
    hass.services.register(DOMAIN, SERVICE_GETINFO, get_text_news)
    return True
