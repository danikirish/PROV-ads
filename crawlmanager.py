from prov.model import ProvDocument
import prov.model as prov
import sqlite3 as lite
from os import path
import os
import seaborn as sns
import matplotlib.pyplot as plt
from prov.dot import prov_to_dot
import matplotlib.image as mpimg


class CrawlManager():
    def __init__(self, crawl_id, db_cursor, output_fp, db_fp):
       self.crawl_id = crawl_id
       self.output_fp = path.join(output_fp, "crawl%d" % crawl_id)
       self.documents = {}
       self.db_fp = db_fp
       self.db_cursor = lite.connect(db_fp).cursor()


    def main(self):
        self.create_prov()
        self.record_prov()
        self.write_prov()
        return self.documents


    def create_prov(self):
        for visit_id in self.db_cursor.execute("select visit_id from site_visits where crawl_id=?", [str(self.crawl_id)]):
            document = ProvDocument()
            document.set_default_namespace('http://danik.com')
            self.documents[visit_id[0]] = document

    def retrieve_tp_hosts(self, visit_id, site_url):
        hosts = []
        for h in self.db_cursor.execute("select host from javascript_cookies where visit_id=?", [str(visit_id)]):
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
            doc.entity('visit%d' % visit)
            self.db_cursor.execute("select site_url from site_visits where visit_id=?", [str(visit)])
            site_url = self.db_cursor.fetchone()[0][7:]
            doc.entity(site_url)
            doc.entity('syncing_algorithm')
            doc.agent('tracker1')
            doc.agent('tracker2')
            doc.activity('syncCookies')
            doc.activity('collectData')
            tp_cookies = doc.collection('cookies%d'%visit)
            #     tp_cookies.set_default_namespace('http://danik.com/bundles')
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
            # for h in self.db_cursor.execute("select host from javascript_cookies where visit_id=?", str(visit)):
            #     split = h[0].split('.')
            #     if 'www' in split: split.remove('www')
            #     host = split[1]
            #     for el in split[2:]:
            #         host += "." + el
            #     if site_url.find(host) == -1:
            #         tp_hosts.append(h[0])

            tp_hosts = self.retrieve_tp_hosts(visit, site_url)
            # print(tp_hosts)

            added_hosts = set()
            for tp in tp_hosts:
                if tp not in added_hosts:
                    e = doc.entity(tp)
                    doc.hadMember(tp_cookies, e)
                    added_hosts.add(tp)
            # self.all_tp_hosts[visit] = tp_hosts



    def write_prov(self):
        if not path.exists(self.output_fp):
            os.mkdir(self.output_fp)

        print("Writing to: ", self.output_fp, "\n")
        for visit, document in self.documents.items():
            # crawl_fp = path.join(self.output_fp, "visit%" % visit)
            json_fp = path.join(self.output_fp, "json")
            png_fp = path.join(self.output_fp, "png")
            os.mkdir(json_fp)
            os.mkdir(png_fp)
            dot = prov_to_dot(document)
            dot.write_png(path.join(png_fp, 'visit%d.png'%visit))
            document.serialize(path.join(json_fp, 'visit%d.json'%visit))
            # self.tester = path.join(self.output_fp,'visit%d.png' %visit)
            # file = open(path.join(self.output_fp, 'visit%d.png' % visit), 'w+')
            # file.write(dot)
            # file.close()
            print("writing visit%d.png" % visit)

