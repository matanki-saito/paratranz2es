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


def convert(datas, paratranz_project_code):
    for data in datas:
        base = data['key'].split(':')

        if len(base) >= 2:
            key = base[0]
            version = base[1]
        else:
            key = base[0]
            version = None

        data['key'] = key

        data.update({
            "_id": key,
            "text_version": version,
            "pz_pj_code": paratranz_project_code
        })


def sub(index_name,
        paratranz_project_code,
        paratranz_secret,
        es_connection):
    out_file_path = "tmp/paratranz_%s.zip" % paratranz_project_code

    print("index_name=%s,code=%s" % (index_name, paratranz_project_code))

    if not os.path.exists(out_file_path):
        # paratranzからzipファイルのダウンロード
        out_file_path = download_trans_zip_from_paratranz(project_id=paratranz_project_code,
                                                          secret=paratranz_secret,
                                                          out_file_path=out_file_path)
        print("download data")

    # rawデータが入ったデータを読み込み
    entries = salvage_raw_jsons_from_zip(out_file_path)

    # 変換
    convert(entries, paratranz_project_code)

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
    # https://paratranz.cn/projects/335
    sub(index_name="ir",
        paratranz_project_code=335,
        paratranz_secret=paratranz_secret,
        es_connection=es_connection)

    # Imperator: Rome pronoun
    # https://paratranz.cn/projects/350
    sub(index_name="ir",
        paratranz_project_code=350,
        paratranz_secret=paratranz_secret,
        es_connection=es_connection)

    # Hearts of Iron IV
    # https://paratranz.cn/projects/903
    sub(index_name="hoi4",
        paratranz_project_code=903,
        paratranz_secret=paratranz_secret,
        es_connection=es_connection)

    # Hearts of Iron IV Kaiserreich
    # https://paratranz.cn/projects/500
    sub(index_name="kr",
        paratranz_project_code=500,
        paratranz_secret=paratranz_secret,
        es_connection=es_connection)

    # Crusader Kings III
    # https://paratranz.cn/projects/1518
    sub(index_name="ck3",
        paratranz_project_code=1518,
        paratranz_secret=paratranz_secret,
        es_connection=es_connection)


if __name__ == '__main__':
    main(paratranz_secret=os.environ.get("PARATRANZ_SECRET"),
         elasticsearch_host=os.environ.get("ELASTICSEARCH_HOST"),
         elasticsearch_password=os.environ.get("ELASTICSEARCH_PASSWORD"))
