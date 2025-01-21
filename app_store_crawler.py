#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
* @ Author: firstfu
* @ Create Time: 2024-03-19
* @ Description: Apple App Store 爬蟲程式
"""

import json
import math
import re
import time
from datetime import datetime
from urllib.parse import quote

import pandas as pd
import requests


def calculate_credibility_score(app, reviews):
    """
    計算應用的可信度評分
    :param app: 應用信息
    :param reviews: 應用評論列表
    :return: 可信度評分 (0-100)
    """
    # 基礎數據
    rating = float(app.get("averageUserRating", 0))
    rating_count = int(app.get("userRatingCount", 0))

    # 1. 評分數量權重 (使用對數函數平滑處理)
    count_weight = min(1.0, math.log(rating_count + 1) / math.log(10000)) if rating_count > 0 else 0

    # 2. 評論質量分析
    review_quality_score = 0
    if reviews:
        valid_reviews = 0
        total_length = 0

        for review in reviews:
            content = str(review.get("內容", ""))
            # 檢查評論是否有效（不是簡單的表情符號或重複字符）
            if len(content) > 10 and not re.match(r"^(.)\1*$", content):
                valid_reviews += 1
                total_length += len(content)

        # 計算平均評論長度和有效評論比例
        avg_length = total_length / len(reviews) if reviews else 0
        valid_ratio = valid_reviews / len(reviews) if reviews else 0

        # 評論質量得分 (0-1)
        review_quality_score = (min(1.0, avg_length / 100) + valid_ratio) / 2

    # 3. 評分分佈分析（檢測是否有刷分嫌疑）
    rating_distribution_score = 1.0
    if rating > 4.8 and rating_count < 100:  # 高分但評分數少，可能有刷分嫌疑
        rating_distribution_score *= 0.7

    # 4. 時間衰減因子（優先展示較新的應用）
    try:
        update_date = datetime.strptime(app.get("currentVersionReleaseDate", ""), "%Y-%m-%dT%H:%M:%SZ")
        days_since_update = (datetime.now() - update_date).days
        time_decay = math.exp(-days_since_update / 365)  # 一年的衰減率
    except:
        time_decay = 0.5

    # 綜合計算最終得分
    base_score = (rating * 0.4 + count_weight * 0.3 + review_quality_score * 0.2 + rating_distribution_score * 0.1) * 100
    final_score = base_score * (0.8 + 0.2 * time_decay)  # 時間衰減影響20%

    return round(final_score, 2)


def fetch_reviews(app_id, country="tw", limit=50):
    """
    獲取應用評論
    :param app_id: 應用ID
    :param country: 國家/地區代碼
    :param limit: 評論數量
    :return: 評論列表
    """
    reviews = []
    offset = 0

    while len(reviews) < limit:
        # App Store 評論 API
        url = f"https://itunes.apple.com/rss/customerreviews/id={app_id}/sortBy=mostRecent/page={offset + 1}/json"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            # 檢查是否有評論數據
            entries = data.get("feed", {}).get("entry", [])
            if not entries or not isinstance(entries, list):
                break

            for entry in entries:
                review = {
                    "評論者": entry.get("author", {}).get("name", {}).get("label", "N/A"),
                    "評分": entry.get("im:rating", {}).get("label", "N/A"),
                    "標題": entry.get("title", {}).get("label", "N/A"),
                    "內容": entry.get("content", {}).get("label", "N/A"),
                    "版本": entry.get("im:version", {}).get("label", "N/A"),
                    "時間": entry.get("updated", {}).get("label", "N/A"),
                }
                reviews.append(review)

            if len(reviews) >= limit:
                break

            offset += 1
            time.sleep(1)  # 避免請求過於頻繁

        except Exception as e:
            print(f"獲取評論時出錯: {e}")
            break

    return reviews[:limit]


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


def print_app_info(app, score):
    """
    格式化打印應用信息
    :param app: 應用信息字典
    :param score: 可信度評分
    """
    print("\n" + "=" * 50)
    print(f"應用名稱: {app.get('trackName', 'N/A')}")
    print(f"開發者: {app.get('artistName', 'N/A')}")
    print(f"應用類別: {app.get('primaryGenreName', 'N/A')}")
    print(f"價格: {'免費' if app.get('price', 0) == 0 else f'${app.get('price')}'}")
    print(f"評分: {app.get('averageUserRating', 'N/A')}")
    print(f"評分數量: {app.get('userRatingCount', 'N/A')}")
    print(f"可信度評分: {score}")
    print(f"版本: {app.get('version', 'N/A')}")
    print(f"大小: {app.get('fileSizeBytes', 'N/A')} bytes")
    print(f"最低系統要求: iOS {app.get('minimumOsVersion', 'N/A')}")
    print(f"App Store 链接: {app.get('trackViewUrl', 'N/A')}")
    print("=" * 50)


def save_to_json(apps_with_reviews, keyword):
    """
    將應用數據保存到 JSON 文件
    :param apps_with_reviews: 包含評論的應用列表
    :param keyword: 搜索關鍵字
    :return: 保存的文件名
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"app_store_{keyword}_{timestamp}.json"

    # 按可信度評分排序
    sorted_apps = sorted(apps_with_reviews, key=lambda x: x["credibility_score"], reverse=True)

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(sorted_apps, f, ensure_ascii=False, indent=2)

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

    # 獲取應用信息和評論，並計算可信度評分
    apps_with_reviews = []

    for app in apps:
        print(f"\n正在獲取 {app.get('trackName', 'N/A')} 的評論...")

        # 獲取評論
        reviews = fetch_reviews(app.get("trackId")) if app.get("trackId") else []

        # 計算可信度評分
        credibility_score = calculate_credibility_score(app, reviews)

        # 整理應用數據
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
            "credibility_score": credibility_score,
            "評論": reviews,
        }
        apps_with_reviews.append(app_data)

    # 保存到 JSON
    filename = save_to_json(apps_with_reviews, keyword)
    print(f"\n數據已保存到文件: {filename}")

    # 詢問是否要在終端顯示詳細信息
    show_details = input("\n是否要在終端顯示詳細信息？(y/n): ").lower().strip() == "y"
    if show_details:
        for app_data in apps_with_reviews:
            print_app_info(app_data, app_data["credibility_score"])


if __name__ == "__main__":
    main()
