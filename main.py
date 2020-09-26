#main
import random, json, time, re, requests, threading
from datetime import datetime
from colorama import init
from termcolor import colored
from dsm import dsm, dsm_monitor

#for windows colour output
init()

#format output text
def output(text,name, colour):
    now=datetime.now().strftime('%H:%M:%S:%f')
    print(colored("["+str(now)+"] ["+name+"] "+text,colour))
#dsm eshop flow
def dsm_go(clss, delay):
    while True:
        if clss.atc(url, delay):
            break
        else:
            time.sleep(2)
    while True:
        formkey=clss.shipping()
        if len(str(formkey))==16:
            break
        else:
            time.sleep(2)
    clss.pay(formkey)

print(colored("   ________                                ____        __ \n  / ____/ /___ _________  ____  __________/ __ )____  / /_\n / /   / / __ `/ ___/ _ \/ __ \/ ___/ ___/ __  / __ \/ __/\n/ /___/ / /_/ / /  /  __/ / / / /__(__  ) /_/ / /_/ / /_  \n\____/_/\__,_/_/   \___/_/ /_/\___/____/_____/\____/\__/  \n\n","blue"))
option=str(input("1 - DSML E-SHOP\n2 - DSMNY E-SHOP\nOption: "))

if option=="1" or option=="2":
    if option=="1":
        sitereg=""
    elif option=="2":
        sitereg="/us"
    else:
        sitereg=""
    with open("dsm/proxies.txt","r") as r:
        proxies=r.read().splitlines()
    proxies.append("None")
    with open("dsm/dsm_accts.txt","r") as r:
        accounts=r.read().splitlines()
    with open("data/profiles.json","r") as r:
        profiles=json.loads(r.read())["profiles"]
    with open("data/settings.json","r") as r:
        settings=json.loads(r.read())
    with open("dsm/tasks.csv","r") as r:
        tasks_wanted=[]
        longtasks=r.read().splitlines()
        longtasks.pop(0)
        for i in longtasks:
            params=i.split(",")
            tasks_wanted.append({"size":params[0],"proxy":params[1],"account_num":params[2],"profile_name":params[3]})
    tasks=[]
    for i in tasks_wanted:
        #try:
        profile="t"
        for j in profiles:
            if str(j["profileName"]) == str(i["profile_name"]):
                profile=dict(j)
        if profile=="t":
            raise
        tasks.append(dsm({**{"account":accounts[int(i["account_num"])-1],"proxy":i["proxy"],"webhook":settings["webhook"],"anticap_key":settings["anticap"],"task":"Task "+str(len(tasks)+1),"size":i["size"]},**profile}, sitereg))
        #except:
            #output("Profile error: "+str(i["profile_name"]),"Task "+str(len(tasks)+1),"red")
    threads=[]
    for i in tasks:
        x=threading.Thread(target=i.login, args=())
        x.start()
        threads.append(x)
        time.sleep(0.01)
    for i in threads:
        i.join()
    delay=input("Enter to start: ")
    url=dsm_monitor(proxies)
    threads=[]
    stagger_delay='%.2f'%(delay/len(tasks))
    for i in tasks:
        x = threading.Thread(target=dsm_go, args=(i,delay))
        x.start()
        threads.append(x)
        time.sleep(float(stagger_delay))
    for i in threads:
        i.join()
    output("Finished", "Main","green")
    time.sleep(1000)
else:
    output("Incorrect option","Main","red")
    time.sleep(5)