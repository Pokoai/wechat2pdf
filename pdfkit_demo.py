#! python
# wechat2pdf.py - 将微信公众号文章导出为pdf文档

"""
初步版本：
文章链接手动提供

后续改进：
自动获取公众号全部历史文章链接，将文章标题和链接存储到 csv 文件中
"""

import pdfkit
import requests, bs4
import os, sys
import re, time


# 时间戳转换为当地时间
def timestamp_convert_localdate(timestamp, time_format="%Y-%m-%d"):
    timeArray = time.localtime(timestamp)
    styleTime = time.strftime(str(time_format), timeArray)
    return styleTime

# pdf的一些参数
PDF_OPTIONS = {
    'page-size': 'A4',
    'encoding': "UTF-8",
}

# requests 下载网页
url = 'https://mp.weixin.qq.com/s/MOOZeVzTjZcRZlX7cuSZmw?'
res = requests.get(url)
res.raise_for_status()
# with open('./temp.txt', 'wb') as f:
#     for chunk in res.iter_content(1000):
#         f.write(chunk)


# 替换图片src、元素，否则图片无法显示
cnt_html = res.text.replace(
        "data-src", "src").replace('style="visibility: hidden;"', "")


# 获取文章标题
# 需要借助爬虫提取文章标题
soup = bs4.BeautifulSoup(res.text)
titleElem = soup.select('#activity-name')
title = titleElem[0].getText().split('\n')[2]

wechatNameElem = soup.select('#js_name')
wechatName = wechatNameElem[0].getText().split()[0]

# 发布时间是用 JavaScript 渲染后显示的，以下方式不起作用
# publishTimeElem = soup.select('#publish_time')
# publishTime = publishTimeElem[0].getText()

# 改用正则表达式，截取需要的时间戳
# ![](https://img.arctee.cn/one/202207021312051.png)
match = re.search(r'\{e\(0,(.*),0,document.getElementById\("publish_time"\)\)', res.text, re.S)
if match:
    # print(match.group(1))
    timestamp = int(match.group(1).split('"')[1])
publishTime = timestamp_convert_localdate(timestamp)

pdfTitle = wechatName + '-' + publishTime + '-' + title

# 设置文章存储路径
desktop_path = "D:\Media\Desktop\wechat2pdf"
output_path = os.path.join(desktop_path, pdfTitle + '.pdf')
output_path2 = os.path.join(desktop_path, pdfTitle + '(img).pdf')

# 利用 pdfkit 开始生成 pdf 文档
pdfkit.from_url(url, output_path)  # 无图片
pdfkit.from_string(cnt_html, output_path2)  # 有图片

print('#' * 80)
print("文章已生成！")
print("标题：" + pdfTitle)
print("地址：" + output_path)
print('#' * 80)