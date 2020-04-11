#!/usr/bin/env python


from prov.model import *
import prov.model as prov
import sqlite3 as lite
from os import path
import os
import matplotlib.pyplot as plt
from prov.dot import prov_to_dot
import matplotlib.image as mpimg
# from IPython.display import Image
# import python_main_function

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
#     def cookie_stats(self, visit_id, site_url=""):
#         tp_cookies = self.all_tp_hosts[visit_id]
#         self.cur.execute("select count(id) from javascript_cookies where visit_id=?", [str(visit_id)])
#         cookies_num = self.cur.fetchone()[0]
#         print("\nVisit to %s (id: %d) resulted in %d cookies being recorded on your browser." % (site_url, visit_id, cookies_num))
#         if len(tp_cookies) == 0:
#             print("None of which are 3rd party")
#         else:
#             print("Of which %d are 3rd party."%len(tp_cookies))
#             print("List of 3rd party trackers: ")
#             print(set(tp_cookies), "\n")
#             # self.cookie_pie(cookies_num, len(tp_cookies), site_url)
#         return cookies_num, len(tp_cookies)
            
    # def all_cookie_stats(self, crawl_id):
    #     cookie_nums = []
    #     tp_cookies_len = []
    #     site_urls = []
    #     # print(self.all_tp_hosts)
    #     for vid, cs in self.all_tp_hosts.items():
    #         # print("VISIT %d" %vid)
    #         self.cur.execute("select site_url from site_visits where visit_id=?", [str(vid)]) #TODO: Refactor this
    #         site_url = self.cur.fetchone()[0][7:]
    #         # print("GOT %s"%site_url)
    #         # print("\nVisit %d to %s" % (vid, site_url), end='')
    #         cnum, tplen = self.cookie_stats(vid, site_url=site_url)
    #         cookie_nums.append(cnum)
    #         tp_cookies_len.append(tplen)
    #         site_urls.append(site_url)
    #     self.cookie_pie(cookie_nums, tplen, site_urls)
    #
    #     input("Press enter to finish...")


    # def cookie_pie(self, num_total, num_tp, site_urls):
    #     for ind in range(len(site_urls)):
    #
    #         color_palette_list = ['#009ACD', '#ADD8E6', '#63D1F4', '#0EBFE9',
    #                               '#C1F0F6', '#0099CC']
    #         labels = ['1st Party', '3rd Party']
    #         plt.rcParams['font.sans-serif'] = 'Arial'
    #         plt.rcParams['font.family'] = 'sans-serif'
    #         plt.rcParams['text.color'] = '#e8001b'
    #         plt.rcParams['axes.labelcolor']= '#e8001b'
    #         plt.rcParams['xtick.color'] = '#e8001b'
    #         plt.rcParams['ytick.color'] = '#e8001b'
    #         plt.rcParams['font.size']=12
    #         values = [len(num_total) - num_tp, num_tp]
    #         explode = (0.1, 0)
    #
    #     fig, ax = plt.subplots()
    #     ax.pie(values, labels=labels, explode=explode, colors=color_palette_list[0:2], autopct='%1.0f%%', shadow=False, startangle=90, pctdistance=0.8, labeldistance=1.1)
    #     ax.axis('equal')
    #     ax.set_title('Proportion of 3rd party cookies from %s\nTotal number of cookies: %d' %(site_urls[ind], len(num_total)))
    #     ax.legend(frameon=False, bbox_to_anchor=(1.5, 0.8))
    #     fig.show()


#
# class Index:
#     ind = 0
#
#     def next(self, event):
#         self.ind += 1
#         i = self.ind % len(freqs)
#         ydata = np.sin(2*np.pi*freqs[i]*t)
#         l.set_ydata(ydata)
#         plt.draw()
#
#     def prev(self, event):
#         self.ind -= 1
#         i = self.ind % len(freqs)
#         ydata = np.sin(2*np.pi*freqs[i]*t)
#         l.set_ydata(ydata)
#         plt.draw()
