#! python
# update_logs.py - 自动生成更新日志文档 update_logs.txt

import os, re, time

from album2pdf_v1 import mkfile


# 读取日志内容，获取各合集文章历史数量
def read_logs(logs_path):
    # 若文件不存在即创建
    mkfile(logs_path)

    # 读取日志文件内容
    with open(logs_path, encoding='utf-8') as logs_f:
        logs_str = logs_f.read()

        match1 = re.search(r'孟岩投资实证（2022）：共(\d+)篇，', logs_str)
        if match1:
            mengyan_num = int(match1.group(1))  # 孟岩投资实证（2022）文章数量
        else:
            mengyan_num = 0  # 初始为0

        match2 = re.search(r'日记：共(\d+)篇，', logs_str)
        if match2:
            ediary_num = int(match2.group(1))  # E大日记文
        else:
            ediary_num = 0  # 初始为0

        match3 = re.search(r'长赢指数投资计划：共(\d+)篇，', logs_str)
        if match3:
            efache_num = int(match3.group(1))  # E大发车文章数量
        else:
            efache_num = 0  # 初始为0

    return ediary_num, efache_num, mengyan_num


# 更新日志内容
def update_logs(dir_path, album_name_list):
    logs = []  # 暂存日志字符串到该列表中
    # print(len(album_name_list))
    # 日志文件地址
    logs_path = os.path.join(dir_path, 'update_logs.txt')
    # 文件历史数量
    history_nums = read_logs(logs_path)
    # print(history_nums)

    for i in range(len(album_name_list)):
        # 合集数据库地址
        db_path = os.path.join(dir_path, album_name_list[i], 'data.txt')

        with open(db_path, encoding='utf-8') as f:
            data_str = f.readline()
            # 获取第一个序列号，即文章最新数量
            max_num = int(re.search(r'序列：(\d+)\s', data_str).group(1))

            # 最新数量与历史数量之差
            update_num = max_num - history_nums[i]

            # 判断更新状态
            if update_num > 0:
                update_str = '，更新 ' + str(update_num) + ' 篇\n'
            elif update_num == 0:
                update_str = '，未更新\n'
            else:
                update_str = '，删除 ' + str(abs(update_num)) + ' 篇\n'

            # 拼接起来，最终要实现效果：「孟岩投资实证（2022）：共28篇，更新 4 篇」
            log_new_str = album_name_list[i] + '：共' + str(max_num) + '篇' + update_str
            # 先加入到日志列表中，等全部加入后，再一次性写入到日志文件中，实现更新日志的效果
            logs.append(log_new_str)
    # print(logs)

    return logs  # return的缩进位置要注意，应放在for外面，否则一次循环就跳出了


# 将新的日志内容写入日志文件
def write_to_logs(dir_path, album_name_list):
    # 日志文件地址
    logs_path = os.path.join(dir_path, 'update_logs.txt')

    # 获取要更新的内容
    logs = update_logs(dir_path, album_name_list)
    # print(logs)

    # 获取当前时间
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    # 写入文件
    with open(logs_path, 'w', encoding='utf-8') as f:
        # 先写入今天日期
        f.write(current_time + '\n\n')
        # 再写入更新日志
        for log in logs:
            f.write(log + '\n')
            # print("谢谢谢\n")


if __name__ == "__main__":
    album_url_dict = {
        '日记': "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIwMTIzNDMwNA==&action=getalbum&album_id=2461687967875416065&scene=173&from_msgid=2653411356&from_itemidx=1&count=3&nolastread=1#wechat_redirect",
        '长赢指数投资计划': "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIwMTIzNDMwNA==&action=getalbum&album_id=2467166481575985152&scene=173&from_msgid=2653411345&from_itemidx=1&count=3&nolastread=1#wechat_redirect",
        '孟岩投资实证（2022）': "https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzIzNTQ4ODg4OA==&action=getalbum&album_id=2206783352551063553&scene=173&from_msgid=2247487451&from_itemidx=1&count=3&nolastread=1#wechat_redirect",

    }
    # 合集名称数据
    album_name_list = list(album_url_dict.keys())
    # 最外层文件夹地址
    dir_path = "D:\Media\Desktop\wechat2pdf"

    write_to_logs(dir_path, album_name_list)

    print("日志更新完成!")