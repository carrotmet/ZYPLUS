# -*- coding: utf-8 -*-
import re

file_path = 'D:/github.com/carrotmet/zyplusv2/backend/app/database.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 查找并替换所有多余的引号模式
# 匹配: 4个或更多引号开头，后面是中文，后面是3个或更多引号
patterns = [
    ('""""""删除所有数据库表', '"""删除所有数据库表"""'),
    ('""""""初始化数据库，返回数据库状态信息', '"""初始化数据库，返回数据库状态信息"""'),
]

for p_old, p_new in patterns:
    if p_old in content:
        content = content.replace(p_old, p_new)
        print(f'Replaced: {p_old}')

# 也使用正则表达式修复
content = re.sub(r'""""""([^"]+?)""""""', r'"""\1"""', content)
content = re.sub(r'""""([^"]+?)""""', r'"""\1"""', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('All docstrings fixed')
