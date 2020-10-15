#dsm_script
import json, requests, json, time, io, datetime, random,re, asyncio
from datetime import datetime, timezone
from colorama import init
from termcolor import colored
from python_anticaptcha import AnticaptchaClient, NoCaptchaTaskProxylessTask
# from pyppeteer import launch
# from pyppeteer_stealth import stealth

init()

headers={
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "referer": "https://london.doverstreetmarket.com/new-items",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "WhatsApp/2.19.360 A"
}
def proxy_format(proxy):
    try:
        if proxy[len(proxy)-1]=="\n":
            proxy= proxy[0:len(proxy)-1]
        try:
            proxylist=proxy.split(":")
            if len(proxylist)==2:
                proxy=proxy
            elif len(proxylist)==4:
                proxy=str(proxylist[2])+":"+str(proxylist[3])+"@"+str(proxylist[0])+":"+str(proxylist[1])
            else:
                return False
            return{
                    "http":"http://"+proxy,
                    "https":"https://"+proxy,
                    "ftp":"ftp://"+proxy
                }
        except:
            return False
    except:
        return False

def find_code(text, target, length):
    resplist=str(text).split(target)
    return(resplist[1][0:length])

# async def headless_checkout(clss,url,cardnum,month,year,cvv):
#     #try:
#     browser = await launch({'headless': False })
#     page = await browser.newPage()#creates page
#     await fucking.bypass_detections(page)#Stealths the page
#     await page.goto(url)
#     await page.keyboard.press("Tab")
#     await page.keyboard.press("Tab")
#     await page.keyboard.press("Tab")
#     await page.keyboard.type(cardnum)
#     await page.keyboard.press("Tab")
#     await page.keyboard.press(str(month)+str(year)[2]+str(year)[3])
#     await page.keyboard.press("Tab")
#     await page.keyboard.type(cvv)
#     await page.click("#pay-by-link > div:nth-child(2) > div.pay-by-link__main > div.pay-by-link__checkout > div > div > ul > li > div.adyen-checkout__payment-method__details._2_jFPDCxgbayWBQMKR2rMi > div > div > button")
#     time.sleep(100)
#     driver.close()
#     send_webhook(clss.cart,url,clss,False)
    #except:
    #    output("Failed manual checkout "+url,clss.name,"red")
    




def output(text,name, colour):
    now=datetime.now().strftime('%H:%M:%S:%f')
    print(colored("["+str(now)+"] ["+name+"] "+str(text),colour))


def dsm_monitor(proxies):
    while True:
        try:
            with open("dsm/product.txt","r") as r:
                product = r.read().splitlines()
            proxy=proxy_format(random.choice(proxies))
            res=requests.get(product[0], headers=headers, proxies=proxy)
            try:
                output("Searching for product","Monitor","white")
                longlist=res.text.split("image-repeat-1")
                longlist.pop(0)
                worked=False
                kwlist=str(product[1]).split("/")
                for i in longlist:
                    for k in kwlist:
                        words=k.split(",")
                        good=len(words)
                        total=0
                        for t in words:
                            if re.search(t, i, re.IGNORECASE):
                                total+=1
                            if total==good:
                                worked=True
                                chunk=i
                                break
                if worked:
                    url=find_code(chunk, "href=\"", 120).split("\"")[0]
                    output("Found product "+url,"Monitor","yellow")
                    return url
                else:
                    time.sleep(float(product[2]))
            except:
                time.sleep(float(product[2]))
        except:
            output("Error searching for product/Can't find (or error in product.txt)","Monitor","red")

