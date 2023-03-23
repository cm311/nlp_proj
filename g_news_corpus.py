from newspaper import Article, ArticleException
from bs4 import BeautifulSoup
from datetime import timedelta
from datetime import datetime as dtime
import datetime
import requests
import time
import urllib3
import random, math


#hl: language
#gl: country
#ceid: country: language
#(en, jp, fr, de)
lang_codes = ['en', 'jp', 'fr', 'de', 'it', 'es']
def get_news_meta_data(keyword='', start_date=0, end_date=0, language='en', depth=0):
    '''   
    Constructs a query string, and queries google news RSS with it.  Parses the returned metadata,
    and returns a list of 'item' objects which can be further parsed in order to extract returned
    articles and further information.


    Attributes:
        lang_string - a string to add to the query URL that specifies language and locale
        query - the final query to pass to google news
        http - urllib3 object to send the query
        response - the HTTP response returned from the query
        soupy - BeautifulSoup object after parsing 'response'
        items - a list of 'item' object from the returned http.

    :param
        keyword - the term to search and scrape google news for.
        start_date - the earliest date that scraped articles are published  yyyy-mm-dd format
        end_date - the latest date that scraped articles are published   yyyy-mm-dd format
        language - the language of the articles to look for.
        depth - how many times to recurse, if the amount of articles is close to 100 (max returned by google news)

    :return:
        A list of 'item' objects that serve as metadata for further scraping.

    '''
    
    if start_date == 0 or end_date == 0:
        start_date = str(datetime.date.today())
        end_date = str(datetime.date.today() + timedelta(days = 1))
    
    if language == 'en':
        country = 'US'
    else:
        country = language

    lang_string = '&ceid=' + country + ':' + language + '&hl=' + language + '-' + country + '&gl=' + country
    query = 'https://news.google.com/rss/search?q=' + keyword + '+after:' + start_date + '+before:' + end_date + lang_string
    #sample lang string ->    '&ceid=US:en&hl=en-US&gl=US'
    #sample working query ->    https://news.google.com/rss/search?q=usa+after:2022-08-01+before:2022-08-03&ceid=US:en&hl=en-US&gl=US
    http = urllib3.PoolManager()
    response = http.request("GET", query)
    soupy = BeautifulSoup(response.data, 'html.parser')
    
    items = soupy.contents[1].find_all('item')

    #if depth is greater than max depth, to change so that a user can enter max articles.  Right now we just recurse once.
    #max_depth 1 = 100 articles
    #max_depth 2 = 400 articles
    #max_depth 3 = 800 articles
    #amount of articles returns =  100 * 2^max_depth.
    if(depth == 3):
        return items
    
    if len(items) > 85 and int(days_between(start_date, end_date)) != 1:
        #drilling once
        depth+=1

        #parse start_date and end_date to get less articles.
        d = int(days_between(start_date, end_date)/2)
        mid_date = dtime.strptime(start_date, "%Y-%m-%d") + timedelta(days=d)
        mid_date = mid_date.strftime("%Y-%m-%d")
        
        if mid_date == start_date:
            return items
        
        items1 = get_news_meta_data(keyword, start_date, mid_date, language, depth)
        items2 = get_news_meta_data(keyword, mid_date, end_date, language, depth)
        items = items1 + items2
    
    return items







def days_between(d1, d2):
    ''' 
    Helper function.  Takes in two dates and returns the number of days between them.
    Date format - yyyy-mm-dd

    Attributes:

    :param
        d1 - the first date
        d2 - the second date

    :return: 
        an integer value, the number of days between d1 and d2

    '''

    d1 = dtime.strptime(d1, "%Y-%m-%d")
    d2 = dtime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)







def news_items_to_dict(items):
    '''
    Takes in a list of items returned from the get_news_meta_data function, and further
    parses them to later be scraped.


    Attributes:

    :param
        items - a list of metadata items returned from get_news_meta_data

    :return:
        returns a list of dictionaries that have the following format

        {'title' : the article title,
        'pubdate' : the date the article was published,
        'link' : the link to the article online}
    
    '''
    article_meta_data = []
    
    for item in items:
        title = item.find('title')
        pubdate = item.find('pubdate')

        stringed = str(item)
        start = stringed.find('href')
        stringed = stringed[start+6:]
        link = stringed[:stringed.find('"')]
        
        article_meta_data.append({'title' : title,
                                 'pubdate' : pubdate,
                                 'link' : link})
    return article_meta_data





def get_article_text(meta_data):
    '''
    Takes in metadata in the form of a dictionary returned from the news_item_to_dict function.
    Uses the Article object from the Newspaper3k library to return the text of the article.
    
    Attributes:
        a - Newspaper3k Article object.

    :param:
        meta_data - a dictionary.  Single article's metadata in the format returned from news_item_to_dict

    :return:  A string representing the text of an article.

    '''
    a = Article(meta_data['link'])
    a.download()
    a.parse()
    return(a.text)





def build_corpus(article_meta_data, show_progress=True):
    '''
    Takes in a list of dict, as returned from the method news_items_to_dict().  Scrapes each article according
    to the links in the metadata and returns a list of the articles' text.

    Attributes:
        articles - the list of articles
        fails - how many times this method raised an ArticleException (when we get a 404 or something like that)
        processed - how many articles are done processing.  used to give some feedback on the progress to the user.

    :params
        article_meta_data - a list of dict object containing the metadata, and the link of the article to scrape
        show_progress - If set to false, will show the progress of the article scraping.

    :return:
        articles - the list, each element is the text of an article.  A corpus of documents to do some analysis on,
        and generate the related terms.  

    '''
    articles = []
    fails = 0
    processed=0
    print('Building corpus from ' + str(len(article_meta_data)) + ' articles...')
    for article in article_meta_data:
        processed+=1
        try:
            articles.append(get_article_text(article))
        except ArticleException:
            fails += 1

        if show_progress == True:
            print('Progress: {:.2f} %    Fail Rate: {:.2f} %  '.format(processed/len(article_meta_data) * 100, fails/processed * 100), end='\r')
    print('Complete          ')
    
    return articles







