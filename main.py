import json
import os
import re
import urllib.request
import zipfile

from elasticsearch import Elasticsearch
from elasticsearch import helpers

compiled_raw_json_file_patter = re.compile(r'^raw/.*\.json$')


def download_trans_zip_from_paratranz(project_id,
                                      secret,
                                      out_file_path,
                                      base_url="https://paratranz.cn"):
    """
    paratranzからzipをダウンロードする
    :param project_id:
    :param secret:
    :param base_url:
    :param out_file_path:
    :return:
    """

    request_url = "{}/api/projects/{}/artifacts/download".format(base_url, project_id)
    req = urllib.request.Request(request_url)
    req.add_header("Authorization", secret)

    with open(out_file_path, "wb") as my_file:
        my_file.write(urllib.request.urlopen(req).read())

    return out_file_path


def salvage_raw_jsons_from_zip(paratranz_zip_path):
    results = []

    with zipfile.ZipFile(paratranz_zip_path) as zip_file:
        infos = zip_file.infolist()

        for info in infos:
            if compiled_raw_json_file_patter.match(info.filename) is None:
                continue

            entry_list = json.loads(zip_file.read(info.filename))
            results.extend(entry_list)

    return results


def sub(index_name,
        paratranz_project_code,
        paratranz_secret,
        es_connection):
    # paratranzからzipファイルのダウンロード
    zip_path = download_trans_zip_from_paratranz(project_id=paratranz_project_code,
                                                 secret=paratranz_secret,
                                                 out_file_path="tmp/paratranz_%s.zip" % (
                                                     paratranz_project_code))

    # zip_path = r'./tmp/paratranz_91.zip'

    # rawデータが入ったデータを読み込み
    entries = salvage_raw_jsons_from_zip(zip_path)

    # ESにインポート
    entries_length = len(entries)
    chunk_size = 2000
    for i in range(0, entries_length, chunk_size):
        print("%d ~ %d" % (i, min(i + chunk_size - 1, entries_length)))
        helpers.bulk(es_connection, entries[i:i + chunk_size], index=index_name)


def main(paratranz_secret,
         elasticsearch_host,
         elasticsearch_password,
         elasticsearch_username="elastic",
         elasticsearch_port=9200):
    # 一時フォルダ用意
    os.makedirs("tmp", exist_ok=True)

    es_connection = Elasticsearch(host=elasticsearch_host,
                                  port=elasticsearch_port,
                                  http_auth=(elasticsearch_username,
                                             elasticsearch_password))

    # Europa Universalis IV
    # https://paratranz.cn/projects/76
    sub(index_name="eu4",
        paratranz_project_code=76,
        paratranz_secret=paratranz_secret,
        es_connection=es_connection)

    # Crusader Kings II
    # https://paratranz.cn/projects/91
    sub(index_name="ck2",
        paratranz_project_code=91,
        paratranz_secret=paratranz_secret,
        es_connection=es_connection)

    # Imperator: Rome
    # https://paratranz.cn/projects/91
    sub(index_name="ir",
        paratranz_project_code=335,
        paratranz_secret=paratranz_secret,
        es_connection=es_connection)


if __name__ == '__main__':
    main(paratranz_secret=os.environ.get("PARATRANZ_SECRET"),
         elasticsearch_host=os.environ.get("ELASTICSEARCH_HOST"),
         elasticsearch_password=os.environ.get("ELASTICSEARCH_PASSWORD"))
