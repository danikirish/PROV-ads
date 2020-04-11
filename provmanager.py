#!/usr/bin/env python


from prov.model import *
import prov.model as prov
import sqlite3 as lite
from os import path
import os
import matplotlib.pyplot as plt
from prov.dot import prov_to_dot
import matplotlib.image as mpimg

from crawlmanager import CrawlManager
from provanalyser import ProvAnalyser


class ProvManager():
    def __init__(self, output_fp=path.join(os.getcwd(), "Crawls", "Results"), db_fp="/Users/Danik/Desktop/KCL/YEAR_3/PRJ/Crawls/crawl-data.sqlite"):
        self.db_fp = db_fp
        self.output_fp = output_fp
        self.crawls = {}
        self.documents = {}
        self.all_tp_hosts = {}
        self.cur = None
        self.last_crawl = None
        self.tester = None
        
    def main(self):
        self.cur = self.db_connect()
        recorded = False
        crawls_queue = []
        for crawl in self.cur.execute("select crawl_id from crawl"):
            crawl_fp = path.join(self.output_fp, "crawl%d" % crawl[0])
            if not path.isdir(crawl_fp):
                recorded = True
                crawls_queue.append(crawl[0])

        self.record_crawls(crawls_queue)
        if not recorded:
            print("No crawls to record")
        else:
            print("Finished recording")

        self.analyse_crawls(crawls_queue)
        # self.create_prov()
        # self.record_prov()
        # self.write_prov()
        # img = mpimg.imread(self.tester)
        # impgplot = plt.imshow(img)
        # plt.show()
        # input('...')


    def record_crawls(self, crawls):
        for crawl in crawls:
            print("RECORDING CRAWL %d" % crawl)
            crawlman = CrawlManager(crawl, self.output_fp, self.db_fp)
            self.documents[crawl] = crawlman.main()

    def analyse_crawls(self, crawls):
        print("Creating analyser...")
        print("Crawls: ", crawls)
        print("Output fp: ", self.output_fp)
        analyser = ProvAnalyser(crawls, self.output_fp, self.db_fp)
        analyser.main()

    def db_connect(self):
        connection = lite.connect(self.db_fp)
        cursor = connection.cursor()
        print("Reading from: ", self.db_fp)
        return cursor


#
#
