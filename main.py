from provmanager import ProvManager
# import os
import subprocess
import sys
subprocess.run("pwd")
# subprocess.call(["source", "/Users/Danik/Desktop/KCL/YEAR_3/PRJ/OpenWPM/venv/bin/activate"])
# subprocess.call(["source", "/OpenWPM/venv/bin/activate"])
# subprocess.run(["cd", "/Users/Danik/Desktop/KCL/YEAR_3/PRJ/Notebooks"])
subprocess.run("source", cwd="OpenWPM/venv/bin/")
# sys.path.append("/Users/Danik/Desktop/KCL/YEAR_3/PRJ/OpenWPM/")
# print("STARTING CRAWL...")
# import prj
# os.system("deactivate")



# print("STARTING ANALYSIS...")
# provman = ProvManager()
# provman.main()