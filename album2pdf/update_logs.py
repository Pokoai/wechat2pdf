#! python
# get_update_status.py - 自动生成更新日志文档 get_update_status.txt

import os, re, time

from album2pdf_v1 import mkfile


# 读取日志文件，获取合集文章历史数量
def read_logs(logs_path):
    # 若文件不存在即创建
    mkfile(logs_path)

    # 读取日志文件内容
    with open(logs_path, encoding='utf-8') as logs_f:
        logs_str = logs_f.read()

        # 因为要将日志文件的写入模式由覆盖改为添加，所以会有多个匹配项，但是re.search好像只匹配第一个，那正好不用修改了
        # 查资料所得：re.search()方法扫描整个字符串，并返回第一个成功的匹配。如果匹配失败，则返回None
        # 这里总结下：re.search()只匹配第一个找到的，re.findall()匹配所有找到的并返回一个列表
        match1 = re.search(r'孟岩投资实证（2022）：共(\d+)篇，', logs_str)
        if match1:
            mengyan_nums = int(match1.group(1))  # 孟岩投资实证（2022）文章数量
        else:
            mengyan_nums = 0  # 初始为0

        match2 = re.search(r'日记：共(\d+)篇，', logs_str)
        if match2:
            ediary_nums = int(match2.group(1))  # E大日记文
        else:
            ediary_nums = 0  # 初始为0

        match3 = re.search(r'长赢指数投资计划：共(\d+)篇，', logs_str)
        if match3:
            efache_nums = int(match3.group(1))  # E大发车文章数量
        else:
            efache_nums = 0  # 初始为0

    return ediary_nums, efache_nums, mengyan_nums


# 今日更新标志位
    # 因为一天运行5次，每次都会覆盖掉日志文件，但我只会晚上看1次状态，那么只要这5次中有一次更新过，就要记录下来，表示今天更新过
    # 另外因为公众号限制，每天只能发布一篇文章，那么只要更新过，即只更新了一篇
    # 我想在日志文件中记录下今天哪些合集更新了文章或者删除了文章，以便通知大家
    # 写到这里，我有了想法：1. 简单点：只在日志文件中说明今天是否更新，而哪个合集更新了这个信息暂时不管，自己去对比已下载文章和历史文章，人工操作有点麻烦；
    # 2. 在日志文件中记录下所有信息：今天谁更新了，但是一天运行5次，我就得考虑如何去迭代这个通知信息，写代码有点麻烦；（以后有时间可以思考思考）
    # 3. 发挥日志文件的正常功能：即使用添加写入，而非覆盖写入。这就要改变 正则表达式从日志中提取最新文章数量的代码，打算每次在文件开头添加写入。代码不复杂；
    # 综上所述，采用第3种方案开搞。


# 读取各合集数据库文件，与日志文件对比，获取更新状态
def get_update_status(output_path, album_name_list, history_nums):
    logs = []  # 暂存新日志字符串到该列表中
    # print(len(album_name_list))

    # 合集数量
    album_num = len(album_name_list)
    # 合集更新标志位，默认未更新为0
    update_flg = [0 for i in range(album_num)]
    # 更新文章总数
    update_cnt = 0

    for i in range(album_num):
        # 数据库地址
        db_path = os.path.join(output_path, album_name_list[i], 'data.txt')
        with open(db_path, encoding='utf-8') as f:
            db_str = f.readline()

            # 获取第一个序列号，即文章最新数量
            album_post_nums = int(re.search(r'序列：(\d+)\s', db_str).group(1))
            # 最新数量与历史数量之差即为更新数量
            update_num = album_post_nums - history_nums[i]  # 这里需要i

            # 判断更新状态
            if update_num > 0:
                update_str = '，更新 ' + str(update_num) + ' 篇\n'
                update_flg[i] = 1  # 有文章更新，标志位置1
                update_cnt += update_num
            elif update_num == 0:
                update_str = '，未更新\n'
            else:
                update_str = '，删除 ' + str(abs(update_num)) + ' 篇\n'

            # 拼接起来，最终要实现效果：「孟岩投资实证（2022）：共28篇，更新 4 篇」
            log_new_str = album_name_list[i] + '：共' + str(album_post_nums) + '篇' + update_str
            # 先加入到日志列表中，等全部加入后，再一次性写入到日志文件中，实现更新日志的效果
            logs.append(log_new_str)
    # print(logs)

    # return的缩进位置要注意，应放在for外面，否则一次循环就结束了
    return logs, update_flg, update_cnt


# 将更新状态写入日志文件中
def update_logs(logs_path, output_path, album_name_list):
    print("\n##################### 开始更新：日志文件 #####################")
    # 读取日志文件，获取合集文章历史数量
    history_nums = read_logs(logs_path)  # ediary_nums, efache_nums, mengyan_nums

    # 获取更新状态
    logs, update_flg, update_cnt = \
        get_update_status(output_path, album_name_list, history_nums)

    # 获取当前时间
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    # 写入日志文件
    with open(logs_path, 'r+', encoding='utf-8') as f:
        # 从文件头部插入
        old = f.read()
        f.seek(0)

        # 先写入今天日期
        f.write(current_time + '\n\n')
        # 再写入更新日志
        for log in logs:
            f.write(log + '\n')
        # 写入原内容
        f.write('\n' + old)
    print("\n##################### 完成更新：日志文件 #####################")

    return update_flg, update_cnt  # 将更新标志位、更新总数传递下去




if __name__ == "__main__":
    album_url_dict = {
        '日记': "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIwMTIzNDMwNA==&action=getalbum&album_id=2461687967875416065&scene=173&from_msgid=2653411356&from_itemidx=1&count=3&nolastread=1#wechat_redirect",
        '长赢指数投资计划': "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIwMTIzNDMwNA==&action=getalbum&album_id=2467166481575985152&scene=173&from_msgid=2653411345&from_itemidx=1&count=3&nolastread=1#wechat_redirect",
        '孟岩投资实证（2022）': "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIzNTQ4ODg4OA==&action=getalbum&album_id=2206783352551063553&scene=173&from_msgid=2247487451&from_itemidx=1&count=3&nolastread=1#wechat_redirect",

    }
    # 合集名称数据
    album_name_list = list(album_url_dict.keys())
    # 最外层文件夹地址
    output_path = "D:\Media\Desktop\wechat2pdf"
    logs_path = os.path.join(output_path, 'update_logs.txt')


    update_logs(logs_path, output_path, album_name_list)
    print("日志更新完成!")