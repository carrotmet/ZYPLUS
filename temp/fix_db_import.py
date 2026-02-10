import re

file_path = 'D:/github.com/carrotmet/zyplusv2/backend/app/database.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 查找"# 数据库目录设置"这一行，在它之前插入模型导入代码
pattern = r'(# 数据库目录设置 - 使用项目根目录下的data文件夹)'
replacement = r'''# 导入所有模型类以确保它们被注册（解决循环导入问题）
from . import models

# 重新导出模型类，以便crud.py可以使用database.Discipline方式访问
Discipline = models.Discipline
MajorCategory = models.MajorCategory
Major = models.Major
Occupation = models.Occupation
MajorOccupation = models.MajorOccupation
CareerPath = models.CareerPath
PersonalExperience = models.PersonalExperience
ExperienceShare = models.ExperienceShare

\g<1>'''

new_content = re.sub(pattern, replacement, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print('database.py updated with model imports')
