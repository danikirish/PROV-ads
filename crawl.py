from OpenWPM.automation import CommandSequence, TaskManager, BrowserManager
import getopt, sys
import copy
import os
NUM_BROWSERS = 1
sites_fp = None
sites = []
fullargs = sys.argv
argslist = fullargs[1:]
options = "hs:d:"
dnt = False

try:
    arguments, values = getopt.getopt(argslist, options, ["sites=", "dnt="])
except getopt.error as err:
    print(str(err))
    sys.exit(2)

for argument, value in arguments:
    if argument == '-h':
        print ("prj.py -s <sites> -d <dnt>")
        sys.exit()
    if argument in ("-d", "--dnt"):
        print("VAL: ", value)
        if int(value) == 1:
            dnt = True
    elif argument in ("-s", "--sites"):
        sites = value
        if os.path.isfile(sites):
            with open(sites, 'r') as s:
                sites = s.readlines()
        else:
            sites = [sites]


if len(sites) == 0:
    sites = ['https://github.com/']

print("SITES: %s" % sites)
print("DNT: %s" % str(dnt))
manager_params, browser_params = TaskManager.load_default_params(NUM_BROWSERS)

manager_params["data_directory"] = os.path.join(os.getcwd(), "Results/Crawls")
manager_params["log_directory"] = os.path.join(os.getcwd(), "Results/Crawls")


for i in range(NUM_BROWSERS):
    browser_params[i]['donottrack'] = dnt
    browser_params[i]['http_instrument'] = True
    # Record cookie changes
    browser_params[i]['cookie_instrument'] = True
    # # Record Navigations
    browser_params[i]['navigation_instrument'] = True
    # # Record JS Web API calls
    # browser_params[i]['js_instrument'] = True
    # # Enable flash for all three browsers
    # browser_params[i]['disable_flash'] = True
    # # Record the callstack of all WebRequests made
    browser_params[i]['callstack_instrument'] = True
    # browser_params[0]['headless'] = True

manager = TaskManager.TaskManager(manager_params, browser_params)

for site in sites:
    command_sequence = CommandSequence.CommandSequence(site, reset=True)
    
    command_sequence.get(sleep=2, timeout=45)

    manager.execute_command_sequence(command_sequence, index='**')

manager.close()

