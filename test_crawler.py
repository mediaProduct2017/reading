from unittest import TestCase
from crawl import Crawler


class TestCrawler(TestCase):
    def test_init_del(self):
        c = 'newsdb'
        try:
            Crawler(c)
        except AttributeError:
            # except ValueError:
            self.fail('Crawler init or del raised Exception unexpectedly')

    def test_init_del_noName(self):
        self.assertRaises(Exception, Crawler, )
        # self.assertRaises(AttributeError, Crawler().__del__, )

    def test_dbcommit(self):
        try:
            Crawler('newsdb').dbcommit()
        except:
            self.fail('Crawler database commit raised Exception unexpectedly')

    def test_createindextables(self):
        a = Crawler('newsdb')
        a.createindextables()
        # print a.__dict__
        results = a.session.execute(
            "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' AND TABLE_SCHEMA = 'newsdb'")
        self.assertEqual([i[2] for i in results], ['link', 'linkword', 'urllist', 'wordlist', 'wordlocation'])
        # fetchone() is similar to next() of an iterator
