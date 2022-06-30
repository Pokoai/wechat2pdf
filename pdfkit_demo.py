import pdfkit
import os, sys

url = "https://arctee.cn"

file_name = '1223'

# 获取当前文件所在目录绝对路径
cur_file_dir = os.path.abspath(__file__).rsplit('\\', 1)[0]
output_path = os.path.join(cur_file_dir, file_name + '.pdf')

pdfkit.from_url(url, output_path)