class dsm:
    def __str__(self):
        return self.name
    def __init__(self, data, site):
        self.data=data
        self.sitereg = site
        self.email=data["account"].split(":")[0]
        self.password=data["account"].split(":")[1]
        self.proxy=proxy_format(data["proxy"])
        self.anticap_key=data["anticap_key"]
        self.name=data["task"]
        self.cart=None
        self.webhook=data["webhook"]
        self.sesh=requests.session()
        self.fname=data["firstName"]
        self.lname=data["lastName"]
        self.address1=data["address1"]
        self.address2=data["address2"]
        self.zipCode=data["zipCode"]
        self.city=data["city"]
        self.province=data["province"]
        self.mobile=data["phoneNumber"]
        self.cardName=data["cardName"]
        self.size=data["size"]
    def login(self):
        for i in range(3):
            try:
                output("Logging in",self.name,"magenta")
                #get login info
                res=self.sesh.get("https://shop.doverstreetmarket.com"+self.sitereg+"/customer/account/login", headers=headers, proxies=self.proxy)
                sitekey=find_code(res.text, "data-sitekey=\"", 40)
                formkey=find_code(res.text, "\"form_key\" type=\"hidden\" value=\"", 16)
                #get captcha
                client = AnticaptchaClient(self.anticap_key)
                task = NoCaptchaTaskProxylessTask("https://shop.doverstreetmarket.com"+self.sitereg+"/customer/account/login", sitekey)
                job = client.createTask(task)
                job.join()
                captcha_response=job.get_solution_response()
                #login data
                data={
                    "form_key": formkey,
                    "login[username]": self.email,
                    "login[password]": self.password,
                    "g-recaptcha-response":captcha_response
                }
                res=self.sesh.post("https://shop.doverstreetmarket.com"+self.sitereg+"/customer/account/loginPost/",data=data, headers=headers, proxies=self.proxy, allow_redirects=False)
                if str(res.status_code) in ["200","302"]:
                    res=self.sesh.post("https://shop.doverstreetmarket.com"+self.sitereg+"/checkout/cart/",data=data, headers=headers, proxies=self.proxy)
                    try:
                        if "product-cart-info" in res.text:
                            splt=res.text.split("product-cart-info")
                            splt.pop(0)
                            for i in splt:
                                url=find_code(i,"customFormSubmit(\'", 150).split("\"")[0]
                                form=find_code(i,"quot;:&quot;",16)
                                self.sesh.post(url,headers=headers,data={"form_key":form})
                    except:
                        None
                    output("Logged in",self.name,"magenta")
                    return True
                else:
                    output("Failed log in,retrying",self.name,"red")
            except:
                output("Failed log in, Retrying",self.name,"red")
        output("Failed log in",self.name,"red")
        return False
    def atc(self, url, delay):
        while True:
            try:
                self.url=url
                self.start=datetime.now()
                res=self.sesh.get(url, headers=headers, proxies=self.proxy)
                output(str(res.status_code),self.name,"cyan")
                self.cart=res.text
                longposturl=find_code(res.text, "<form action=\"", 250)
                posturl=longposturl.split("\"")[0]
                pid=str(posturl.split("/")[9])
                try:
                    longsizelist=res.text.split("<input type=\"hidden\" name=\"sa")
                    longsizelist.pop(0)
                    longsizelist=[x[0:26] for x in longsizelist]
                    sizelist=[x[0:13] for x in longsizelist]
                    vallist=[x[22:25] for x in longsizelist]
                    data={
                        "product": pid,
                        "related_product": "",
                        "is_multi_order": "1",
                    }
                    for i in range(len(sizelist)):
                        data["qtys"+sizelist[i][0:8]]="0"
                        data["sa"+sizelist[i]]=vallist[i]
                    data["qtys"+sizelist[int(self.size)-1][0:8]]="1"
                except:
                    data={
                        "product": pid,
                        "related_product": "",
                        "qty": "1"
                    }
                data["product"] = "275392"
                print(data)
                res=self.sesh.post(posturl,data=data, headers=headers, proxies=self.proxy, allow_redirects=False)
                output(str(res.status_code),self.name,"cyan")
                print(res.text)
                if dict(res.headers)['Location'] == "https://shop.doverstreetmarket.com"+self.sitereg+"/checkout/cart/" and str(res.status_code) == "302":
                    output("In cart"+str(res.status_code),self.name,"cyan")
                    # try:
                    #     if self.name == "Task 1":
                    #         with open('temp.html', "a+") as r:
                    #             r.write(res.text)
                    # except:
                    #     None
                    return True
                else:
                    output("Waiting for restock of size "+str(self.size),self.name,"white")
                    time.sleep(delay)
            except Exception as e:
                try:
                    if self.name == "Task 1":
                        with open('temp.html', "a+") as r:
                            r.write(self.name+"atc error"+str(e))
                except:
                    None
                output("Failed atc",self.name,"red")
                time.sleep(delay)
    
    def shipping(self):
        for i in range(3):
            try:
                res=self.sesh.post("https://shop.doverstreetmarket.com"+self.sitereg+"/checkout/onepage/", headers=headers, proxies=self.proxy)
                output(str(res.status_code),self.name,"cyan")
                #with io.open("temp.html", "w", encoding="utf-8") as f:
                #    f.write(res.text)
                formkey=find_code(res.text, "\"form_key\" type=\"hidden\" value=\"", 16)
                addyid=find_code(res.text, "shipping[address_id]\" value=\"", 8)
                data={
                    "billing_address_id": "",
                    "billing[address_id]": addyid,
                    "billing[firstname]": self.fname,
                    "billing[lastname]": self.lname,
                    "billing[company]": "",
                    "billing[street][]": self.address1,
                    "billing[street][]": self.address2,
                    "billing[city]": self.city,
                    "billing[region_id]": "",
                    "billing[region]": self.province,
                    "billing[postcode]": self.zipCode,
                    "billing[country_id]": "GB",
                    "billing[telephone]": self.mobile,
                    "billing[fax]": "",
                    "billing[use_for_shipping]": "1",
                    "form_key": formkey
                }
                res=self.sesh.post("https://shop.doverstreetmarket.com"+self.sitereg+"/checkout/onepage/saveBilling/",data=data, headers=headers, proxies=self.proxy)
                output(str(res.status_code),self.name,"cyan")
                if str(res.status_code) in ["200", "302","320"]:
                    if self.sitereg == "":
                        data={
                            "shipping_method": "tablerate_bestway",
                            "form_key": formkey
                        }
                    else:
                        data={
                            "shipping_method": "matrixrate_matrixrate_1099",
                            "ship-note": "",
                            "form_key": formkey
                        }
                    res=self.sesh.post("https://shop.doverstreetmarket.com"+self.sitereg+"/checkout/onepage/saveShippingMethod/",data=data, headers=headers, proxies=self.proxy)
                    output(str(res.status_code),self.name,"cyan")
                    data={
                        "payment[method]": "adyen_pay_by_link",
                        "form_key": formkey
                    }
                    res=self.sesh.post("https://shop.doverstreetmarket.com"+self.sitereg+"/checkout/onepage/savePayment/",data=data, headers=headers, proxies=self.proxy)
                    output(str(res.status_code),self.name,"cyan")
                    if str(res.status_code) in ["200", "302","320"]:
                        output("Submitted shipping",self.name,"cyan")
                        return formkey
                    else:
                        output("Failed shipping (could be atc error)"+str(res.status_code),self.name,"red")
                        time.sleep(1000)
                        return False
                else:
                    output("Failed shipping (Could be atc error)",self.name,"red")
                    try:
                        if self.name == "Task 1":
                            with open('temp.html', "a+") as r:
                                r.write(self.name+"Ship fail"+res.text)
                    except:
                        None
                    time.sleep(1000)
                    return False
            except Exception as e:
                try:
                    if self.name == "Task 1":
                        with open('temp.html', "a+") as r:
                            r.write(self.name+"Ship fail"+str(e)+res.text)
                except:
                    None
                output("Failed shipping (Could be atc error or rate-limit)",self.name,"red")
                time.sleep(1000)
                return False

    def pay(self, formkey):
        for i in range(3):
            try:
                output("Submitting order",self.name,"cyan")
                data={
                    "payment[method]": "adyen_pay_by_link",
                    "form_key": formkey,
                    "agreement[1]": "1"
                }
                res=self.sesh.post("https://shop.doverstreetmarket.com"+self.sitereg+"/checkout/onepage/saveOrder/",data=data, headers=headers, proxies=self.proxy)
                print(res.status_code)
                res=self.sesh.get("https://shop.doverstreetmarket.com"+self.sitereg+"/adyen/process/redirect/", headers=headers, proxies=self.proxy)
                print(res.text)
                url=find_code(res.text, "action=\"", 200).split("\"")[0]
                self.finish=datetime.now()
                if self.send_webhook(url):
                    output("Checkout link sent",self.name,"green")
                    return
                else:
                    output(url,self.name,"green")
                    return
            except Exception as e:
                try:
                    if self.name == "Task 1":
                        with open('temp.html', "a+") as r:
                            r.write(self.name+"payment fail"+str(e))
                except:
                    None
                output("Checkout Error", self.name,"red")
    def send_webhook(self, url):
        try:
            try:
                checkout_speed=str(self.finish-clss.start)
            except:
                checkout_speed="Unknown"
            try:
                img="https://d2f5l340292seg.cloudfront.net/catalog/product/cache/1/thumbnail/150x/"+find_code(self.cart,"https://d2f5l340292seg.cloudfront.net/catalog/product/cache/1/thumbnail/150x/",120).split("\"")[0]
            except:
                img="https://cdn.cybersole.io/media/discord-logo.png"
            try:
                title=find_code(self.cart,"<h1>", 50).split("<")[0]
            except:
                title="Unknown"
            try:
                price=find_code(self.cart,"Price\":",10).split(",")[0]
            except:
                price="Unknown"
            data={
                "embeds": [
                {
                "author": {
                "name": "",
                "url": "",
                "icon_url": ""
                },  
                "title": "Click to pay",
                "description": "**"+title+"**",
                "timestamp":datetime.now().isoformat(),
                "url": url,
                "thumbnail":{"url":img},
                "color": "2303786",
                "footer":{"text":"Clarencs E-Shopper", "icon_url":""},
                "fields": [
                    {
                    "name":"Size",
                    "value":self.size,
                    "inline":"true"
                    },
                    {
                    "name":"Price",
                    "value":price,
                    "inline":"true"
                    },
                    {
                    "name":"Card",
                    "value":"||"+str(self.cardName)+"||",
                    "inline":"true"
                    },
                    {
                    "name":"Task",
                    "value":self.name,
                    "inline":"true"
                    },
                    {
                    "name":"Proxy",
                    "value":"||"+str(self.data["proxy"])+"||",
                    "inline":"true"
                    },
                    {
                    "name":"Speed",
                    "value":checkout_speed,
                    "inline":"true"
                    },
                    {
                    "name":"Item",
                    "value":self.url,
                    "inline":"false"
                    }
                ],
                }
            ]
            }
            if not link:
                data["embeds"][0]["title"]="Checkout Successful "+str(self.cardName)
            res=requests.post(self.webhook, data=json.dumps(data), headers={"Content-Type": "application/json"})
            if str(res.status_code)=="204":
                return True
            else:
                return False
        except:
            return False
