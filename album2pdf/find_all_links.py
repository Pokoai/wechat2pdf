#! python
# find_all_links.py - 通过合集链接找到该合集下所有文章的ID、标题、链接、序列号、发布时间等信息

"""
功能基本实现 2022-7-4

"""

import requests, bs4
import re
import os


# 单独爬取合集页面里第一篇（倒序）文章ID、标题、链接、序列号、发布时间
# 顺便爬取微信公众号名称、合集名称
# 将以上内容写入文件data.txt中，后续可改为写入数据库中或csv
# 同时返回第一篇文章id、data.txt文件夹路径、合集文章数量、公众号唯一标识_biz
def get_first_msg_info(album_url, output_dir_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
    }

    res = requests.get(album_url, headers)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text)

    # 获取微信公众号名称
    wechat_name_elem = soup.select('.album__author-name')
    wechat_name = wechat_name_elem[0].getText()

    # 获取合集名称
    album_name_elem = soup.select('#js_tag_name')
    album_name = album_name_elem[0].getText().replace('#', '')

    # 获取合集文章数量
    album_num_elem = soup.select('.album__num')
    album_num = int(album_num_elem[0].getText().split('个')[0])  # 27个内容，提取27

    # 获取第一篇文章信息
    first_elem = soup.select('li')[0]
    first_id = first_elem.get('data-msgid')
    print(f'\nfirst_id：{first_id}\n')
    pos_num = first_elem.get('data-pos_num')
    if pos_num == '':
        pos_num = str(album_num)  # 有的合集文章没有设置pos_num属性
    title = first_elem.get('data-title')
    link = first_elem.get('data-link')
    # 从link里提取_biz
    _biz = re.search(r'__biz=(\S+)&mid', link).group(1)
    print(f'_biz：{_biz}')

    # 获取第一篇文章发布时间
    # 发布时间是用 JavaScript 渲染后显示的，要用正则表达式截取时间戳
    # ![](https://img.arctee.cn/one/202207021312051.png)
    publish_time = 0  # 默认值
    res = requests.get(link, headers)
    res.raise_for_status()
    match = re.search(r'\{e\(0,(.*),0,document.getElementById\("publish_time"\)\)', res.text, re.S)
    if match:
        publish_time = int(match.group(1).split('"')[1])

    # 根据合集名称确定路径
    album_path = os.path.join(output_dir_path, album_name)  # 合集文件夹路径
    os.makedirs(album_path, exist_ok=True)
    file_path = os.path.join(album_path, 'data.txt')  # data.txt路径

    # 写入第一篇文章的信息
    with open(file_path, 'w', encoding='utf-8') as f:
        # f.write(f'公众号名称：{wechat_name}\n合集名称：{album_name}\n合集本地路径：{album_path}\n\n'
        #         f'序列：{pos_num}\n文章标题：{title}\n发布时间：{publish_time}\n'
        #         f'链接：{link}\nID：{first_id}\n\n')

        f.write(f'序列：{pos_num}\n文章标题：{title}\n发布时间：{publish_time}\n'
                f'链接：{link}\nID：{first_id}\n\n')

    return first_id, file_path, album_num, _biz


# 设置requests.get()的参数params
# first_id：首篇文章id，合集主页爬取所得
# album_id：合集id，提取自手动提供的合集链接中
# _biz：唯一用户标识，合集主页爬取所得
def set_params(first_id, album_id, _biz):
    params = {
        'action': 'getalbum',
        '_biz': _biz,
        'album_id': album_id,
        'count': '20',
        'begin_msgid': str(first_id),
        'begin_itemidx': '1',
        'uin': '',
        'key': '',
        'pass_ticket': '',
        'wxtoken': '',
        'devicetype': '',
        'clientversion': '',
        '_biz': _biz,
        'appmsg_token': '',
        'x5': '0',
        'f': 'json',
    }
    return params


# 获取合集内所有文章标题、链接、发布时间、ID等信息
# requests.get(url=url, headers=headers, params=params)的响应信息不包含第一篇文章，所有需要单独爬取
def get_all_info(album_url, album_id, output_dir_path):
    """
    album_url：合集链接
    output_dir_path：存储文章信息的文件所在文件夹
    """
    # 先将第一篇文章信息写入文件中，并获得其id和合集名称
    first_id, file_path, album_num, _biz = get_first_msg_info(album_url, output_dir_path)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
    }
    # 通过网络抓包获取的url
    url = 'https://mp.weixin.qq.com/mp/appmsgalbum'

    msg_cnt = 0  # 每一次爬取到的文章数量
    msg_num = 1  # 总共爬取到的文章数量，第一篇已经单独爬取过，所以起始为1
    pos_max_num = album_num - 1  # 第二篇文章的序列号
    while True:
        params = set_params(first_id, album_id, _biz)
        data_json = requests.get(url=url, headers=headers, params=params).json()
        # 解析返回的json数据
        album_resp = data_json.get('getalbum_resp')
        article_list = album_resp.get('article_list')
        for dic in article_list:
            title = dic['title']
            link = dic['url']
            publish_time = dic['create_time']
            msgid = dic['msgid']
            # 有的合集文章没有设置pos_num属性，需要自己手动设置
            if 'pos_num' in dic:
                pos_num = dic['pos_num']
            else:
                pos_num = str(pos_max_num)
                pos_max_num -= 1

            msg_cnt += 1

            # 写入的文章不含最新的第一篇，也可能不包含最后的几篇
            with open(file_path, 'a+', encoding='utf-8') as f:
                f.write(f'序列：{pos_num}\n文章标题：{title}\n发布时间：{publish_time}\n链接：{link}\nID：{msgid}\n\n')

        # 如果本次最后一篇文章的pos_num为1则跳出循环
        # 该退出循环条件有问题，因为某些合集pos_num为空
        # 现换为 msg_cnt == album_num 作为退出条件，album_num直接通过html爬取获得
        # if int(article_list[msg_cnt-1]['pos_num']) == 1:
        msg_num += msg_cnt
        if msg_num == album_num:
            break
        # 每次响应最多只返回20篇文章的信息，所以要找到本次响应的最后一篇文章，以它的id作为下一次起始id
        first_id = article_list[msg_cnt-1]['msgid']  # 更新first_id
        msg_cnt = 0  # msg_cnt需要清零，为下次循环准备

    return file_path


if __name__ == "__main__":
    # album_url = 'https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIzNTQ4ODg4OA==&action=getalbum&album_id=2206783352551063553&scene=173&from_msgid=2247487451&from_itemidx=1&count=3&nolastread=1#wechat_redirect'
    album_url = 'https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIzNTQ4ODg4OA==&action=getalbum&album_id=1323674556309241856&scene=173&from_msgid=2247485047&from_itemidx=1&count=3&nolastread=1#wechat_redirect'

    output_dir_path = "D:\Media\Desktop\wechat2pdf"  # 主文件夹路径
    album_id = 2206783352551063553
    get_all_info(album_url, album_id, output_dir_path)

    print("Done!")