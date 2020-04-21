from prov.model import *
import sqlite3 as lite
from os import path
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import json


class ProvAnalyser(): # TODO: Pie charts for cookies and bar charts for trackers?
    def __init__(self, crawls, output_fp, params):
        self.crawls = crawls
        self.output_fp = output_fp
        self.visits = {}
        self.params = params
        # for crawl in crawls: # TODO: Refactor so that it doesnt need to access the database.
        #     self.visits[crawl] = {site_visit[0]: None for site_visit in self.db_cursor.execute("select visit_id from site_visits where crawl_id=?", [str(crawl)])}

    def main(self):
        for crawl in sorted(os.listdir(self.output_fp)):
            if 'crawl' in crawl:
                crawl_fp = path.join(self.output_fp, crawl)
                crawl_id = crawl.split('crawl')[1]
                self.visits[crawl_id] = None
                for directory in os.listdir(crawl_fp):
                    if 'json' in directory:
                        json_fp = path.join(crawl_fp, directory)
                        visits = []
                        for visit in sorted(os.listdir(json_fp)):
                            visits.append(int(visit.split('visit')[1].split('.')[0]))
                            self.visits[int(crawl_id)] = {visit: None for visit in visits}

        # print("Analysis for crawls")
        for crawl in self.crawls:
            self.load_data(crawl)
            self.analyse_crawl(crawl)

    def load_data(self, crawl):
        visits_from_crawl = self.visits[crawl]
        json_fp = path.join(self.output_fp, "crawl%d" % crawl, "json")
        # print("\nFilepath: ", json_fp)
        # print("\n\nLoading crawl %d" % crawl)

        for file, visit in zip(os.listdir(json_fp), visits_from_crawl):
            with open(path.join(json_fp,path.normpath(file))) as js:
                visits_from_crawl[visit] = json.load(js)

    def analyse_crawl(self, crawl_id):
        crawl = self.visits[crawl_id]

        # date_time = self.db_cursor.execute("select start_time from crawl where crawl_id=?", [str(crawl_id)]).fetchone()[0]
        # date, time = date_time.split(" ")[0], date_time.split(" ")[1][:-3:]
        # print("\nAnalysing crawl %d on %s at %s" % (crawl_id, date, time))
        print("\nAnalysing crawl %d..." % crawl_id)
        urls = []
        for visit_js in self.visits[crawl_id].values():
            urls.append(visit_js['entity']['visit']['url'])
        # for site_url in self.db_cursor.execute("select site_url from site_visits where crawl_id=?", [str(crawl_id)]):
        #     urls.append(site_url[0])
        print("Made %d visits" % len(list(crawl.keys())))
        print("Visited sites: ", urls)

        for (visit_id, visit_js), site_url in zip(crawl.items(), urls):
            self.analyse_visit(visit_id, visit_js, site_url)

    def analyse_visit(self, visit_id, visit_js, site_url): # TODO: first time visiting?
        print("Analysing visit %d to %s " % (visit_id, site_url))
        hosts_cookies = self.retrieve_hosts_cookies(visit_js)
        if not hosts_cookies.keys():
            print("Visit had no third-party hosts!\n")
        else:
            cookies_num = 0
            for val in hosts_cookies.values():
                cookies_num += len(val)
            # TODO: Check if tracker was encountered in other visits
            print("Visit %d resulted in %d third-party trackers " % (visit_id, len(hosts_cookies.keys())))
            print("And a total %d third-party cookies " % cookies_num)
            print("Number of cookies for every tracker: ")
            most_cookies = 0
            most_tracker = None
            for tracker, cookies in hosts_cookies.items():
                print("%s – %d" % (tracker, len(cookies)))
                if len(cookies) > most_cookies:
                    most_tracker = tracker
                    most_cookies = len(cookies)
            print("Tracker with most cookies – %s with %d cookies" % (most_tracker, most_cookies))
        syncs = []
        for activity, params in visit_js['activity'].items():
            if 'syncCookies' in activity:
                syncs.append(params)
        if syncs: print("There have been %d instances of cookie syncing during this visit" % len(syncs))
        for sync in syncs:
            dsp = sync['DSP']
            dmp = sync['DMP']
            print("DSP – %s and DMP – %s" % (dsp, dmp))

    def retrieve_hosts_cookies(self, visit_js):
        hosts_cookies = {}
        # cookies = []
        try:
            for v in visit_js['hadMember'].values():
                if v['prov:collection'] == 'trackers':
                    hosts_cookies[v['prov:entity']] = []
            for v  in visit_js['wasAttributedTo'].values():
                if v['prov:agent'] in hosts_cookies.keys():
                    hosts_cookies[v['prov:agent']].append(v['prov:entity'])
        finally:
            return hosts_cookies


    # def cookie_stats(self, visit_id):
    #
    # def cookie_hosts(self):
    #
    # def full_analysis(self):
    #
    # def make_piechart(self):

    # def cookie_stats(self, visit_id, site_url=""):
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
    #
    #
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

