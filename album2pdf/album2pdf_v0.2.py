#! python
# album2pdf_v0.2.py - 将微信公众号合集文章批量导出为pdf文档

"""
最新问题：
1. 合集页面的文章列表html是动态显示的，打开网页后只会显示前10条，
只有混动滚轮往下翻才会触发显示更多条信息。
所以目前采用的方法仅能爬取10条记录。


初步版本：
合集链接手动提供

后续改进：
1. 自动获取公众号全部合集链接，然后手动选取感兴趣的合集
2. 用 pyqt5 封装起来
"""

import pdfkit
import requests, bs4
import os, sys
import re, time

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
# 采用 os.makedirs 可以递归
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


# 获取合集内所有文章链接
# 有问题：只能爬取前10篇文章链接
def get_all_links(url):
    """
    url为合集链接
    """
    link_list = []

    res = requests.get(url)
    res.raise_for_status()
    # with open('./temp.txt', 'w') as f:
    #     f.write(res.text)
    soup = bs4.BeautifulSoup(res.text)
    linkElems = soup.select('li')
    # album__list-item js_album_item js_wx_tap_highlight wx_tap_cell
    for i in range(len(linkElems)):
        link_list.append(linkElems[i].get('data-link'))
    # print(len(linkElems))
    return link_list


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

    link_list = get_all_links(url)
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
    url = 'https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIzNTQ4ODg4OA==&action=getalbum&album_id=2206783352551063553&scene=173&from_msgid=2247487451&from_itemidx=1&count=3&nolastread=1#wechat_redirect'
    category = '孟岩投资实证2021'  # 类别，根据类别自动创建子文件夹
    dir_path = "D:\Media\Desktop\wechat2pdf"  # 主文件夹路径
    wechat2pdf(url, category, dir_path)

