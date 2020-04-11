from prov.model import *
import prov.model as prov
import sqlite3 as lite
from os import path
import os
import matplotlib.pyplot as plt
from prov.dot import prov_to_dot
# from crawlmanager import CrawlManager
import matplotlib.image as mpimg
# from IPython.display import Image
# import python_main_function
import json

class ProvAnalyser():

    def __init__(self, crawls, output_fp, db_fp):
        self.crawls = crawls
        self.output_fp = output_fp
        self.db_fp = db_fp
        self.db_cursor = lite.connect(db_fp).cursor()
        # self.visits = {cr:[] for cr in self.crawls}
        self.visits = {}
        # for site_visit, crawl_id in self.db_cursor.execute("select visit_id and crawl_id from site_visits"):
        #     if site_visit not in self.visits[crawl_id]:
        #         self.visits[crawl_id].append({site_visit:None})
        for crawl in crawls:
            self.visits[crawl] = {site_visit[0]: None for site_visit in self.db_cursor.execute("select visit_id from site_visits where crawl_id=?", [str(crawl)])}
            # self.visits[crawl_id[0]] = site_visit[0]
        # self.documents = documents
        # self.crawls = crawls_to_analyse

    def main(self):
        # print("Analysis for crawls")
        for crawl in self.crawls:
            self.load_data(crawl)
            self.analyse_crawl(crawl)
        # print("Collected %d crawls" % len(self.visits.keys()))
        # print(list(self.visits[2].keys()))


    def load_data(self, crawl):
        visits_from_crawl = self.visits[crawl]
        json_fp = path.join(self.output_fp, "crawl%d" % crawl, "json")
        # print("\nFilepath: ", json_fp)
        print("\n\nLoading crawl %d" % crawl)

        for file, visit in zip(os.listdir(json_fp), visits_from_crawl):
            # print("\nLoading visit %d" % visit)
            # print("File: ", file)

            with open(path.join(json_fp,path.normpath(file))) as js:
                visits_from_crawl[visit] = json.load(js)
        # print(visits_from_crawl)

    def analyse_crawl(self, crawl_id):
        crawl = self.visits[crawl_id]
        # print(list(crawl.keys()))

        date_time = self.db_cursor.execute("select start_time from crawl where crawl_id=?", [str(crawl_id)]).fetchone()[0]
        date, time = date_time.split(" ")[0], date_time.split(" ")[1][:-3:]
        print("Analysing crawl %d on %s at %s" % (crawl_id, date, time))
        urls = []

        for site_url in self.db_cursor.execute("select site_url from site_visits where crawl_id=?", [str(crawl_id)]):
            urls.append(site_url[0])
        print("Made %d visits" % len(list(crawl.keys())))
        print("Visited sites: ", urls)

        for (visit_id, visit_js), site_url in zip(crawl.items(), urls):
            self.analyse_visit(visit_id, visit_js, site_url)



    def analyse_visit(self, visit_id, visit_js, site_url):
        print("Analysing visit %d to %s " % (visit_id, site_url))
        hosts = self.retrieve_hosts(visit_js)
        if not hosts:
            print("Visit had no third-party hosts!\n")
        else:
            print("Visit %d resulted in %d third-party hosts: " % (visit_id, len(hosts)))
            print(hosts, "\n")


    def retrieve_hosts(self, visit_js):
        hosts = []
        try:
            for k,v in visit_js['hadMember'].items():
                hosts.append(v['prov:entity'])
        finally:
            return hosts


    # def cookie_stats(self, visit_id):
    #
    # def cookie_hosts(self):
    #
    # def full_analysis(self):
    #
    # def make_piechart(self):


