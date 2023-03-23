from nltk.corpus import stopwords
from gensim.models import Word2Vec, FastText
import nltk
import requests
import stanza
from g_news_corpus import *




def run_stanza_pipeline(articles, language='en'):
    nlp = stanza.Pipeline(language, processors='tokenize,pos,lemma')
    flattened_articles = flatten_corpus(articles)
    tagged_corpus = nlp(flattened_articles)
    print('Tagged corpus created from NLP pipeline.\n\n\n\n')
    return tagged_corpus





def get_word_lemmas(corpus, language='en'):
    '''
    '''

    lemmas = []
    adjectives = []
    nouns = []
    verbs = []
    

    for sentence in corpus.sentences:
        for word in sentence.words:
            lemmas.append(word.lemma)
            if word.upos == 'ADJ':
                adjectives.append(word.lemma)
            if word.upos == 'NOUN':
                nouns.append(word.lemma)
            if word.upos == 'VERB':
                verbs.append(word.lemma)

    lemmas = stopword_removal(lemmas, language)
    adjectives = stopword_removal(adjectives, language)
    nouns = stopword_removal(nouns, language)
    verbs = stopword_removal(verbs, language)


    return lemmas, adjectives, nouns, verbs
        





#for sentiment analysis, There is a paper that shows that Adjectives and nouns
#are the parts of speech that provide the most extra meaning.  Verbs do in some
#cases.  For this reason I am weighting Adjectives and nouns higher than verbs when
#assigning the related terms.  (.4, .4, .2)
def related_from_most_frequent(tagged_corpus, language='en'):
    '''

    '''

    lemmas, adjectives, nouns, verbs = get_word_lemmas(tagged_corpus, language)

    freq = nltk.FreqDist(lemmas)

    words = []
    for i in freq.most_common():
        if i[0] in adjectives:
            words.append(i[0])
        if len(words) == 8:
            break

    return words





def related_from_word2vec(keyword, corpus, language='en'):
    sentences = sentence_tokenize(corpus, language)

    if len(sentences) < 250:
        min_c = 2
    if len(sentences) > 250 and len(sentences) <= 1000:
        min_c = 3
    if len(sentences) > 1000 and len(sentences) <=3000:
        min_c = 4
    if len(sentences) > 3000 and len(sentences) <= 6000:
        min_c = 5
    if len(sentences) > 6000 and len(sentences) <= 10000:
        min_c = 6
    if len(sentences) > 10000 and len(sentences) <= 13000:
        min_c = 7
    if len(sentences) > 13000 and len(sentences) <= 13000:
        min_c = 8
    if len(sentences) > 16000 and len(sentences) <= 20000:
        min_c = 9
    if len(sentences) > 20000 and len(sentences) <= 25000:
        min_c = 10
    if len(sentences) > 25000 and len(sentences) <= 35000:
        min_c = 11
    if len(sentences) > 35000:
        min_c = 12

    model = Word2Vec(sentences=sentences, window=5, min_count=min_c, workers=4)
    similar = model.wv.most_similar(keyword)
    return similar[:8]





def related_from_fasttext(keyword, corpus, language='en'):
    sentences = sentence_tokenize(corpus, language)

    if len(sentences) < 250:
        min_c = 1
    if len(sentences) > 250 and len(sentences) <= 1000:
        min_c = 2
    if len(sentences) > 1000 and len(sentences) <=3000:
        min_c = 3
    if len(sentences) > 3000 and len(sentences) <= 6000:
        min_c = 4
    if len(sentences) > 6000 and len(sentences) <= 10000:
        min_c = 5
    if len(sentences) > 10000 and len(sentences) <= 13000:
        min_c = 6
    if len(sentences) > 13000 and len(sentences) <= 13000:
        min_c = 7
    if len(sentences) > 16000 and len(sentences) <= 20000:
        min_c = 8
    if len(sentences) > 20000 and len(sentences) <= 25000:
        min_c = 9
    if len(sentences) > 25000 and len(sentences) <= 35000:
        min_c = 10
    if len(sentences) > 35000:
        min_c = 11


    model = FastText(window=4, min_count=min_c, sentences=sentences, workers=4)
    similar = model.wv.most_similar(keyword)
    return similar[:8]





def stopword_removal(doc, language='en'):
    if language == 'en':
        stopWords = set(stopwords.words('english'))
    if language == 'fr':
        stopWords = set(stopwords.words('french'))
    stopWords.update({',', '.', '’', '“', '”', ')', '(', '—', '``', '?', ':', ';', "''", '/', '–', '‘',
                     '$', '%', '[', ']', "'s", '!', "'", '-', '}', '{', '//', '"', '«', '»', 'could', 'get', 'come', 'go',
                     'also', 'might', 'many'})

    tokens = [i for i in doc if i not in stopWords]

    return tokens









def sentence_tokenize(corpus, language='en'):

    all_sentences = []
    for sentence in corpus.sentences:
        new_sentence = []
        for word in sentence.words:
            if word.lemma != None:
                new_sentence.append(word.lemma.lower())
        new_sentence = stopword_removal(new_sentence, language)
        all_sentences.append(new_sentence)

    return all_sentences



