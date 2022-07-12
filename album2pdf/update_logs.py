#! python
# update_logs.py - 自动生成更新日志文档 update_logs.txt

import os, re, time

# 合集名称数据
album_name_list = ["孟岩投资实证（2022）", "日记", "长赢指数投资计划"]

# 最外层文件夹地址
dir_path = "D:\Media\Desktop\wechat2pdf"
# 日志文件地址
logs_path = os.path.join(dir_path, 'update_logs.txt')


# 读取日志内容，返回各合集文章历史数量
def read_logs():
    # 读取日志文件内容
    with open(logs_path, encoding='utf-8') as logs_f:
        logs_str = logs_f.read()
        mengyan_num = int(re.search(r'孟岩投资实证（2022）：(\d+)，', logs_str).group(1))  # 孟岩投资实证（2022）文章数量
        ediary_num = int(re.search(r'E大日记：(\d+)，', logs_str).group(1))              # E大日记文章数量
        efache_num = int(re.search(r'E大投资计划：(\d+)，', logs_str).group(1))           # E大发车文章数量

    return mengyan_num, ediary_num, efache_num


# 全局变量，存储文件历史数量
history_nums = read_logs()


# 更新日志内容
logs = []  # 暂存日志字符串到该列表中
for i in range(len(album_name_list)):
    # 合集数据库地址
    db_path = os.path.join(dir_path, album_name_list[i], 'data.txt')

    with open(db_path, encoding='utf-8') as f:
        data_str = f.readline()
        # 获取第一个序列号，即文章最新数量
        max_num = int(re.search(r'序列：(\d+)\s', data_str).group(1))

        # 最新数量与日志数量相减
        update_num = max_num - history_nums[i]

        # 判断更新状态
        if update_num > 0:
            update_str = '，更新' + str(update_num) + '篇\n'
        elif update_num == 0:
            update_str = '，未更新'
        else:
            update_str = '，删除' + str(abs(update_num)) + '篇\n'

        # 拼接起来，最终要实现效果：「孟岩投资实证（2022）：28，更新4篇」
        log_new_str = album_name_list[i] + '：' + str(max_num) + update_str
        # 先加入到日志列表中，等全部加入后，再一次性写入到日志文件中，实现更新日志的效果
        logs.append(log_new_str)


# 将新的日志内容写入日志文件
with open(logs_path, 'w', encoding='utf-8') as f:
    # 先写入今天日期
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    f.write(current_time + '\n\n')

    # 写入日志内容
    for log in logs:
        f.write(log + '\n')