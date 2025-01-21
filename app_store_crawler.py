#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
* @ Author: firstfu
* @ Create Time: 2024-03-19
* @ Description: Apple App Store 爬蟲程式
"""

import json
from datetime import datetime
from urllib.parse import quote

import pandas as pd
import requests


def search_apps(keyword, country="tw", limit=40):
    """
    搜索 App Store 應用
    :param keyword: 搜索關鍵字
    :param country: 國家/地區代碼
    :param limit: 返回結果數量
    :return: 搜索結果列表
    """
    # 將關鍵字進行 URL 編碼
    encoded_keyword = quote(keyword)

    # App Store 搜索 API
    url = f"https://itunes.apple.com/search?term={encoded_keyword}&country={country}&entity=software&limit={limit}"

    try:
        # 發送請求
        response = requests.get(url)
        response.raise_for_status()  # 檢查請求是否成功

        # 解析 JSON 響應
        data = response.json()

        return data.get("results", [])

    except requests.exceptions.RequestException as e:
        print(f"請求出錯: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"JSON 解析錯誤: {e}")
        return []


def print_app_info(app):
    """
    格式化打印應用信息
    :param app: 應用信息字典
    """
    print("\n" + "=" * 50)
    print(f"應用名稱: {app.get('trackName', 'N/A')}")
    print(f"開發者: {app.get('artistName', 'N/A')}")
    print(f"應用類別: {app.get('primaryGenreName', 'N/A')}")
    print(f"價格: {'免費' if app.get('price', 0) == 0 else f'${app.get('price')}'}")
    print(f"評分: {app.get('averageUserRating', 'N/A')}")
    print(f"評分數量: {app.get('userRatingCount', 'N/A')}")
    print(f"版本: {app.get('version', 'N/A')}")
    print(f"大小: {app.get('fileSizeBytes', 'N/A')} bytes")
    print(f"最低系統要求: iOS {app.get('minimumOsVersion', 'N/A')}")
    print(f"App Store 链接: {app.get('trackViewUrl', 'N/A')}")
    print("=" * 50)


def save_to_excel(apps, keyword):
    """
    將應用數據保存到 Excel 文件
    :param apps: 應用列表
    :param keyword: 搜索關鍵字
    :return: 保存的文件名
    """
    # 準備數據
    data = []
    for app in apps:
        app_data = {
            "應用名稱": app.get("trackName", "N/A"),
            "開發者": app.get("artistName", "N/A"),
            "應用類別": app.get("primaryGenreName", "N/A"),
            "價格": "免費" if app.get("price", 0) == 0 else f"${app.get('price')}",
            "評分": app.get("averageUserRating", "N/A"),
            "評分數量": app.get("userRatingCount", "N/A"),
            "版本": app.get("version", "N/A"),
            "大小(bytes)": app.get("fileSizeBytes", "N/A"),
            "最低系統要求": f"iOS {app.get('minimumOsVersion', 'N/A')}",
            "App Store 链接": app.get("trackViewUrl", "N/A"),
            "更新日期": app.get("currentVersionReleaseDate", "N/A"),
            "應用描述": app.get("description", "N/A"),
        }
        data.append(app_data)

    # 創建 DataFrame
    df = pd.DataFrame(data)

    # 生成文件名（包含時間戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"app_store_{keyword}_{timestamp}.xlsx"

    # 保存到 Excel
    df.to_excel(filename, index=False, engine="openpyxl")

    return filename


def main():
    """
    主函數
    """
    print("歡迎使用 App Store 爬蟲程式！")
    keyword = input("請輸入要搜索的應用關鍵字: ")

    print("\n正在搜索，請稍候...\n")
    apps = search_apps(keyword)

    if not apps:
        print("未找到相關應用或發生錯誤。")
        return

    print(f"找到 {len(apps)} 個相關應用")

    # 保存到 Excel
    filename = save_to_excel(apps, keyword)
    print(f"\n數據已保存到文件: {filename}")

    # 詢問是否要在終端顯示詳細信息
    show_details = input("\n是否要在終端顯示詳細信息？(y/n): ").lower().strip() == "y"
    if show_details:
        for app in apps:
            print_app_info(app)


if __name__ == "__main__":
    main()
