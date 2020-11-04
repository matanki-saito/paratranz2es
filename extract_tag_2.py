import json
import os
import re
import urllib.request
import zipfile

import yaml

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
        data.update({
            "_id": data['key'],
            "pz_pj_code": paratranz_project_code
        })


def sub(index_name,
        paratranz_project_code,
        paratranz_secret):
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

    # パターンを抽出
    tags = {}
    valid = re.compile(r"\[([A-Za-z0-9\.\-]+)\|E\]")
    for entry in entries:
        for match in valid.findall(entry['original']):
            fragment = match.split(".")
            fragment.reverse()

            if fragment[0] in tags:
                tags[fragment[0]] += 1
            else:
                tags[fragment[0]] = 1

    filterd_tags = {}
    for tag in tags:
        if tags[tag] >= 0:
            filterd_tags[tag] = tags[tag]

    # 出力
    with open('tag.yml', 'w') as outfile:
        yaml.dump(filterd_tags, outfile, default_flow_style=False)


def main(paratranz_secret,
         elasticsearch_host,
         elasticsearch_password,
         elasticsearch_username="elastic",
         elasticsearch_port=9200):
    # 一時フォルダ用意
    os.makedirs("tmp", exist_ok=True)

    # Crusader Kings II
    # https://paratranz.cn/projects/91
    sub(index_name="ck2",
        paratranz_project_code=91,
        paratranz_secret=paratranz_secret)


if __name__ == '__main__':
    main(paratranz_secret=os.environ.get("PARATRANZ_SECRET"),
         elasticsearch_host=os.environ.get("ELASTICSEARCH_HOST"),
         elasticsearch_password=os.environ.get("ELASTICSEARCH_PASSWORD"))
