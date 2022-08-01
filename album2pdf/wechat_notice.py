#! python
# wechat_notice.py - 给多个群发送通知

import pywintypes # 务必加这一句，否则会报错"ImportError: DLL load failed while importing win32gui: 找不到指定的程序。"

from wxauto import *
import time, random



# 需要发送通知的微信群 ["微信群备注名"]
whos = ["E大孟大投资交流群upupup", ]

# 所有消息发送完毕后，给自己发送一个通知
end_notice_user = "文件传输助手"
end_notice_info = "微信群通知发送完成！"

# 需要发送的消息
# msg =
# file1 = "D:/Media/Desktop/img28.jpg"

def wechat_group_notice(msg):
    wx = WeChat()  # 获取当前微信客户端
    wx.GetSessionList()  # 获取会话列表

    # 换行消息
    message = "您好，公众号有新文章发布，请稍后去阿里云盘查收！\n\n"
    for log in msg:
        log += '\n'
        message += log
    # print(message)
    WxUtils.SetClipboard(message)  # 将内容复制到剪贴板，类似于Ctrl + C

    for who in whos:
        time.sleep(random.randint(5, 8))  # 随机等待10-20s

        wx.ChatWith(who)  # 打开聊天窗口
        # wx.Search(username) # 查找微信好友，不会在当前聊天栏滚动查找
        wx.SendClipboard()  # 发送剪贴板的内容，类似于Ctrl + V
        # wx.SendFiles(file1)  # 可发送多个文件

        print("发送成功：", who)

    print("全部发送完成")
    wx.ChatWith(end_notice_user)
    wx.SendMsg(end_notice_info)


if __name__ == "__main__":
    wechat_group_notice()