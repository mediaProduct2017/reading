from unittest import TestCase, main
from create_tables import TableCreator


class TestTableCreator(TestCase):
    def test_init_del(self):
        c = 'newsdb'
        try:
            TableCreator(c)
        except AttributeError:
            # except ValueError:
            self.fail('Crawler init or del raised Exception unexpectedly')

    def test_init_del_noName(self):
        self.assertRaises(Exception, TableCreator, )
        # self.assertRaises(AttributeError, Crawler().__del__, )

    def test_dbcommit(self):
        try:
            TableCreator('newsdb').dbcommit()
        except:
            self.fail('Crawler database commit raised Exception unexpectedly')

    def test_createindextables(self):
        a = TableCreator('newsdb')
        a.createindextables()
        # a.dbcommit()
        # when creating tables, sqlalchemy commits automatically
        # If the tables already exist, nothing happens, raise no exceptions
        # print a.__dict__
        results = a.session.execute(
            "SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' AND TABLE_SCHEMA = 'newsdb'")
        self.assertEqual([i[2] for i in results], ['link', 'linkword', 'urllist', 'wordlist', 'wordlocation'])
        # results.fetchall() is also doable
        # fetchone() is similar to next() of an iterator

if __name__ == '__main__':
    main()
