# 2019-nCoV-data-push-via-IFTTT


## 概述

2020 年初，新型冠状病毒以骇人的规模爆发。为了得到最新的数据信息，我决定开发这样的一个程序来通过 IFTTT 向我推送通知。

如有意，欢迎 fork 此仓库并改动来获得属于你自己的，更优化、客制化的推送服务

在此感谢我的朋友 [@GZTime](http://blog.gztime.cc/) ，因为代码的部分内容受他的项目启发，他是一名优秀的开发者。

如果配置遇到障碍，你也可以参考以下优秀的文章：[少数派](https://sspai.com/post/39243)、
[RealPython](https://realpython.com/python-bitcoin-ifttt/)。


## 特别说明

1. 笔者来自宁夏，因此订阅了宁夏、湖北数据；
2. 笔者是高三生，因此添加了高考倒计时；也正因如此，我没有时间、精力优化代码，其中的有的部分显得笨拙，还望各位自行调整，谢谢理解；
3. 代码从腾讯新闻获取数据，有时会出现数据错乱的情况（如前一天增加人数异常），你可以参考多个数据源；
4. 笔者将此程序运行在一台弹性云上，你也可以稍加配置后将它运行在树莓派、Linux服务器上；
5. 如果有更多问题，请通过邮件联系我：yuyanglee@hwstudio.site，谢谢！


## 使用方法

由于推送服务的高度客制化，你需要在配置推送前对代码做相关调整。

### IFTTT 端 Applet 配置
1. 在你的 IFTTT 账户中添加Applet
    - 将 "This" 设置为 "Webhooks" ，依据个人爱好设定 Event Name

    - 将 "That" 设置为 "Notifications" ，依据个人爱好选择 "notification" 或 "rich notification"

        在富文本通知中，你可以向通知（横幅）增加跳转链接、URLScheme 等功能

    - 设定你喜爱的 Message 内容

        请通过 "Add Ingredient" 将三个 "Value" 全部加入 Message ，其他内容可选。

    - 前往 Webhooks 页面中的 Documentaion 获取你的 Key

        **请妥善保存你的 key，如泄露可以重新申请，此处不再赘述方法。**

    - 在项目中的 "subscribed_urls.csv"中按照模板写入你的推送地址参数： Event Name 和 Key

        事实上，你可以在每一行输入一组推送地址的参数，程序将读取此文件、构建每个推送地址并批量推送通知。

2. 调整 IFTTT_push.py 代码

    下面列出了运行代码较重要的调整，请自行理解代码逻辑以完成更高级的升级。

    - 修改代码中的以下代码，将你需要的省（自治区、直辖市）名称写入 list

        程序会自动在获取到的数据中查询此 list 中数据。

        ```python
        area_requested = ['宁夏', '湖北']
        ```

    - 调整 `get_data()` 以客制化属于你的推送文本

        由于直接从解析的 json 中加载了数据，这部分代码可能较为繁杂。你可以自己对它进行优化使得代码简洁、灵活。

        **你也应该在 IFTTT_push_end.py 中调整相关内容。**
        
    - 调整 `IFTTT_push(push_text_1, push_text_2, silent_mode)`

        这段代码配置了一个 POST 请求。
            
        `push_text_x` 分别对应了你在 IFTTT 中配置的三个 value

        `silent_mode` 是一个布尔型变量，它决定是否启用静默模式，即是否将推送成功的通知输出
        
        `CEE_left` 计算了高考倒计时天数，你也可以按需修改。

        **值得注意的是，为了使得 json 中的内容包含`\n`，你需要在此使用`\\n`。**

        ```python
        def IFTTT_push(push_text_1, push_text_2, silent_mode):
            today    = datetime.date.today()
            CEE_left = (CEE_date - today).days

            push_val1_text = ...
            push_val2_text = ...
            push_val3_text = ...
            body = "..."
            headers = ...
        ```

        **你也应该在 IFTTT_push_end.py 中调整相关内容。**

        
    - 调整 `sub_doc_path` 来从任何位置读取数据
            这个字符串是你保存推送地址数据的 csv 文件地址。
    
    - 调整推送时间

        在主函数中，调整以下代码修改 apscheduler 的推送时间

        ```python
        trigger = CronTrigger(hour='*/1')
        ```
            
        例如，以上代码使程序在整点推送通知。

3. 运行程序
    - start.bat 文件将在前台运行程序
        推荐服务器使用
    - start_daemon.vbs 文件将在后台运行程序
    - stop.bat 文件将结束程序并发送程序下线推送
        **注意：这将清除后台所有 python 进程，如需定向结束进程请自行设置**

## 更新计划

如果条件允许，希望增加包括但不限于以下功能：

1. 调整数据处理逻辑，将省市数据先存储，再按需取用；
2. 在上一条完成的情况下，实现每个推送地址可以订阅不同的省市数据的服务；
3. 增加历史数据存储模块，保存更新数据；
4. 在上一条完成的情况下，通过训练模型或库完成函数拟合和未来数据预测，并加入推送内容。


## 后记

无论拟合的函数向我们展示怎样的峰值，无论SIR模型、SEIR模型的模拟告诉我们怎样的前景，无论药店的N95卖5块还是50块，我们都应该带着信心和理性看待此次疫情，应该从身边做起，宣传、运用相关知识，助力缓解、消灭疫情。

无论病毒将历史导向何处，我们终将笑着挺过去。愿这一切结束后，我们还能笑着在武汉街头，吃一碗热干面。