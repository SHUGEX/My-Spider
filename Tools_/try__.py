#插入产品信息
insert_good_sql = """
    INSERT INTO T_GOOD(good_name, good_type, img_src, good_description, how_to_use,             
    volumetric, price,sale, spider_time)
    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
values = (pymysql.escape_string(data_dict['good_name']),
    pymysql.escape_string(data_dict['good_type']),data_dict['img_src'], pymysql.escape_string(data_dict['good_description']), data_dict['how_to_use'],pymysql.escape_string(data_dict['volumetric']), pymysql.escape_string(data_dict['price']),data_dict['sale'], datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))