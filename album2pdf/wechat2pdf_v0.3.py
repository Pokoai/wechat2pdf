#! python
# wechat2pdf_v0.3.py - 将微信公众号合集文章批量导出为pdf文档

"""
初步版本：
合集链接手动提供

后续改进：
1. 自动获取公众号全部合集链接，然后手动选取感兴趣的合集
2. 用 pyqt5 封装起来
3. 多线程采集（仅仅为了学习实践，实际上没必要，因为一次性采集文章不多）
"""

import pdfkit
import requests, bs4
import os, sys
import re, time
import json

# 模板html,微信抓取到的html内容过多
T_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="referrer" content="never">
    <meta name="referrer" content="no-referrer">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <style>{style}</style>
</head>
<body>
    {content}
</body>
</html>"""

# pdf的一些参数
PDF_OPTIONS = {
    'page-size': 'A4',
    'encoding': "UTF-8",
}

# 新建文件夹
# 该方法只能创建单级文件夹，无法递归创建
# 直接采用系统提供的 os.makedirs 可以递归
# def mkdir(path):
#     folder = os.path.exists(path)
#     if not folder:
#         print("--- 新建文件夹... ---")
#         os.mkdir(path)
#         print("--- OK ---")
#     else:
#         print("--- 文件夹已存在! ---")


# 新建文件
def mkfile(file_path):
    file = os.path.exists(file_path)
    if not file:
        # print("--- 新建文件... ---")
        file = open(file_path, 'w')
        # print("--- OK ---")
        file.close()
    else:
        # print("--- 文件已存在! ---")
        pass


# 时间戳转换为当地时间
def timestamp_convert_localdate(timestamp, time_format="%Y-%m-%d"):
    timeArray = time.localtime(timestamp)
    styleTime = time.strftime(str(time_format), timeArray)
    return styleTime


# 获取合集内所有文章标题、链接、发布时间、ID等信息
def get_all_info(url, output_dir_path):
    """
    url：合集链接
    output_dir_path：存储文章信息的文件所在文件夹
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
    }

    # 先获取最新文章ID
    res = requests.get(url, headers)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text)
    firstIdElem = soup.select('li')[0]
    first_id = firstIdElem.getText('data-msgid')  # 合集页面里排在第一位的文章id

    # 网络抓包获取的
    urll = 'https://mp.weixin.qq.com/mp/appmsgalbum'
    # 目前仅自动获取first_id, 其他参数手动提供，后续改进为全部自动获取
    params = {
        'action': 'getalbum',
        '_biz': 'MzIzNTQ4ODg4OA==',
        'album_id': '2206783352551063553',
        'count': '50',
        'begin_msgid': first_id,
        'begin_itemidx': '1',
        'uin': '',
        'key': '',
        'pass_ticket': '',
        'wxtoken': '',
        'devicetype': '',
        'clientversion': '',
        '_biz': 'MzIzNTQ4ODg4OA==',
        'appmsg_token': '',
        'x5': '0',
        'f': 'json',
    }
    data_json = requests.get(urll, headers, params).json()

    album_resp = data_json.get('getalbum_resp')
    article_list = album_resp.get('article_list')
    msg_cnt = len(article_list)  # 爬取到的文章数量
    for dic in article_list:
        pos_num = dic['pos_num']
        title = dic['title']
        url = dic['url']
        create_time = dic['create_time']
        msgid = dic['msgid']

        # 这里应该将获取的数据写到csv文件中或者数据库里
        # 我暂时先写到data.txt文件里
        file_path = os.path.join(output_dir_path, 'data.txt')
        # 写入的文章不含最新的第一篇，也可能不包含最后的几篇
        with open(file_path, 'a+', encoding='utf-8') as f:
            f.write(f'序列：{pos_num}\n文章标题：{title}\n发布时间：{create_time}\n链接：{url}\nID：{msgid}\n\n')

    # 检查最后一篇文章的pos_num是否为1来判断爬取的文章是否齐全
    # 不为1则从new_id接着爬取，这里仅爬取两次，改进版可以通过循环检测爬取
    if article_list[msg_cnt-1]['pos_num'] != 1:
        new_id = article_list[msg_cnt-1]['msgid']
        first_id = new_id
        data_json = requests.get(urll, headers, params).json()

        album_resp = data_json.get('getalbum_resp')
        article_list = album_resp.get('article_list')
        msg_cnt += len(article_list)  # 总共爬取到的文章数量
        for dic in article_list:
            pos_num = dic['pos_num']
            title = dic['title']
            url = dic['url']
            create_time = dic['create_time']
            msgid = dic['msgid']

            with open(file_path, 'a+', encoding='utf-8') as f:
                f.write(f'序列：{pos_num}\n文章标题：{title}\n发布时间：{create_time}\n链接：{url}\nID：{msgid}\n\n')


