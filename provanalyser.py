from prov.model import *
from os import path
import os
import json


# This class analyses the provenance for every supplied crawl
class ProvAnalyser:
    def __init__(self, crawls, output_fp):
        self.crawls = crawls
        self.output_fp = output_fp
        self.visits = {}

    def main(self):
        # Iterate through every crawl's directory and make a list of visits for each crawl.
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

        # Perform analysis for every crawl in queue
        for crawl in self.crawls:
            self.load_data(crawl)
            self.analyse_crawl(crawl)

    # Load JSON data into the visits dictionary
    def load_data(self, crawl):
        visits_from_crawl = self.visits[crawl]
        json_fp = path.join(self.output_fp, "crawl%d" % crawl, "json")

        for file, visit in zip(os.listdir(json_fp), visits_from_crawl):
            with open(path.join(json_fp,path.normpath(file))) as js:
                visits_from_crawl[visit] = json.load(js)

    # Analyse a single crawl
    def analyse_crawl(self, crawl_id):
        crawl = self.visits[crawl_id]

        print("\nAnalysing crawl %d..." % crawl_id)
        urls = []
        for visit_js in self.visits[crawl_id].values():
            urls.append(visit_js['entity']['visit']['url'])
        print("Made %d visits" % len(list(crawl.keys())))
        print("Visited sites: ", urls)

        for (visit_id, visit_js), site_url in zip(crawl.items(), urls):
            self.analyse_visit(visit_id, visit_js, site_url)

    # Analyse a single visit
    def analyse_visit(self, visit_id, visit_js, site_url):
        print("\nVISIT %d" % visit_id)
        print("URL: %s" % site_url)
        hosts_cookies = self.retrieve_hosts_cookies(visit_js)
        dnt = visit_js['entity']['crawl']['DNT']
        if not hosts_cookies.keys():
            print("Visit had no third-party hosts!")
        else:
            cookies_num = 0
            for val in hosts_cookies.values():
                cookies_num += len(val)

            print("Visit %d resulted in %d third-party trackers " % (visit_id, len(hosts_cookies.keys())))
            if dnt: print("Trackers did not respect the DNT:1 signal")
            print("And a total %d third-party cookies " % cookies_num)
            print("Number of cookies for every tracker: ")
            # Find the tracker with most number of cookies
            most_cookies = 0
            most_tracker = None
            for tracker, cookies in hosts_cookies.items():
                print("%s – %d" % (tracker, len(cookies)))
                if len(cookies) > most_cookies:
                    most_tracker = tracker
                    most_cookies = len(cookies)
            print("Tracker with most cookies – %s with %d cookies" % (most_tracker, most_cookies))

        # Find cookie syncing instances
        syncs = []
        for activity, params in visit_js['activity'].items():
            if 'syncCookies' in activity:
                syncs.append(params)
        if syncs: print("There have been %d instances of cookie syncing during this visit" % len(syncs))
        for sync in syncs:
            dsp = sync['DSP']
            ssp = sync['SSP']
            print("DSP – %s and SSP – %s" % (dsp, ssp))

    # Get the cookies and corresponding trackers
    def retrieve_hosts_cookies(self, visit_js):
        hosts_cookies = {}
        try:
            for v in visit_js['hadMember'].values():
                if v['prov:collection'] == 'trackers':
                    hosts_cookies[v['prov:entity']] = []
            for v in visit_js['wasAttributedTo'].values():
                if v['prov:agent'] in hosts_cookies.keys():
                    hosts_cookies[v['prov:agent']].append(v['prov:entity'])
        finally:
            return hosts_cookies
