#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日早报推送 — 企业微信群机器人（带链接版）
每天8:00自动抓取百度热搜并推送，每条新闻带可点击链接
"""

import requests
import re
from datetime import datetime

WEBHOOK_URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=b4cc3813-779a-4c22-b8f9-6b594caf6c59"

WEEKDAYS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]

def get_news():
    """从百度热搜抓取新闻标题+链接"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    url = "https://top.baidu.com/board?tab=realtime"
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = "utf-8"
        html = resp.text
        
        news_items = []
        
        # 从页面JSON数据中提取标题和链接
        pattern1 = r'"word":"([^"]+)"[^}]*"url":"([^"]+)"'
        matches1 = re.findall(pattern1, html)
        
        if matches1:
            for title, link in matches1[:15]:
                if link.startswith("//"):
                    link = "https:" + link
                elif link.startswith("/"):
                    link = "https://top.baidu.com" + link
                elif not link.startswith("http"):
                    link = "https://www.baidu.com/s?wd=" + requests.utils.quote(title)
                news_items.append((title, link))
        
        # 备用：从文本中找热搜标题
        if not news_items:
            pattern2 = r'"word":"([^"]+)"'
            titles = re.findall(pattern2, html)
            for i, title in enumerate(titles[:15]):
                link = f"https://www.baidu.com/s?wd={requests.utils.quote(title)}"
                news_items.append((title, link))
        
        return news_items
        
    except Exception as e:
        print(f"抓取新闻出错: {e}")
        return []

def push_to_wechat(news_items):
    """推送到企业微信群机器人"""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    weekday = WEEKDAYS[now.weekday()]
    
    md_content = f"# 📰 每日早报\n"
    md_content += f"> **{date_str} {weekday}**\n\n"
    
    if not news_items:
        md_content += "⚠️ 今日暂无热点新闻数据\n"
    else:
        for i, (title, link) in enumerate(news_items, 1):
            md_content += f"{i}. [{title}]({link})\n"
    
    md_content += "\n---\n"
    md_content += "🤖 *每日早报机器人 · 08:30 自动推送*\n\n"
    md_content += "> ⏰ **记得打卡！**"
    
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "content": md_content
        }
    }
    
    try:
        resp = requests.post(WEBHOOK_URL, json=payload, timeout=10)
        result = resp.json()
        print(f"推送结果: {result}")
        return result.get("errcode") == 0
    except Exception as e:
        print(f"推送出错: {e}")
        return False

def main():
    print(f"========== 每日早报 {datetime.now().strftime('%Y-%m-%d %H:%M')} ==========")
    news = get_news()
    print(f"✅ 抓取到 {len(news)} 条新闻")
    success = push_to_wechat(news)
    if success:
        print("✅ 推送成功！每条新闻均附带了可点击链接。")
    else:
        print("❌ 推送失败！")

if __name__ == "__main__":
    main()
