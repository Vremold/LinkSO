import os
import pickle
import json

src_pkl = "./build/packages.pkl"
save_file = "./build/packages.json"

result = {}
with open(src_pkl, "rb") as inf:
    obj = pickle.load(inf)
    for package in obj:
        if package.name not in result:
            result[package.name] = {"exceptions": [], "classes": [], "interfaces": [], "errors": [], "enums": []}
        for exception in package.exceptions:
            result[package.name]["exceptions"].append(exception.name)
        for clss in package.classes:
            result[package.name]["classes"].append(clss.name)
        for inter in package.interfaces:
            result[package.name]["interfaces"].append(inter.name)
        for err in package.errors:
            result[package.name]["errors"].append(err.name)
        for enum in package.enums:
            if not enum:
                continue
            print(type(enum), enum)
            result[package.name]["enums"].append(enum.name)

with open(save_file, "w", encoding="utf-8") as outf:
    json.dump(result, outf, ensure_ascii=False)            