#!/usr/bin/env python
# -*- coding:utf-8 -*-

import hashlib
import json
import os
import shutil
import urllib.request
import zipfile
from os.path import join

_ = join


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


def assembly_mod(mod_file_name,
                 resource_paratranz_sub_zip_file_path,
                 out_dir_path,
                 resource_dir):
    """
    Appモッドを作成
    :param mod_file_name: Modファイル名
    :param resource_paratranz_sub_zip_file_path: ParatranzからダウンロードできるSub Mod zipファイルのパス
    :param out_dir_path: 出力フォルダ
    :param resource_dir: リソースディレクトリ
    :return:
    """

    # TODO パス修正する
    ext_paratranz_sub_dir_path = _(".", "tmp", "paratranz_ext_sub")
    mod_dir_path = _(out_dir_path, mod_file_name)
    mod_loc_root_dir_path = _(mod_dir_path, "localization")
    mod_loc_replace_english_dir_path = _(mod_loc_root_dir_path, "replace", "english")

    # 初期化（AzureDevでは必要ない）
    if os.path.exists(ext_paratranz_sub_dir_path):
        shutil.rmtree(ext_paratranz_sub_dir_path)
    if os.path.exists(mod_dir_path):
        shutil.rmtree(mod_dir_path)
    os.makedirs(mod_dir_path, exist_ok=True)
    os.makedirs(mod_loc_root_dir_path, exist_ok=True)
    os.makedirs(mod_loc_replace_english_dir_path, exist_ok=True)

    # zip展開する
    with zipfile.ZipFile(resource_paratranz_sub_zip_file_path) as existing_zip:
        existing_zip.extractall(ext_paratranz_sub_dir_path)

    with zipfile.ZipFile(resource_paratranz_sub_zip_file_path) as existing_zip:
        existing_zip.extractall(ext_paratranz_sub_dir_path)

    # gameを移す
    shutil.copytree(src=_(ext_paratranz_sub_dir_path, "utf8", "game", "localization", "english"),
                    dst=_(mod_loc_root_dir_path, "english"),
                    ignore=shutil.ignore_patterns("cultures_l_english.yml",
                                                  "decisions_l_english.yml",
                                                  "nation_formation_l_english.yml",
                                                  "additional_place_l_english.yml",
                                                  "additional_names_l_english.yml"))

    # 下に３つはlocalization/replace/englishに入る
    shutil.move(_(ext_paratranz_sub_dir_path,
                  "utf8", "game", "localization", "english", "cultures_l_english.yml"),
                _(mod_loc_replace_english_dir_path, "cultures_l_english.yml"))
    shutil.move(_(ext_paratranz_sub_dir_path,
                  "utf8", "game", "localization", "english", "additional_place_l_english.yml"),
                _(mod_loc_replace_english_dir_path, "additional_place_l_english.yml"))
    shutil.move(_(ext_paratranz_sub_dir_path,
                  "utf8", "game", "localization", "english", "additional_names_l_english.yml"),
                _(mod_loc_replace_english_dir_path, "additional_names_l_english.yml"))

    # 必要ファイルを配置
    shutil.copy(_(resource_dir, "thumbnail.png"),
                _(mod_dir_path, "thumbnail.png"))
    shutil.copy(_(resource_dir, "descriptor.mod"),
                _(mod_dir_path, "descriptor.mod"))

    return mod_dir_path


def generate_dot_mod_file(mod_title_name,
                          mod_dir_name,
                          mod_tags,
                          mod_image_file_path,
                          mod_supported_version,
                          out_dir_path):
    """
    .modファイルを作る
    :param mod_title_name:
    :param mod_dir_name: ディレクトリの名前
    :param mod_tags: Set<String>型
    :param mod_image_file_path:
    :param mod_supported_version:
    :param out_dir_path: 出力ディレクトリのパス
    :return: 出力ファイルパス
    """

    os.makedirs(out_dir_path, exist_ok=True)

    out_file_path = _(out_dir_path, "{}.mod".format(mod_dir_name))

    with open(out_file_path, "w", encoding="utf-8") as fw:
        lines = [
            'name="{}"'.format(mod_title_name),
            'path="mod/{}"'.format(mod_dir_name),
            'tags={}'.format("{" + " ".join(map(lambda c: '"{}"'.format(c), mod_tags)) + "}"),
            'supported_version="{}"'.format(mod_supported_version),
            'picture="{}"'.format(mod_image_file_path)
        ]

        fw.write("\n".join(lines))

    return out_file_path


def generate_distribution_file(url,
                               mod_file_path,
                               out_file_path):
    """
    trielaで使用する配布用設定ファイルを作成する。
    :param url:
    :param mod_file_path:
    :param out_file_path:
    :return:
    """

    with open(mod_file_path, 'rb') as fr:
        md5 = hashlib.md5(fr.read()).hexdigest()

    d_new = {'file_md5': md5,
             'url': url,
             'file_size': os.path.getsize(mod_file_path)}

    with open(out_file_path, "w", encoding="utf-8") as fw:
        json.dump(d_new, fw, indent=2, ensure_ascii=False)

def update_source(mod_folder_path):
    shutil.rmtree("source", ignore_errors=True)
    shutil.copytree(mod_folder_path, _("source"))


def main():
    # 一時フォルダ用意
    os.makedirs(_(".", "tmp"), exist_ok=True)
    os.makedirs(_(".", "out"), exist_ok=True)
    out_dir_path = _(".", "out")

    # main name
    mod_file_name = "japanesesub"

    # 翻訳の最新版をダウンロードする project_id=350はI:R JPのプロジェクトID
    p_file_sub_path = download_trans_zip_from_paratranz(
        project_id=350,
        secret=os.environ.get("PARATRANZ_SECRET"),
        out_file_path=_(".", "tmp", "paratranz_sub.zip"))

    print("p_file_sub_path:{}".format(p_file_sub_path))

    # Modを構築する（フォルダのまま）
    mod_folder_path = assembly_mod(
        mod_file_name=mod_file_name,
        resource_paratranz_sub_zip_file_path=p_file_sub_path,
        out_dir_path=out_dir_path,
        resource_dir=_(".", "resource"))

    print("mod_dir_path:{}".format(out_dir_path))

    # .modファイルを作成する
    generate_dot_mod_file(
        mod_title_name="Japanese Language Mod Sub",
        mod_dir_name=mod_file_name,
        mod_tags={"Translation", "Localisation"},
        mod_image_file_path="title.jpg",
        mod_supported_version="2.0.*",
        out_dir_path=out_dir_path)

    print("generate .mod file")

    # utf8ファイルを移動する（この後git pushする）
    update_source(mod_folder_path=mod_folder_path)


if __name__ == "__main__":
    main()
