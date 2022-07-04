# wechat2pdf
> 最终目标：将微信公众号文章批量导出为pdf

工具：python + pdfkit（wkhtmltopdf） + requests + BeautifulSoup4 + re

**初步版本：**
1. 文章链接手动提供
2. 未实现批量功能，仅完成单篇文章的导出

**后续改进：**
1. 仅提供公众号名称或其他信息，自动获取公众号全部历史文章链接；
2. 将文章标题、链接等信息存储到 csv 文件或数据库中；


## album2pdf
> 将微信公众号合集文章批量导出为pdf文档

**后续改进：**
1. 仅提供公众号名称或其他信息，实现自动获取公众号全部合集链接，然后手动选取感兴趣的合集；
2. 查询文章更新状态（简易版），如果未更新则不执行转pdf程序，并且通知更新了几篇文章/未更新/删除了几篇文章等信息。目前思路是比较 data.txt 文档内容来判断更新状态，更简易版是直接比较最新文章的 pos_num 与已转换文章的 pos_num，来判断更新状态；
3. 用 pyqt5 封装起来，便于信息输入和转换结果展示；
4. 多线程，提高采集速度；（目前50篇文章大概需要92秒）
5. 打包成 .exe 可执行程序，可分发给任何人使用；

目前的功能我自己用用已经够了，时间有限，不知后续何时抽得出时间来完善。

有兴趣的朋友可以参与进来，一同完成后续改进计划。
