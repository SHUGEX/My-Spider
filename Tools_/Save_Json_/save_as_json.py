import json


def xsg_save_data(xsg_title_list, xsg_date_list,
                  xsg_clicks_list, xsg_content_list, xsg_checker_list, xsg_j, xsg_mysql):
    """存储数据"""

    print(f"\n\033[1;36m曲阜师大学校要闻 第{xsg_j + 1}页15条新闻解析完毕 准备下载...\033[0m\n")

    for xsg_i in range(len(xsg_title_list)):

        xsg_mysql.execute(
            'insert into xsg_news(id,xsg_title_list, xsg_date_list,xsg_clicks_list, '
            'xsg_content_list, xsg_checker_list) values(0,("%s"),("%s"),("%s"),("%s"),("%s"))'
            % (xsg_title_list[xsg_i], xsg_date_list[xsg_i], xsg_clicks_list[xsg_i],
               xsg_content_list[xsg_i], xsg_checker_list[xsg_i]))

        with open(f'曲阜师大学校要闻.json', 'a', encoding="utf-8") as f:
            print(f"\n新闻{xsg_i + 1 + xsg_j * 15}；\n\t\"{xsg_title_list[xsg_i]}\""
                  f"--{xsg_date_list[xsg_i]}"
                  f"--浏览{xsg_clicks_list[xsg_i]}次 审核:{xsg_checker_list[xsg_i]} 下载中...\n")
            dict_ = {
                "新闻标题": xsg_title_list[xsg_i],
                "发布时间": xsg_date_list[xsg_i],
                "浏览次数": xsg_clicks_list[xsg_i],
                "新闻正文": xsg_content_list[xsg_i],
                "审核": xsg_checker_list[xsg_i]
            }
            json_data = json.dumps(dict_, ensure_ascii=False) + ',\n'
            f.write(json_data)

    print(f"\n\033[1;36m曲阜师大学校要闻 第{xsg_j + 1}页15条新闻 已下载...\033[0m", end="  ")