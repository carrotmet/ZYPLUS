# -*- coding: utf-8 -*-
"""
初始化专业数据脚本
将专业数据添加到数据库中
"""

import sys
import os
import json

# 添加backend到路径
backend_path = 'D:/github.com/carrotmet/zyplusv2/backend'
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

os.chdir(backend_path)

from app.database import SessionLocal, init_database
from app import models, schemas, crud

def init_major_data():
    """初始化专业数据"""
    print("=== 初始化专业数据 ===\n")
    
    db = SessionLocal()
    
    try:
        # 获取所有学科门类
        disciplines = db.query(models.Discipline).all()
        print(f"找到 {len(disciplines)} 个学科门类")
        
        for discipline in disciplines:
            print(f"\n处理学科门类: {discipline.name} (ID: {discipline.id})")
            
            # 获取该门类的专业类
            categories = db.query(models.MajorCategory).filter(
                models.MajorCategory.discipline_id == discipline.id
            ).all()
            
            print(f"  专业类数量: {len(categories)}")
            
            for category in categories:
                majors_count = db.query(models.Major).filter(
                    models.Major.category_id == category.id
                ).count()
                print(f"    {category.name}: {majors_count} 个专业")
        
        # 定义专业数据
        major_data = [
            # 哲学
            {
                "name": "哲学",
                "code": "010101",
                "category_id": 1,  # 哲学类
                "description": "培养具有系统哲学知识和理论思维能力的人才",
                "duration": 4,
                "main_courses": ["哲学导论", "逻辑学", "伦理学", "美学", "宗教学"]
            },
            {
                "name": "逻辑学",
                "code": "010102",
                "category_id": 1,
                "description": "研究思维形式和规律的学科",
                "duration": 4,
                "main_courses": ["数理逻辑", "哲学逻辑", "计算逻辑", "语言逻辑", "认知逻辑"]
            },
            
            # 经济学 - 经济学类
            {
                "name": "经济学",
                "code": "020101",
                "category_id": 2,  # 经济学类
                "description": "培养具备经济学理论基础和应用能力的专业人才",
                "duration": 4,
                "main_courses": ["微观经济学", "宏观经济学", "计量经济学", "国际经济学", "发展经济学"]
            },
            {
                "name": "国际经济与贸易",
                "code": "020401",
                "category_id": 2,
                "description": "培养国际贸易和跨国经营的专业人才",
                "duration": 4,
                "main_courses": ["国际贸易学", "国际金融", "跨国公司经营", "国际商法", "外贸英语"]
            },
            
            # 经济学 - 金融学类
            {
                "name": "金融学",
                "code": "020301",
                "category_id": 3,  # 金融学类
                "description": "培养金融市场分析和投资管理的专业人才",
                "duration": 4,
                "main_courses": ["货币银行学", "证券投资学", "公司金融", "金融工程", "风险管理"]
            },
            {
                "name": "保险学",
                "code": "020303",
                "category_id": 3,
                "description": "培养保险业务和风险评估的专业人才",
                "duration": 4,
                "main_courses": ["保险学原理", "风险管理", "精算学", "财产保险", "人身保险"]
            },
            
            # 工学 - 电子信息类
            {
                "name": "电子信息工程",
                "code": "080701",
                "category_id": 5,  # 电子信息类
                "description": "培养电子技术和信息处理的专业人才",
                "duration": 4,
                "main_courses": ["电路分析", "信号与系统", "数字信号处理", "通信原理", "嵌入式系统"]
            },
            {
                "name": "通信工程",
                "code": "080703",
                "category_id": 5,
                "description": "培养现代通信技术和系统的专业人才",
                "duration": 4,
                "main_courses": ["通信原理", "移动通信", "光纤通信", "卫星通信", "信息论"]
            },
            
            # 工学 - 计算机类
            {
                "name": "计算机科学与技术",
                "code": "080901",
                "category_id": 4,  # 计算机类
                "description": "培养掌握计算机科学理论和技术的专业人才，具备软件开发、系统设计和算法分析能力",
                "duration": 4,
                "main_courses": ["数据结构", "计算机网络", "操作系统", "数据库原理", "软件工程"]
            },
            {
                "name": "软件工程",
                "code": "080902",
                "category_id": 4,
                "description": "培养软件开发和项目管理的工程人才，注重实践能力和团队协作",
                "duration": 4,
                "main_courses": ["软件工程导论", "面向对象程序设计", "软件测试", "项目管理", "系统分析与设计"]
            },
            {
                "name": "网络工程",
                "code": "080903",
                "category_id": 4,
                "description": "培养网络技术和网络安全的专业人才",
                "duration": 4,
                "main_courses": ["计算机网络", "网络安全", "路由与交换技术", "网络协议分析", "云计算技术"]
            },
            {
                "name": "人工智能",
                "code": "080717",
                "category_id": 4,
                "description": "培养人工智能算法研究和应用开发的专业人才",
                "duration": 4,
                "main_courses": ["机器学习", "深度学习", "自然语言处理", "计算机视觉", "强化学习"]
            },
            
            # 艺术学 - 设计学类
            {
                "name": "视觉传达设计",
                "code": "130502",
                "category_id": 6,  # 设计学类
                "description": "培养视觉传达和数字媒体设计的创意人才",
                "duration": 4,
                "main_courses": ["设计基础","平面设计", "UI/UX设计", "品牌设计", "数字媒体设计"]
            },
            {
                "name": "环境设计",
                "code": "130503",
                "category_id": 6,
                "description": "培养室内外环境设计的专业人才",
                "duration": 4,
                "main_courses": ["设计素描", "色彩构成", "空间设计", "室内设计", "景观设计"]
            },
            {
                "name": "产品设计",
                "code": "130504",
                "category_id": 6,
                "description": "培养工业产品设计的专业人才",
                "duration": 4,
                "main_courses": ["产品设计基础", "工业设计史", "材料工艺", "产品建模", "人机工程学"]
            },
        ]
        
        print(f"\n准备插入 {len(major_data)} 个专业...")
        
        created_count = 0
        for data in major_data:
            # 检查是否已存在
            existing = db.query(models.Major).filter(
                models.Major.code == data["code"]
            ).first()
            
            if existing:
                print(f"  跳过: {data['name']} (已存在)")
                continue
            
            try:
                # 序列化main_courses为JSON字符串
                major_dict = data.copy()
                major_dict['main_courses'] = json.dumps(data['main_courses'], ensure_ascii=False)
                
                # 创建专业
                major = models.Major(**major_dict)
                db.add(major)
                db.commit()
                db.refresh(major)
                print(f"  创建: {data['name']} (ID: {major.id})")
                created_count += 1
            except Exception as e:
                db.rollback()
                print(f"  错误: {data['name']} - {e}")
        
        print(f"\n成功创建 {created_count} 个专业")
        
        # 验证数据
        print("\n=== 验证数据 ===")
        total_majors = db.query(models.Major).count()
        print(f"数据库中专业总数: {total_majors}")
        
        for discipline in disciplines:
            categories = db.query(models.MajorCategory).filter(
                models.MajorCategory.discipline_id == discipline.id
            ).all()
            
            for category in categories:
                majors = db.query(models.Major).filter(
                    models.Major.category_id == category.id
                ).all()
                
                if majors:
                    print(f"  {discipline.name} > {category.name}:")
                    for major in majors:
                        print(f"    - {major.name} ({major.code})")
        
    finally:
        db.close()

if __name__ == "__main__":
    init_major_data()
