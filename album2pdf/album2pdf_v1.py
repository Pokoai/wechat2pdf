#! python
# album2pdf_v1.py - 将微信公众号合集文章批量导出为pdf文档

"""
初步版本：
合集链接手动提供

后续改进：
1. 自动获取公众号全部合集链接，然后手动选取感兴趣的合集
2. 用 pyqt5 封装起来
3. 多线程，提高采集速度
4. 打包成 .exe 可执行程序
"""

import pdfkit
import requests, bs4
import os, time, re

from find_all_links import get_all_info


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


# 替换图片src、元素，否则图片无法显示
def replace_html_tags(html):
    # 替换图片标签属性
    # 这种替换方式太过耗时，后续改进可考虑换其他方式
    # data-src替换为src 有时候返回的正文被隐藏了，将hidden去掉
    html = html.replace(
        "data-src", "src").replace('style="visibility: hidden;"', "")
    # soup = bs4.BeautifulSoup(html)
    # # 选择正文（去除javascript等）
    # html = soup.select('div#img-content')[0]


    # soup = bs4.BeautifulSoup(html, 'html.parser')
    #
    # # 删除评论和投票的html标签
    # if soup.iframe:
    #     soup.iframe.decompose()

    # # 用模板格式化
    # comments = soup.findAll("img", {"class": "like_comment_pic"})
    # styles = soup.find_all('style')
    # content = soup.find('div', id='page-content')
    # fmt_html = T_HTML.format(style=styles[0].string, content=content)
    # cnt_html = fmt_html.replace(comments[0].attrs['src'], '')
    return html


# 终端实时输出转换信息
def print_info(pdf_title, msg_path):
    print('#' * 100)
    if 'img' in msg_path:
        print("Img文章已生成！")
    else:
        print("文章已生成！")
    print("标题：" + pdf_title)
    print("地址：" + msg_path)
    print('#' * 100)
    # print('\n')


# 查询文章更新状态（简易版），如果未更新则不执行转pdf程序
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
def wechat2pdf(album_url, output_dir_path="D:\Media\Desktop\wechat2pdf"):
    """
    album_url：微信公众号合集链接
    dir_path：主文件夹，有默认值
    """
    start_time = time.time()

    # 通知合集文章更新状态
    # notice_new_title(title_num, output_dir_path)

    file_str= ''
    file_path = get_all_info(album_url, album_id, output_dir_path)
    # file_path = "D:\Media\Desktop\wechat2pdf\孟岩投资实证（2022）\data.txt"
    album_path = os.path.dirname(file_path)
    with open(file_path, encoding='utf-8') as f:
        file_str = f.read()

    # 匹配序列号
    pos_num_list = re.findall(r'序列：(\d+)\s', file_str)
    # 匹配标题
    title_list = re.findall(r'文章标题：(.+)\s', file_str)
    # 匹配发布时间
    publish_time_list = re.findall(r'发布时间：(\d+)\s', file_str)
    # 匹配链接
    link_list = re.findall(r'链接：(\S+)\s', file_str)

    msg_num = len(link_list)  # 文章数量
    for i in range(msg_num):
        # 设置文章路径
        publish_time = timestamp_convert_localdate(int(publish_time_list[i]))
        title = pos_num_list[i] + '.' + title_list[i] + '-' + publish_time
        msg_path = os.path.join(album_path, title + '.pdf')
        msg_path2 = os.path.join(album_path, title + '(img).pdf')  # 带图片

        # requests加载文章
        res = requests.get(link_list[i])
        res.raise_for_status()
        # 转换html
        cnt_html = replace_html_tags(res.text)

        # 利用pdfkit开始生成pdf文档
        pdfkit.from_url(link_list[i], msg_path)  # 无图片版
        print_info(title, msg_path)
        try:
            pdfkit.from_string(cnt_html, msg_path2, options=PDF_OPTIONS)  # 有图片版
        except IOError:
            pass
        print_info(title, msg_path2)

    end_time = time.time()
    all_time = int(end_time - start_time)
    print(f"\n本次共生成 {msg_num} 篇文章！")
    print(f"耗时：{all_time}秒")


if __name__ == "__main__":
    album_url = input("请输入合集链接（不带双引号）：")
    # output_dir_path = input("请输入主文件夹路径（不带双引号）：")
    # album_url = 'https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIzNTQ4ODg4OA==&action=getalbum&album_id=1511849982641913857&scene=173&from_msgid=2247485557&from_itemidx=1&count=3&nolastread=1#wechat_redirect'
    output_dir_path = "D:\Media\Desktop\wechat2pdf2"  # 主文件夹路径

    # 通过链接提取合集id
    album_id = re.search(r'album_id=(\d+)&', album_url).group(1)
    print(f'\nalbum_id：{album_id}\n')

    wechat2pdf(album_url, output_dir_path)
