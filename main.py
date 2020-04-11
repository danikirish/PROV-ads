from provmanager import ProvManager
# import os
# from subprocess import Popen, PIPE
# import sys

# venv = "/Users/Danik/Desktop/KCL/YEAR_3/PRJ/OpenWPM/venv/bin/activate"
# with open(venv) as f:
#     code = compile(f.read(), venv, 'exec')
#     exec(code, dict(__file__=venv))
# subprocess.Popen(["sudo", ".", "/Users/Danik/Desktop/KCL/YEAR_3/PRJ/OpenWPM/venv/bin/activate"])
# process = Popen(['source', '/Users/Danik/Desktop/KCL/YEAR_3/PRJ/OpenWPM/venv/bin/activate'], stdout=PIPE, stderr=PIPE)
# Popen(['sudo', '.', './OpenWPM/venv/bin/activate'])
# stdout, stderr = process.communicate()
# subprocess.call(["source", "/Users/Danik/Desktop/KCL/YEAR_3/PRJ/OpenWPM/venv/bin/activate"])
# subprocess.call(["source", "/OpenWPM/venv/bin/activate"])
# subprocess.run(["cd", "/Users/Danik/Desktop/KCL/YEAR_3/PRJ/Notebooks"])
# subprocess.run("source", cwd="OpenWPM/venv/bin/")
# sys.path.append("/Users/Danik/Desktop/KCL/YEAR_3/PRJ/OpenWPM/")
# print("STARTING CRAWL...")
# import prj
# os.system("deactivate")



print("LAUNCHING...")
provman = ProvManager()
# provman.main()
provman.analyse_crawls([8,9])