from prov.model import ProvDocument
import prov.model as prov
import sqlite3 as lite
from os import path
import os
from prov.dot import prov_to_dot

# This class handles creation of provenance for a given crawl
class CrawlManager:
    def __init__(self, crawl_id, output_fp, db_fp):
        self.crawl_id = crawl_id
        self.output_fp = path.join(output_fp, "crawl%d" % crawl_id)
        self.documents = {}
        self.db_fp = db_fp
        self.db_cursor = lite.connect(db_fp).cursor()
        self.params = self.extract_params()
        self.google_sync_id = 'google_gid='  # Google's parameter for cookie matching
        self.google_ssp = 'cm.g.doubleclick'  # Google's SSP domain
        self.google_pixel_id = 'google_push='  # Google's parameter for pixel matching

    def main(self):
        self.create_prov()
        self.record_prov()
        if len(self.documents.values()) == 0:  # If no crawls were successful
            return False
        else:
            self.write_prov()
            return self.documents, self.params

    # Get parameters for this crawl in a dictionary
    def extract_params(self):
        params_str = self.db_cursor.execute("select browser_params from crawl where crawl_id=?", [str(self.crawl_id)]).fetchone()[0]
        params = eval(params_str, {'true': True, 'false': False, 'null': None})
        return params

    def create_prov(self):
        visits = []
        for visit_id in self.db_cursor.execute("select visit_id from site_visits where crawl_id=?", [str(self.crawl_id)]):
            visits.append(visit_id[0])

        for visit_id in visits:
            try:
                self.db_cursor.execute("select command_status from crawl_history where visit_id=?", [str(visit_id)])
                if self.db_cursor.fetchone()[0] == 'error':  # Check if visit had an error
                    print('Error in visit %s' % visit_id)
                    continue
                document = ProvDocument()
                document.set_default_namespace('http://prj.com')
                self.documents[visit_id] = document  # Save a blank document for this visit
            except:
                pass

    # Get third-party cookies
    def retrieve_tp_hosts(self, visit_id, site_url):
        hosts_ids = []
        for host, cookie_id, record_type in self.db_cursor.execute("select host, id, record_type from javascript_cookies where visit_id=?", [str(visit_id)]):
            if record_type == 'deleted':  # Ignore if cookie was deleted
                continue
            split = host.split('.')
            if 'www' in split: split.remove('www')
            host = split[1]
            for el in split[2:]:
                host += "." + el
            if site_url.find(host) == -1:  # If the host and site domain are not the same
                hosts_ids.append((host, cookie_id))
        return hosts_ids

    # Find instances of cookie syncing
    def cookie_sync(self):
        redirects = []
        cookie_synced = {}  # Dictionary of cookie sync instances {visit_id: (old_url, new_url)}
        for old_url, new_url, visit_id in self.db_cursor.execute("select old_request_url, new_request_url, visit_id from http_redirects where crawl_id=?", [str(self.crawl_id)]):
            redirects.append((int(visit_id), old_url, new_url))

        for redirect in redirects:
            if self.google_sync_id in redirect[2] and self.google_ssp in redirect[1].split('/')[2]:  # Conditions for cookie syncing
                if redirect[0] not in cookie_synced.keys():  # If first instance for this visit
                    cookie_synced[redirect[0]] = []
                cookie_synced[redirect[0]].append((redirect[1], redirect[2]))
            elif self.google_pixel_id in redirect[2] and self.google_ssp in redirect[2].split('/')[2]:
                if redirect[0] not in cookie_synced.keys():
                    cookie_synced[redirect[0]] = []
                cookie_synced[redirect[0]].append((redirect[2], redirect[1]))
        return cookie_synced

    # Record provenance
    def record_prov(self): # TODO: Pixel matching.
        cookies_syncs = self.cookie_sync()
        for visit, doc in self.documents.items():
            self.db_cursor.execute("select site_url from site_visits where visit_id=?", [str(visit)])
            site_url = self.db_cursor.fetchone()[0].split('://')[1]
            publisher = site_url.split('/')[0]
            synced = False
            if visit in cookies_syncs.keys():  # Check for cookie syncing in this visit
                if cookies_syncs[visit]:
                    synced = True

            # TYPES
            # Agents
            doc.agent('OpenWPM', {'prov:type': 'prov:SoftwareAgent'})
            doc.agent('user')
            doc.agent(publisher)

            # Entities
            doc.entity('visit', {'id': visit, 'url': site_url})
            doc.entity(site_url)
            doc.entity('crawl', {'id': self.crawl_id,
                                 'DNT': self.params['donottrack']})
            doc.entity(self.params['browser'].capitalize())

            # Activities
            doc.activity('performCrawl')
            doc.activity('setCookies')
            doc.activity('visitSite')

            doc.collection('trackers')
            doc.collection('cookies')

            # RELATIONS
            # Delegations
            doc.actedOnBehalfOf('OpenWPM', 'user')

            # Associations
            doc.wasAssociatedWith('performCrawl', 'OpenWPM')

            # Generations
            doc.wasGeneratedBy('cookies', 'setCookies')
            doc.wasGeneratedBy('visit', 'visitSite')
            doc.wasGeneratedBy('crawl', 'performCrawl')

            # Derivations
            doc.wasDerivedFrom('visit', site_url, activity='visitSite')

            doc.wasStartedBy('visitSite', 'crawl', starter='performCrawl')

            # Attributions
            doc.wasAttributedTo(site_url, 'publisher')

            # Usages
            doc.used('visitSite', site_url)
            doc.used('setCookies', site_url)
            doc.used('performCrawl', self.params['browser'].capitalize())

            # Third-party cookies
            tp_hosts_cookies = self.retrieve_tp_hosts(visit, site_url)
            added_hosts = set()
            for host, cookie in tp_hosts_cookies:
                if host not in added_hosts:
                    doc.agent(host)
                    doc.hadMember('trackers', host)
                    doc.wasAssociatedWith('setCookies', host)
                    added_hosts.add(host)
                doc.entity(str(cookie))
                doc.wasAttributedTo(str(cookie), host)
                doc.hadMember('cookies', str(cookie))

            # Cookie syncing
            if synced:
                sync_counter = 1
                for sync in cookies_syncs[visit]:
                    sync_name = 'syncCookies%d' % sync_counter
                    ssp, dsp = sync[0].split('/')[2], sync[1].split('/')[2]
                    doc.activity(sync_name, None, None, {'DSP': dsp, 'SSP': ssp})
                    doc.wasAssociatedWith(sync_name, ssp)
                    doc.wasAssociatedWith(sync_name, dsp)
                    sync_counter += 1

    # Write provenance to files
    def write_prov(self):
        json_fp = path.join(self.output_fp, "json")
        png_fp = path.join(self.output_fp, "png")
        if not path.exists(self.output_fp):  # Check for records of this crawl
            os.makedirs(self.output_fp)
            os.mkdir(json_fp)
            os.mkdir(png_fp)
        for visit, document in self.documents.items():
            print("writing visit%d" % visit)
            dot = prov_to_dot(document)
            dot.write_png(path.join(png_fp, 'visit%d.png' % visit))
            document.serialize(path.join(json_fp, 'visit%d.json' % visit), indent=4)
