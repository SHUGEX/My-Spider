"""
一.创建表：
 create table hero(
     id int auto_increment primary key,
     name varchar(20) not null,
     age int default 0,
     sex varchar(20),
     score int
 )charset=utf8;

二.插入数据
insert into hero values
(0,'赵云',16,'male',97),
(0,'张飞',23,'male',95),;

--查询表的所有数据
select * from hero;


--给name取别名
--select name as '姓名' from hero;
--select name '姓名' from hero;


C:\ProgramData\MySQL\MySQL Server 8.0\Data\

                 1.   show databases;


                 2.     drop database 数据库名;    >> 彻底删除整个数据库


                        create database xsg_qufu_spider;

                 3.     use xsg_qufu_spider;

                 3.      create table xsg_news(
                                 id int auto_increment primary key,
                                 xsg_title_list varchar(100) not null,
                                 xsg_date_list varchar(15) not null,
                                 xsg_clicks_list varchar(10) not null,
                                 xsg_content_list varchar(100000) not null,
                                 xsg_checker_list varchar(100) not null
                             )charset=utf8mb4;

create table xsg_news(id int auto_increment primary key,xsg_title_list varchar(100) defaut,xsg_date_list varchar(100) not null,xsg_clicks_list varchar(100) not null,xsg_content_list varchar(15000) not null,xsg_checker_list varchar(100) not null)charset=utf8mb4;

                 4.      desc hero;

                         drop table 表名;           >> 彻底删除整个表

                 5.      select * from hero;

                         delete from 表名;    >> 清空整个表中的数据，但表的字段结构还存在
                          delete from 表名 where 条件;  >> 删除表中的某一行记录



"""

from pymysql import *

# 与mysql数据库进行连接,会创建一个连接对象
con_obj = connect(host="127.0.0.1", user="root",
                  password="123456", database="xsg_qufu_spider", port=3306, charset='utf8mb4')
print('连接成功....')

# 创建一个游标对象
mysql_ = con_obj.cursor()

# 写sql语句，并且使用python代码让sql语句执行
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

        con_obj.commit()
        mysql_.close()

    print(f"\n\033[1;36m曲阜师大学校要闻 第{xsg_j + 1}页15条新闻 已下载...\033[0m", end="  ")



mysql_.close()

con_obj.close()




