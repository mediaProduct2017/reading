from unittest import TestCase
from crawl import Crawler


class TestCrawler(TestCase):
    def test_init_del(self):
        c = 'newsdb'
        try:
            a = Crawler(c)
            # print a.session
        except AttributeError:
            # except ValueError:
            self.fail('Crawler init raised Exception unexpectedly')

    def test_init_noOrWrongName(self):
        # Crawler()
        self.assertRaises(Exception, Crawler, )
        # self.failUnlessRaises(Exception, Crawler, )
        #
        # self.assertRaises(AttributeError, Crawler().__del__, )
        # self.failUnlessRaises(AttributeError, Crawler, )
        # self.assertRaises(Exception, Crawler, 1)

    def test_dbcommit(self):
        c = 'newsdb'
        try:
            Crawler(c).dbcommit()
        except ValueError:
            self.fail('Crawler commit raised Exception unexpectedly')