def get_news_articles_text(keyword='', start_date=0, end_date=0, language='en',):
    '''
    ****better to use create_articles_from_keyphrase instead.
    Combines the methods get_news_meta_data and build_corpus in order to generate a corpus of text from a keyword.
    Not really used, better to use create_articles_from_keyphrase instead.

    Attributes:
        meta_data - meta_data of articles, including links to them
        articles_text - corpus of articles

    :params
        keyword - the term to search for
        start_date - earliest article date
        end_date - latest article date
        language - the 2 letter language code.

    :return:
        returns a list of strings, the corpus of articles.
    '''

    meta_data = get_news_meta_data(keyword, start_date, end_date, language)
    articles_text = build_corpus(meta_data)
    return articles_text







def create_articles_from_keyphrase(keyword='', start_date=0, end_date=0, language='en',):
    '''
        Puts all the above methods together to query Google News.  Scrapes all the articles and puts
        them into a list of articles.  The main method to build a corpus from Google News for later NLP analysis.

        Attributes:
            articles - corpus of articles, a list of strings

        :params
            keyword - the term to search for
            start_date - the earliest date of the articles
            end_date - the latest date of the articles
            language - language of articles to search for.

        :return:
            articles - a list of strings, each element corresponding to the body of an article.

    '''

    print('Querying ' + language + ' articles...')
    articles = get_news_meta_data(keyword, start_date, end_date, language)
    articles = list(set(articles))
    print('Number of articles retrieved: ' + str(len(articles)))
    articles = news_items_to_dict(articles)
    articles = build_corpus(articles)
    remove_short(articles)
    print('\n\n')
    return articles








def multi_lang_articles(keyphrase, start_date, end_date):
    '''
    Attributes:
        arts_en - corpus of english articles
        arts_fr - corpus of french articles
        arts_de - corpus of german articles
        arts_es - corpus of spanish articles
        arts_it - corpus of italian articles


    :param
        keyword - the term to search for
        start_date - the earliest date of the articles
        end_date - the latest date of the articles

    :return:
        a tuple of 5 lists, each corresponding to a corpus of articles in the following languages
        English, French, German, Spanish, Italian.
    '''

    arts_en = create_articles_from_keyphrase(keyphrase, start_date, end_date, 'en')
    print('\n')
    arts_fr = create_articles_from_keyphrase(keyphrase, start_date, end_date, 'fr')
    print('\n')
    arts_de = create_articles_from_keyphrase(keyphrase, start_date, end_date, 'de')
    print('\n')
    arts_es = create_articles_from_keyphrase(keyphrase, start_date, end_date, 'es')
    print('\n')
    arts_it = create_articles_from_keyphrase(keyphrase, start_date, end_date, 'it')
    print('\n')
    
    return arts_en, arts_fr, arts_de, arts_es, arts_it





def flatten_corpus(articles):
    '''
    Takes in a list of articles (strings) and flattens the list so that one large string is returned.
    Used to more quickly build a Stanza pipeline

    Attributes:
        flattened_articles - a single string containing all the articles in the corpus
        

    :params
        articles - the list of articles to flatten

    :return:
        flattened_articles - a string of all the articles concatenated together

    '''

    flattened_articles = ""
    flattened_articles = '           '.join(art for art in articles)
    
    return flattened_articles




def remove_short(articles):
    for a in articles:
        if (len(a)) < 500:
            del articles[articles.index(a)]








def clean_and_save(articles, keyword, start, end):
    remove_short(articles)
    
    filename = 'articles/' + keyword + ' ' + start + ' ' + end + '.txt'
    # open file in write mode
    with open(filename, 'w', encoding='utf-8') as fp:
        for art in articles:
            # write each item on a new line
            fp.write("%s\n" % art)
        print('Wrote articles to txt\n')







def get_articles_incrementing_date(keyword):
    
    start = '2022-01-01'
    
    while dtime.strptime(start, "%Y-%m-%d") < datetime.datetime.today():
        end = dtime.strptime(start, "%Y-%m-%d") + datetime.timedelta(days=20)
        end = end.strftime("%Y-%m-%d")
        
        print('Using date ranges ' + start + ' ' + end)
        articles = create_articles_from_keyphrase(keyword, start, end)
        clean_and_save(articles, keyword, start, end)

        start=dtime.strptime(end, "%Y-%m-%d") + datetime.timedelta(days=1)
        start = start.strftime("%Y-%m-%d")




def generate_test_corpora(start):
    arts_en = []
    arts_fr = []

    days_ = 1

    first = start
    while days_ < 11:
        start = dtime.strptime(first, "%Y-%m-%d") + datetime.timedelta(days=days_ - 1)
        start = start.strftime("%Y-%m-%d")
        print(start)

        next_ = dtime.strptime(start, "%Y-%m-%d") + datetime.timedelta(days=1)
        next_ = next_.strftime("%Y-%m-%d")
        print(next_)

        arts_en.append(create_articles_from_keyphrase('africa', start, next_, language='en'))
        arts_fr.append(create_articles_from_keyphrase('afrique', start, next_, language='fr'))

        days_ = days_ + 1

    return arts_en, arts_fr
    