#!/usr/bin/env python
# coding: utf-8

# In[191]:


from prov.model import *
import prov.model as prov
from http import cookies
import sqlite3 as lite
from os import path
import seaborn as sns
import matplotlib.pyplot as plt
from prov.dot import prov_to_dot
# from IPython.display import Image
# import python_main_function 

# if __main__ == "main":
#     provman = ProvManager()
#     provman.main()


class ProvManager():
    def __init__(self, output_fp=path.join(os.getcwd(), "results/"), db_fp="/Users/Danik/Desktop/KCL/YEAR_3/PRJ/Crawls/crawl-data.sqlite"):
        self.db_fp = db_fp
        self.output_fp = output_fp
        self.documents = {}
        self.all_tp_hosts = {1: [],
                           2: [],
                           3: [],
                           4: []}
        self.cur = None
        if not path.exists(self.output_fp):
            os.mkdir(self.output_fp)
            
        
    def main(self):
        self.db_connect()
        self.create_prov()
        self.record_prov()
        self.write_prov()
        self.all_cookie_stats()
    
    def db_connect(self):
        connection = lite.connect(self.db_fp)
        self.cur = connection.cursor()
    
    def create_prov(self):
        for visit_id in self.cur.execute("select visit_id from site_visits"):
            document = ProvDocument()
            document.set_default_namespace('http://danik.com')
            self.documents[visit_id[0]] = document
#         return document
    
    def retrieve_tp_hosts(self,visit_id, site_url):
        hosts = []
        for h in self.cur.execute("select host from javascript_cookies where visit_id=?", str(visit_id)):
            split = h[0].split('.')
            if 'www' in split: split.remove('www')
            host = split[1]
            for el in split[2:]:
                host += "." + el
            if site_url.find(host) == -1:
                hosts.append(h[0])
        return hosts
    
    def record_prov(self):        
        for visit, doc in self.documents.items():
            tp_hosts = []
            doc.agent('OpenWPM', {'prov:type': 'prov:SoftwareAgent'})
            doc.agent('user')
            doc.activity('performCrawl')
            doc.entity('visit%d'%visit)
            self.cur.execute("select site_url from site_visits where visit_id=?",str(visit))
            site_url = self.cur.fetchone()[0][7:]
            doc.entity(site_url)
            doc.entity('syncing_algorithm')
            doc.agent('tracker1')
            doc.agent('tracker2')
            doc.activity('syncCookies')
            doc.activity('collectData')

            tp_cookies = doc.collection('cookies%d'%visit)
        #     tp_cookies.set_default_namespace('http://danik.com/bundles')
#             sync_algorithm = doc.bundle('syncing_algorithm')
        #     sync_algorithm.set_default_namespace('http://danik.com/syncing')


            doc.actedOnBehalfOf('OpenWPM', 'user')
            doc.wasAssociatedWith('performCrawl', 'OpenWPM')
            doc.wasGeneratedBy('visit%d'%visit, 'performCrawl')
            doc.wasDerivedFrom('visit%d'%visit, site_url, 'performCrawl')
            doc.wasAttributedTo(site_url, 'tracker1')
            doc.wasAssociatedWith('collectData', 'tracker1')
            doc.wasGeneratedBy('cookies%d'%visit, 'collectData')
            doc.actedOnBehalfOf('tracker2', 'tracker1', 'syncCookies')
            doc.used('syncCookies', 'cookies%d'%visit)
            doc.used('syncCookies', 'syncing_algorithm')
            doc.used('performCrawl', site_url)
            doc.used('collectData', site_url)

#             for h in cur.execute("select host from javascript_cookies where visit_id=?", str(visit)):
#                 split = h[0].split('.')
#                 if 'www' in split: split.remove('www')
#                 host = split[1]
#                 for el in split[2:]:
#                     host += "." + el
#                 if site_url.find(host) == -1:
#                     tp_hosts.append(h[0])
            tp_hosts = self.retrieve_tp_hosts(visit, site_url)
#             print(tp_hosts)
        #         hosts.append(host)
        #         if host in trackers:
        #             hosts.append(host)
            for tp in tp_hosts:
                e = doc.entity(tp)
                doc.hadMember(tp_cookies, e)
            self.all_tp_hosts[visit] = tp_hosts
        print("finished record:")
        print(self.all_tp_hosts[2])
            
    def write_prov(self):
        for visit, document in self.documents.items():
            dot = prov_to_dot(document)
            dot.write_png(path.join(self.output_fp,'visit%d.png' %visit))
#             file = open(path.join(self.output_fp,'visit%d.png' %visit), 'w+')
#             file.write(dot)
#             file.close()
            print("writing")
#             dot.write_png('visit%d.png' %visit)

    def cookie_stats(self, visit_id, site_url = ""):
        tp_cookies = self.all_tp_hosts[visit_id]
        self.cur.execute("select count(id) from javascript_cookies where visit_id=?", str(visit_id))
        cookies_num = self.cur.fetchone()[0]
        print("This visit resulted in %d cookies being recorded on your browser." % cookies_num)
        if len(tp_cookies) == 0:
            print("None of which are 3rd party")
        else:
            print("Of which %d are 3rd party."%len(tp_cookies))
            print("List of 3rd party trackers: ")
            print(set(tp_cookies))
            self.cookie_pie(cookies_num, len(tp_cookies), site_url)
            
    def all_cookie_stats(self,):
        for vid, cs in self.all_tp_hosts.items():
            self.cur.execute("select site_url from site_visits where visit_id=?",str(vid)) #TODO: Refactor this
            site_url = self.cur.fetchone()[0][7:]
            print("\nVisit %d to %s" % (vid, site_url), end='')
            self.cookie_stats(vid, site_url = site_url)
        input("Press enter to finish...")
            
    def cookie_pie(self, num_total, num_tp, site_url=""):
        color_palette_list = ['#009ACD', '#ADD8E6', '#63D1F4', '#0EBFE9', 
                              '#C1F0F6', '#0099CC']
        labels = ['1st Party', '3rd Party']
        plt.rcParams['font.sans-serif'] = 'Arial'
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['text.color'] = '#e8001b'
        plt.rcParams['axes.labelcolor']= '#e8001b'
        plt.rcParams['xtick.color'] = '#e8001b'
        plt.rcParams['ytick.color'] = '#e8001b'
        plt.rcParams['font.size']=12
        values = [num_total -num_tp, num_tp]
        explode = (0.1, 0)

        fig, ax = plt.subplots()
        ax.pie(values, labels=labels, explode=explode, colors=color_palette_list[0:2], autopct='%1.0f%%', shadow=False, startangle=90, pctdistance=0.8, labeldistance=1.1)
        ax.axis('equal')
        ax.set_title('Proportion of 3rd party cookies from %s\nTotal number of cookies: %d' %(site_url, num_total))
        ax.legend(frameon=False, bbox_to_anchor=(1.5, 0.8))
        fig.show()

