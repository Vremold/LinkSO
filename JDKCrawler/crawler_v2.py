"""
目标：爬取Java® Platform, Standard Edition & Java Development Kit
Version 17 API Specification里面的全部API
网址：https://docs.oracle.com/en/java/javase/17/docs/api/index.html
"""

import os
import sys
import time
import json

import requests
from scrapy.selector import Selector

BASE_URL = "https://docs.oracle.com/en/java/javase/17/docs/api/"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"'
}
save_dir = "./export"

def req(url, retry=5, interval=10):
    while retry > 0:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return Selector(response=response)
        time.sleep(interval)
        retry -= 1 

def clean_text(texts):
    text = "".join(texts)
    return text.strip().replace("\n", "")

def crawl_module(url):
    response = req(url)
    module_divs = response.css("div.col-first.all-modules-table")
    des_divs = response.css("div.col-last.all-modules-table")
    modules = []
    for module, des in zip(module_divs, des_divs):
        module_name = module.css("a::text").extract_first()
        module_url = BASE_URL + module.css("a::attr(href)").extract_first()
        module_des = des.css("*::text").extract()
        module_des = clean_text(module_des)
        modules.append([module_name, module_url, module_des])
    return modules

def crawl_package(module_name, url):
    response = req(url)
    package_divs = response.css("div.col-first.package-summary-table")
    des_divs = response.css("div.col-last.package-summary-table")
    packages = []
    for package, des in zip(package_divs, des_divs):
        package_name = package.css("a::text").extract_first()
        package_url = BASE_URL + module_name + "/" + package.css("a::attr(href)").extract_first()
        package_des = des.css("*::text").extract()
        package_des = clean_text(package_des)
        packages.append([module_name, package_name, package_url, package_des])
    return packages

def crawl_interfaces_or_classes(module_name, package_name, url):
    response = req(url)
    ic_divs = response.css("div.col-first.class-summary")
    des_divs = response.css("div.col-last.class-summary")
    ics = []
    for ic, des in zip(ic_divs, des_divs):
        ic_name = ic.css("a::text").extract_first()
        ic_url = BASE_URL + ic.css("a::attr(href)").extract_first()
        ic_des = des.css("*::text").extract()
        ic_des = clean_text(ic_des)
        ics.append([module_name, package_name, ic_name, ic_url, ic_des])
    return ics

def crawl_apis(module_name, package_name, ci_name):
    url = "https://docs.oracle.com/en/java/javase/17/docs/api/" + module_name + "/" + "/".join(package_name.split(".")) + "/"+ ci_name + ".html"
    print(url)
    response = req(url)
    api_divs = response.css("#method-summary-table\.tabpanel > div > div.col-second")
    api_des_divs = response.css("#method-summary-table\.tabpanel > div > div.col-last")
    apis = list()
    for api_div, api_des_div in zip(api_divs, api_des_divs):
        api_name = api_div.css("*::text").extract()
        api_name = clean_text(api_name)
        api_des = api_des_div.css("*::text").extract()
        api_des = clean_text(api_des)
        apis.append([module_name, package_name, ci_name, api_name, api_des])
    
    return apis

if __name__ == "__main__":
    # all_modules = crawl_module("https://docs.oracle.com/en/java/javase/17/docs/api/index.html")
    # with open(os.path.join(save_dir, "modules.json"), "w", encoding="utf-8") as outf:
    #     json.dump(all_modules, outf, ensure_ascii=False)
    # with open(os.path.join(save_dir, "modules.json"), "r", encoding="utf-8") as inf:
    #     all_modules = json.load(inf)
    
    # all_packages = []
    # for module_name, module_url, module_des in all_modules:
    #     packages = crawl_package(module_name, module_url)
    #     all_packages.extend(packages)
    # with open(os.path.join(save_dir, "packages.json"), "w", encoding="utf-8") as outf:
    #     json.dump(all_packages, outf, ensure_ascii=False)
    # with open(os.path.join(save_dir, "packages.json"), "r", encoding="utf-8") as inf:
    #     all_packages = json.load(inf)

    # all_ics = []
    # for module_name, package_name, package_url, _ in all_packages:
    #     ics = crawl_interfaces_or_classes(module_name, package_name, package_url)
    #     all_ics.extend(ics)
    # with open(os.path.join(save_dir, "class_or_interfaces.json"), "w", encoding="utf-8") as outf:
    #     json.dump(all_ics, outf)
    
    finished_cinames = set()
    with open(os.path.join(save_dir, "apis.json"), "r", encoding="utf-8") as inf:
        for line in inf:
            obj = json.dumps(line)
            finished_cinames.add(line[2])
    all_ics = []
    with open(os.path.join(save_dir, "class_or_interfaces.json"), "r", encoding="utf-8") as inf:
        all_ics = json.load(inf)
    outf = open(os.path.join(save_dir, "apis.json"), "a+", encoding="utf-8")
    for module_name, package_name, ci_name, _, _ in all_ics:
        if ci_name in finished_cinames:
            continue
        print("[Crawler V2] dealing with {}#{}#{}".format(module_name, package_name, ci_name))
        apis = crawl_apis(module_name, package_name, ci_name)
        for api in apis:
            outf.write("{}\n".format(json.dumps(api)))