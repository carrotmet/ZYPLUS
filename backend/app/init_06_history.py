# -*- coding: utf-8 -*-
"""
06 学科门类：历史学 - 初始化脚本
包含：历史学类
"""

import sys
import os
import json

backend_path = 'D:/github.com/carrotmet/zyplusv2/backend'
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
os.chdir(backend_path)

from app.database import SessionLocal
from app import models

def get_or_create_discipline(db, name, code, description):
    discipline = db.query(models.Discipline).filter(models.Discipline.code == code).first()
    if not discipline:
        discipline = models.Discipline(name=name, code=code, description=description)
        db.add(discipline)
        db.commit()
        db.refresh(discipline)
        print(f"  创建学科门类: {name} (ID: {discipline.id})")
    else:
        print(f"  学科门类已存在: {name} (ID: {discipline.id})")
    return discipline

def get_or_create_category(db, name, code, discipline_id, description):
    category = db.query(models.MajorCategory).filter(
        models.MajorCategory.code == code,
        models.MajorCategory.discipline_id == discipline_id
    ).first()
    if not category:
        category = models.MajorCategory(
            name=name, code=code, discipline_id=discipline_id, description=description
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        print(f"    创建专业类: {name} (ID: {category.id})")
    else:
        print(f"    专业类已存在: {name} (ID: {category.id})")
    return category

def create_major_if_not_exists(db, name, code, category_id, description, duration, courses):
    existing = db.query(models.Major).filter(models.Major.code == code).first()
    if existing:
        print(f"      跳过: {name} (已存在)")
        return None
    
    major = models.Major(
        name=name,
        code=code,
        category_id=category_id,
        description=description,
        duration=duration,
        main_courses=json.dumps(courses, ensure_ascii=False)
    )
    db.add(major)
    db.commit()
    db.refresh(major)
    print(f"      创建专业: {name} (ID: {major.id})")
    return major

def init_history_data():
    print("=== 初始化 06 历史学类数据 ===\n")
    db = SessionLocal()
    
    try:
        discipline = get_or_create_discipline(
            db, "历史学", "06",
            "历史学学科门类，包含历史学等专业类"
        )
        
        category = get_or_create_category(db, "历史学类", "0601", discipline.id,
            "研究人类社会发展过程的学科")
        
        majors_data = [
            ("历史学", "060101", "培养从事历史研究和教学的专业人才",
             ["中国通史", "世界通史", "史学概论", "中国历史文选", "中国史学史", "西方史学史", "历史地理学"]),
            ("世界史", "060102", "培养从事世界历史研究和教学的专业人才",
             ["世界通史", "中国通史", "史学概论", "古代文明", "中世纪史", "近现代史", "区域国别史"]),
            ("考古学", "060103", "培养从事考古研究和实务的专业人才",
             ["考古学通论", "田野考古", "文物学", "博物馆学", "古代文字", "科技考古", "文化遗产"]),
            ("文物与博物馆学", "060104", "培养从事文物与博物馆工作的专业人才",
             ["博物馆学概论", "文物学", "考古学", "博物馆陈列设计", "文物保护", "文化遗产管理", "藏品管理"]),
            ("文物保护技术", "060105T", "培养从事文物保护技术的专业人才",
             ["文物保护概论", "无机化学", "有机化学", "分析化学", "文物材料", "保护修复技术", "文物检测"]),
            ("外国语言与外国历史", "060106T", "培养从事外国语言与外国历史研究的专业人才",
             ["外国历史", "专业外语", "区域研究", "国际关系", "跨文化交际", "翻译", "世界文明史"]),
            ("文化遗产", "060107T", "培养从事文化遗产保护和管理的专业人才",
             ["文化遗产概论", "文化遗产法规", "文化遗产保护", "博物馆学", "考古学", "文化人类学", "旅游管理"]),
            ("古文字学", "060108T", "培养从事古文字学研究的专业人才",
             ["古文字学", "甲骨文", "金文", "战国文字", "简帛学", "文字学", "古代汉语", "考古学"]),
            ("科学史", "060109T", "培养从事科学技术史研究的专业人才",
             ["科学史", "技术史", "科学哲学", "科学社会学", "中国古代科技史", "世界科技史", "科技政策"]),
        ]
        for name, code, desc, courses in majors_data:
            create_major_if_not_exists(db, name, code, category.id, desc, 4, courses)
        
        print("\n=== 历史学类数据初始化完成 ===")
        
    finally:
        db.close()

if __name__ == "__main__":
    init_history_data()
