#!/usr/bin/env python


from prov.model import *
import prov.model as prov
import sqlite3 as lite
from os import path
import os
from crawlmanager import CrawlManager
from provanalyser import ProvAnalyser


# ProvManager class gives out commands and passes parameters to other classes
class ProvManager:
    def __init__(self, output_fp=path.join(os.getcwd(), "Crawls", "Results"), db_fp=path.join(os.getcwd(),"Crawls","crawl-data.sqlite")):
        self.db_fp = db_fp
        self.output_fp = output_fp
        self.cur = None  # Database cursor

    def main(self):
        self.cur = self.db_connect()
        recorded = False  # Indicates whether there were any crawls recorded so far
        crawls_queue = []  # Queue of crawls that need to be recorded
        for crawl in self.cur.execute("select crawl_id from crawl"):
            crawl_fp = path.join(self.output_fp, "crawl%d" % crawl[0])
            if not path.isdir(crawl_fp):  # Check if records for this crawl exist
                recorded = True
                crawls_queue.append(crawl[0])

        analyse_queue, params = self.record_crawls(crawls_queue)  # Create provenance for crawls
        if not recorded:
            print("No crawls to record")
        else:
            print("Finished recording")

        if analyse_queue:
            self.analyse_crawls(analyse_queue)  # Analyse provenance
        else:
            print("No crawls to analyse")


    def record_crawls(self, crawls):
        print("Writing to: ", self.output_fp)
        all_params = []
        recorded_crawls = []  # Crawls that provenance was recorded for
        for crawl in crawls:
            print("\nRECORDING CRAWL %d" % crawl)
            crawlman = CrawlManager(crawl, self.output_fp, self.db_fp)  # Create a CrawlManager object for every crawl
            returned = crawlman.main()
            if returned is not False:  # Check if was successfully recorded
                params = returned[1]  # Browser parameters
                all_params.append(params)
                recorded_crawls.append(crawl)
        return recorded_crawls, all_params  # Return the list of crawls recorded

    def analyse_crawls(self, crawls):
        print("\n\nCreating analyser...")
        print("Crawls: ", crawls)
        analyser = ProvAnalyser(crawls, self.output_fp)  # Create one ProvAnalyser object for all crawls
        analyser.main()
        print("Finished analysis.")

    def db_connect(self):
        connection = lite.connect(self.db_fp)
        cursor = connection.cursor()
        print("Reading data from: ", self.db_fp)
        return cursor