# 替换图片src、元素，否则图片无法显示
def replace_html_tags(html):
    # 替换图片标签属性
    html = html.replace(
        "data-src", "src").replace('style="visibility: hidden;"', "")

    soup = bs4.BeautifulSoup(html, 'html.parser')

    # 删除评论和投票的html标签
    if soup.iframe:
        soup.iframe.decompose()

    # 用模板格式化
    comments = soup.findAll("img", {"class": "like_comment_pic"})
    styles = soup.find_all('style')
    content = soup.find('div', id='page-content')
    fmt_html = T_HTML.format(style=styles[0].string, content=content)
    # cnt_html = fmt_html.replace(comments[0].attrs['src'], '')

    return html


# 获取文章标题
# 需要借助爬虫提取文章标题
# 可以改进：无需每篇文章单独爬取，可以一次性获取的
def get_title(res):
    soup = bs4.BeautifulSoup(res.text)

    # 标题
    titleElem = soup.select('#activity-name')
    title = titleElem[0].getText().split('\n')[2]

    # 公众号名称
    wechatNameElem = soup.select('#js_name')
    wechatName = wechatNameElem[0].getText().split()[0]

    # 发布时间
    # 正则表达式，截取需要的时间戳
    # ![](https://img.arctee.cn/one/202207021312051.png)
    match = re.search(r'\{e\(0,(.*),0,document.getElementById\("publish_time"\)\)', res.text, re.S)
    if match:
        # print(match.group(1))
        timestamp = int(match.group(1).split('"')[1])
    publishTime = timestamp_convert_localdate(timestamp)

    pdfTitle = wechatName + '-' + publishTime + '-' + title
    return pdfTitle


def print_info(pdfTitle, output_path):
    print('#' * 100)
    if 'img' in output_path:
        print("Img文章已生成！")
    else:
        print("文章已生成！")
    print("标题：" + pdfTitle)
    print("地址：" + output_path)
    print('#' * 100)
    # print('\n')


# 通知文章更新状态（简易版）
# 首先在存储pdf文档的文件夹下手动新建一个文档cnt.txt，内容为空
def notice_new_title(title_num, output_dir_path):
    """
    仅支持单项操作，如只删除了，或只更新了
    如果既删除又更新了，该函数会出错
    因为该函数思想是：将当前合集内文章数量与上次执行该函数保存的数量进行对比，来通知文章更新状态
    升级版其实也简单，只要从文章发布时间或者文章链接入手即可
    """
    file_path = os.path.join(output_dir_path, 'cnt.txt')
    mkfile(file_path)

    with open(file_path, 'r+', encoding='utf-8') as f:
        # 先读取文件, 将文件指针指向开始，并使用truncate()清除所有内容
        cnt = f.read()
        f.seek(0)
        f.truncate()

        if cnt == '':
            cnt = 0
        cnt = int(cnt)
        if title_num > cnt:
            print("## 最近更新了 %d 篇文章，敬请享用~~~" % (title_num-cnt))
        elif title_num == cnt:
            print("## 未更新文章，走吧。。。")
        else:
            print("## 竟然删除了 %d 篇文章，有啥不可告人的秘密？？？" % (cnt-title_num))

        # 更新 cnt
        f.write(str(title_num))
        f.seek(0)


# 生成pdf
def wechat2pdf(url, category, dir_path="D:\Media\Desktop\wechat2pdf"):
    """
    url：微信公众号合集链接
    category：分类子文件夹
    dir_path：主文件夹，有默认值
    """
    # 新建文件夹
    output_dir_path = os.path.join(dir_path, category)
    # mkdir(output_dir_path)
    """
    以递归的方式创建文件夹，如果dir_1不存在，就先创建dir_1，而后递归创建剩余的文件夹，这样就不存在FileNotFoundError；
    如果想要创建的目录已经存在，设置exist_ok = True，就不会引发FileExistsError
    """
    os.makedirs(output_dir_path, exist_ok=True)

    link_list = get_all_links()
    title_num = len(link_list)  # 文章数量

    for link in link_list:
        res = requests.get(link)
        res.raise_for_status()

        # 转换html
        cnt_html = replace_html_tags(res.text)
        # 设置标题
        pdfTitle = get_title(res)

        # 设置文章存储路径
        output_path = os.path.join(output_dir_path, pdfTitle + '.pdf')  # 无图片
        output_path2 = os.path.join(output_dir_path, pdfTitle + '(img).pdf')  # 有图片

        # 利用pdfkit开始生成pdf文档
        pdfkit.from_url(url, output_path)  # 无图片
        print_info(pdfTitle, output_path)

        try:
            pdfkit.from_string(cnt_html, output_path2)  # 有图片
        except IOError:
            pass
        print_info(pdfTitle, output_path2)

    print("本次共生成 %d 篇文章！\n" % title_num)
    # 通知文章更新状态
    notice_new_title(title_num, output_dir_path)



if __name__ == "__main__":
    # url：合集链接
    url = 'https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIzNTQ4ODg4OA==&action=getalbum&album_id=1689138318304690182&scene=173&from_msgid=2247487438&from_itemidx=1&count=3&nolastread=1#wechat_redirect'
    category = '孟岩投资实证2021'  # 类别，根据类别自动创建子文件夹
    dir_path = "D:\Media\Desktop\wechat2pdf"  # 主文件夹路径
    wechat2pdf(url, category, dir_path)

