# coding=utf8

import os
import re
import logging
import xml.etree.cElementTree as ET
import click
import pymongo
from tools import shape_element, chinese_words


log_format = '[%(asctime)-15s %(levelname)s:%(name)s:%(module)s:%(lineno)d] %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)
file_name = "beijing_china.osm"
client = pymongo.MongoClient()
db = client.uda
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


@click.command()
def show_incorrect_street():
    et = ET.parse(file_name)
    street_types = {}
    for element in et.iter():
        if element.tag in {"node", "way"}:
            for tag in element.iter("tag"):
                if tag.get("k") == "addr:street":
                    value = tag.get("v")
                    # 中文分词太过麻烦暂时忽略
                    if chinese_words.search(value):
                        continue
                    res = street_type_re.search(value.split(",")[0])
                    if res:
                        m = res.group()
                        street_types.setdefault(m, set())
                        street_types[m].add(value)
    for k, v in sorted(street_types.items(), key=lambda x:-len(x[1])):
        logging.info("{:10} {}".format(k, v))


@click.command()
def loadmongo():
    logging.info("begin load data to mongo")
    et = ET.parse(file_name)
    logging.info("parsed finish")
    if db.openstreetmap.count():
        db.openstreetmap.drop()
    # db.createCollection("openstreetmap")
    i = 0
    buffer_list = []
    for element in et.iter():
        json_obj = shape_element(element)
        if json_obj:
            buffer_list.append(json_obj)
        if len(buffer_list) >= 1000:
            db.openstreetmap.insert_many(buffer_list)
            buffer_list = []
        i += 1
        if i %100000 == 0:
            logging.info("insert to mongo: {}".format(i))
    else:
        db.openstreetmap.insert_many(buffer_list)
        buffer_list = []

    cnt = db.openstreetmap.count()
    logging.info("finish load data to mongo {}".format(cnt))


@click.command()
def stat():
    file_size = os.path.getsize("beijing_china.osm")
    file_size_show = "{:.2f}MB".format(file_size/1024.0/1024)
    all_count = db.openstreetmap.find().count()
    node_count = db.openstreetmap.find({"type": "node"}).count()
    way_count = db.openstreetmap.find({"type": "way"}).count()
    distinct_user_count = len(db.openstreetmap.distinct("created.uid"))

    logging.info("{k:30}: {v}".format(k="file_size", v=file_size))
    logging.info("{k:30}: {v}".format(k="file_size_show", v=file_size_show))
    logging.info("{k:30}: {v}".format(k="all_count", v=all_count))
    logging.info("{k:30}: {v}".format(k="node_count", v=node_count))
    logging.info("{k:30}: {v}".format(k="way_count", v=way_count))
    logging.info("{k:30}: {v}".format(k="distinct_user_count", v=distinct_user_count))


@click.group()
def cli():
    pass


if __name__ == "__main__":
    cli.add_command(loadmongo)
    cli.add_command(stat)
    cli.add_command(show_incorrect_street)
    cli()