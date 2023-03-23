import requests
import matplotlib.pyplot as plt
import time
import nlp_analysis as nlp


def tuples_to_lists(terms):
    term_list = []
    for term in terms:
        term_list.append(term[0])

    return term_list




def get_similarity_score_between_languages(l1, l2, l1_terms, l2_terms):
    sim_score = 0

    if type(l1_terms[0]) == 'tuple':
        l1_terms = tuples_to_lists(l1_terms)
    if type(l2_terms[0]) == 'tuple':
        l2_terms = tuples_to_lists(l2_terms)

    for t_l1 in l1_terms:
        for t_l2 in l2_terms:
            query = 'http://api.conceptnet.io/relatedness?node1=/c/' + l1 + '/'+ t_l1 + '&node2=/c/' + l2 + '/' + t_l2
            
            obj = requests.get(query).json()
            sim_score += obj['value']
            time.sleep(2)

    return sim_score







def get_similarity_score_between_methods(method1_terms, method2_terms, language='en'):

    if type(method1_terms[0]) is tuple:
        method1_terms = tuples_to_lists(method1_terms)
    if type(method2_terms[0]) is tuple:
        method2_terms = tuples_to_lists(method2_terms)

    sim_score = 0
    returned_values = 0
    for t_l1 in method1_terms:
        for t_l2 in method2_terms:
            query = 'http://api.conceptnet.io/relatedness?node1=/c/' + language + '/'+ t_l1 + '&node2=/c/' + language + '/' + t_l2
            
            obj = requests.get(query).json()
            sim_score += obj['value']
            time.sleep(2)

    return sim_score


def visualize_drift(freq_sim, fastt_sim, word2vec_sim, dates):

    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    ax1.set_xticklabels(dates)
    plt.ylabel('Relatedness of Generated Terms')

    ax1.plot(word2vec_sim, label='Word2Vec')
    ax1.plot(fastt_sim, label='FastText')
    ax1.plot(freq_sim, label='Frequency Distribution')
    plt.legend(loc='upper left')
    plt.xticks(rotation=45)



def demonstrate_all(start='2022-08-15'):
    arts_en, arts_fr = nlp.generate_test_corpora(start)

    en_data = {'frequency' : [],
                'word2vec' : [],
                'FastText' : []}
    fr_data = {'frequency' : [],
                'word2vec' : [],
                'FastText' : []}
    
    for arts in arts_en:
        pipe = nlp.run_stanza_pipeline(arts)
        en_data['frequency'].append(nlp.related_from_most_frequent(pipe))
        en_data['word2vec'].append(nlp.related_from_word2vec('africa', pipe))
        en_data['FastText'].append(nlp.related_from_fasttext('africa', pipe))

    for arts in arts_fr:
        pipe = nlp.run_stanza_pipeline(arts, language='fr')
        fr_data['frequency'].append(nlp.related_from_most_frequent(pipe, language='fr'))
        fr_data['word2vec'].append(nlp.related_from_word2vec('afrique', pipe, language='fr'))
        fr_data['FastText'].append(nlp.related_from_fasttext('afrique', pipe, language='fr'))




    #Gets the sim scores between English and French languages
    freq_sim = []
    for i in range(len(en_data['frequency'])):
        en = en_data['frequency'][i]
        fr = fr_data['frequency'][i]
        sim_score = get_similarity_score_between_languages('en', 'fr', en, fr)
        freq_sim.append(sim_score)
        print('Calculating Frequency relatedness...')

        
    word2vec_sim = []
    for i in range(len(en_data['word2vec'])):
        en = tuples_to_lists(en_data['word2vec'][i])
        fr = tuples_to_lists(fr_data['word2vec'][i])
        sim_score = get_similarity_score_between_languages('en', 'fr', en, fr)
        word2vec_sim.append(sim_score)
        print('Calculating word2vec relatedness...')
        
    fastt_sim = []
    for i in range(len(en_data['FastText'])):
        en = tuples_to_lists(en_data['FastText'][i])
        fr = tuples_to_lists(fr_data['FastText'][i])
        sim_score = get_similarity_score_between_languages('en', 'fr', en, fr)
        fastt_sim.append(sim_score)
        print('Calculating FastText relatedness...')

    dates = ['Aug 14', 'Aug 15', 'Aug 16', 'Aug 17', 'Aug 18', 'Aug 19', 'Aug 20', 'Aug 21']


    return en_data, fr_data, freq_sim, fastt_sim, word2vec_sim


    visualize_drift(freq_sim, fastt_sim, word2vec_sim, dates)

    
