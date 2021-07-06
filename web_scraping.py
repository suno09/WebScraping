import requests
import re
import json
import string
from bs4 import BeautifulSoup
from unidecode import unidecode
from itertools import count
from collections import defaultdict


def load_data(url: str):
    """
    load data html from web
    :param url:
    :return: text html
    """

    page = requests.get(url=url)
    soup = BeautifulSoup(page.content, 'html.parser')
    return soup


def eurekasante_lexicon_scraping():
    print('Start scrapping from eurekasante...')
    lexicons = {}
    for letter in string.ascii_uppercase:
        print(f'Letter {letter}...')
        letter_lexicons = []
        bs_html = load_data(
            f'https://eurekasante.vidal.fr/lexique-medical/{letter}.html')
        dl = bs_html.find(name='dl')
        # get the dt and dd
        dts = dl.find_all(name='dt')
        dds = dl.find_all(name='dd')
        for dt, dd in zip(dts, dds):
            a = dt.find(name='a')
            print(f'=> {a.text}')
            ps = dd.find_all(name='p')
            letter_lexicons.append({
                'name': a['name'],
                'text': a.text.lower(),
                'desc': '\n'.join(map(lambda p: p.text, ps))
            })

        lexicons[letter] = letter_lexicons

    with open('eurekasante_lexicons.json', 'w') as w:
        json.dump(lexicons, w, indent=4)


def doctissimo_lexicon_scraping():
    letters = ['0-9'] + list(string.ascii_uppercase)
    print('Start scrapping from doctissimo...')
    lexicons = {}
    for letter in letters:
        print(f'Letter {letter}...')
        letter_lexicons = []
        bs_html = load_data(
            f'https://www.doctissimo.fr/sante/dictionnaire-medical/initiale-{letter}.htm')
        ul = bs_html.find(name='ul', class_='content-listing multi-columns-1')
        # get the dt and dd
        lis = ul.find_all(name='li')
        for li in lis:
            a = li.find(name='a')
            print(f'=> {a.text}')
            bs_html_href = load_data(a['href'])
            div = bs_html_href.find(name='div',
                                    class_='row doc-block-definition')
            div_content = div.find(name='div').find(name='div')
            ps = div_content.find_all(name='p')
            letter_lexicons.append({
                'name': unidecode(a.text.lower()).replace(' ', '-'),
                'text': a.text.lower(),
                'desc': '\n'.join(map(lambda p: p.text, ps))
            })

        lexicons[letter] = letter_lexicons

    with open('doctissimo_lexicons.json', 'w') as w:
        json.dump(lexicons, w, indent=4)


def dict_academie_med_scraping():
    # pattern = r'<p class="terme"><b>(.+?)(?:</b>)'
    dics = defaultdict(list)
    for i in count(start=1, step=1):
        print(f'Page {i}...')
        try:
            bs_html = load_data(
                f'http://dictionnaire.academie-medecine.fr/index.php?q=&page={i}')
            ps = bs_html.find_all(name='p', class_='terme')
            if ps.__len__() == 0:
                break

            for p in ps:
                b = p.find(name='b')
                new_b = re.sub(r"\(.*?\)", "", b.text).strip().lower()
                dics[new_b[0]].append({
                    'name': unidecode(new_b.replace(' ', '-')),
                    'text': new_b,
                    'desc': ''
                })
        except Exception as e:
            print(f"=> Echec page : {e}")

    with open('dict_academie_med.json', 'w') as w:
        json.dump(dics, w, indent=4)


def vidal_substance_medicaments_scraping():
    print('Start scrapping from vidal...')
    substances = defaultdict(list)
    for letter in string.ascii_uppercase:
        print(f'Letter {letter}...')
        letter_substances = []
        bs_html = load_data(
            f'https://www.vidal.fr/Sommaires/Substances-{letter}.htm')
        ul = bs_html.find(name='ul',
                          class_='substances list_index has_children')
        # get the lis
        lis = ul.find_all(name='li')
        for li in lis:
            medics = []
            a = li.find(name='a')
            print(f'=> {a.text}')
            bs_html_href = load_data(f"https://vidal.fr/{a['href']}")
            ul_a = bs_html_href.find(name='ul', class_='list_index')
            if ul_a:
                lis_a = ul_a.find_all(name='li')
                for li_a in lis_a:
                    t = li_a.text.strip().lower()
                    medics.append({
                        'name': unidecode(t.replace(' ', '-')),
                        'text': t
                    })

            letter_substances.append({
                'name': unidecode(a.text.lower()).replace(' ', '-'),
                'text': a.text.lower(),
                'medics': medics
            })

        substances[letter] = letter_substances

    with open('vidal_medics_by_subs.json', 'w') as w:
        json.dump(substances, w, indent=4)


if __name__ == '__main__':
    # eurekasante_lexicon_scraping()
    # doctissimo_lexicon_scraping()
    dict_academie_med_scraping()
    # vidal_substance_medicaments_scraping()
