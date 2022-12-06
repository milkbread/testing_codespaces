from bs4 import BeautifulSoup
from pandas import read_csv
from IPython.display import display, HTML
from ipywidgets import interact
from requests import get

import numpy as numpy
import matplotlib.pyplot as plt
from wordcloud import WordCloud

class TextPlusUserStories():

    _base_url = 'https://repository.de.dariah.eu/1.0/dhcrud/21.11113/%s/data'
    _user_stories = _base_url % '0000-000E-67EF-2'
    _keywords = _base_url % '0000-000E-67EF-3'

    # basic function to load list of user_stories from dariah
    def load_user_stories(self: Self@TextPlusUserStories) -> list:

        # load user story dataset
        dataframe = read_csv(self._user_stories, sep="\t")

        # rename/simplify column names
        dataframe = dataframe.rename(columns={
            'Unnamed: 0': 'name',
            'controlled-DFG-subject-area': 'subject_area',
            'keywords-sentences': 'kw_sentences',
            'keywords-condensed': 'kw_short',
            'URL': 'url',
            'data-domain': 'domain'
        })

        # sort by 'url'
        dataframe = dataframe.sort_values('url')

        # Store all user stories in an array
        # ...in preparation for interactive select
        stories = [('Bitte auswählen', '')]
        for user_story in dataframe[['url', 'name']].itertuples():
            domain, author = user_story.name.split('_', 1)
            number = user_story.url.rsplit('-', 1)[1].replace('/', '')
            name = '%s - %s (%s)' % (number, author, domain)
            stories.append((name, user_story.url))

        return stories

    def _center_wordcloud(self):
        display(HTML("""
        <style>
        .jp-RenderedImage {
            display: table-cell;
            text-align: center;
            vertical-align: middle;
        }
        </style>
        """))

    def _wordcloud(self, article):

        self._center_wordcloud()

        text_list = []
        for p in article.find_all('p')[3:]:
            text_list.append(p.text)

        x, y = numpy.ogrid[:300, :300]

        mask = (x - 150) ** 2 + (y - 150) ** 2 > 130 ** 2
        mask = 255 * mask.astype(int)

        wc = WordCloud(background_color="white", mask=mask)
        wc.generate(' '.join(text_list))

        plt.axis("off")
        plt.imshow(wc, interpolation="bilinear")
        plt.show()


    # basic function, which is called by "interact"
    def _show_story(self, url):
        if url:
            # get full html content of user_story
            html_text = get(url).text

            # modify html content to display user story without any header
            user_story = BeautifulSoup(html_text, 'html.parser')
            # 1. get artice content only
            article = user_story.find('article')
            # 2. get body content
            body = user_story.find('body')
            # 3. clear body and add only article to body of user story
            body.clear()
            body.append(article)


            self._wordcloud(article)
            display(HTML(str(user_story)))

    # basic function that to add a interactive select to notebook
    def interact(self: Self@TextPlusUserStories) -> None:
        interact(self._show_story, url=self.load_user_stories());
