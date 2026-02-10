# -*- coding: utf-8 -*-
"""
05 学科门类：文学 - 中国语言文学类与新闻传播学类
包含：中国语言文学类、新闻传播学类
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
    """获取或创建学科门类"""
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
    """获取或创建专业类"""
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
    """创建专业（如果不存在）"""
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

def init_literature_chinese_data():
    """初始化文学学科数据（中国语言文学类与新闻传播学类）"""
    print("=== 初始化 05 文学类数据（中国语言文学与新闻传播）===\n")
    db = SessionLocal()
    
    try:
        # 创建学科门类：文学
        discipline = get_or_create_discipline(
            db, "文学", "05",
            "文学学科门类，包含中国语言文学、外国语言文学、新闻传播学等专业类"
        )
        
        # 0501 中国语言文学类
        category = get_or_create_category(db, "中国语言文学类", "0501", discipline.id,
            "研究中国语言和文学的学科")
        majors_data = [
            ("汉语言文学", "050101", "培养从事汉语言文学教学、研究和应用的专业人才",
             ["现代汉语", "古代汉语", "语言学概论", "中国古代文学", "中国现当代文学", "外国文学", "文学概论", "写作"]),
            ("汉语言", "050102", "培养具备汉语及语言学、中国文学等方面系统知识和专业技能的语言学专门人才",
             ["现代汉语", "古代汉语", "语言学概论", "汉语史", "文字学", "音韵学", "训诂学", "语言调查与研究方法"]),
            ("汉语国际教育", "050103", "培养从事对外汉语教学和中外文化交流的专业人才",
             ["现代汉语", "古代汉语", "语言学概论", "对外汉语教学概论", "中国文化概论", "跨文化交际", "第二语言习得"]),
            ("中国少数民族语言文学", "050104", "培养从事中国少数民族语言文学研究和教学的专业人才",
             ["语言学概论", "古代汉语", "现代汉语", "民族语言", "民族文学", "民族文化", "民族古籍"]),
            ("古典文献学", "050105", "培养从事古典文献整理和研究的专业人才",
             ["古代汉语", "文字学", "音韵学", "训诂学", "目录学", "版本学", "校勘学", "古籍整理"]),
            ("应用语言学", "050106T", "培养从事应用语言学研究和实务的专业人才",
             ["语言学概论", "应用语言学", "计算语言学", "语料库语言学", "心理语言学", "社会语言学", "语言信息处理"]),
            ("秘书学", "050107T", "培养从事秘书工作的专业人才",
             ["秘书学概论", "公文写作", "办公自动化", "档案管理", "会务组织", "公共关系", "商务礼仪"]),
            ("中国语言与文化", "050108T", "培养从事中国语言与文化研究和传播的专业人才",
             ["现代汉语", "古代汉语", "中国文化概论", "中国古代文学", "中国现当代文学", "文化人类学", "跨文化交际"]),
            ("手语翻译", "050109T", "培养从事手语翻译的专业人才",
             ["手语语言学", "中国手语", "国际手语", "聋人文化", "口译基础", "翻译理论与实践", "特殊教育概论"]),
            ("数字人文", "050110T", "培养从事数字人文研究和应用的专业人才",
             ["数字人文导论", "文本挖掘", "数据可视化", "自然语言处理", "数字图书馆", "人文数据库", "计算思维"]),
            ("中国古典学", "050111T", "培养从事中国古典学研究的专业人才",
             ["中国古代经典", "古文字学", "古典文献学", "经学", "史学", "子学", "集部之学"]),
            ("汉学与中国学", "050112T", "培养从事汉学与中国学研究的专业人才",
             ["海外汉学史", "中国学概论", "中国古代文化", "中国近现代史", "中西文化交流", "国际中国研究", "比较文化"]),
            ("应用中文", "050113T", "培养从事中文应用的专业人才",
             ["应用写作", "中文信息处理", "媒体语言", "创意写作", "文案策划", "新媒体传播", "文化产业"]),
        ]
        for name, code, desc, courses in majors_data:
            create_major_if_not_exists(db, name, code, category.id, desc, 4, courses)
        
        # 0503 新闻传播学类
        category3 = get_or_create_category(db, "新闻传播学类", "0503", discipline.id,
            "研究新闻传播活动及其规律的学科")
        majors_data3 = [
            ("新闻学", "050301", "培养从事新闻采编、新闻研究的专业人才",
             ["新闻学概论", "中国新闻史", "外国新闻史", "新闻采访与写作", "新闻编辑", "新闻评论", "媒介伦理与法规"]),
            ("广播电视学", "050302", "培养从事广播电视工作的专业人才",
             ["广播电视概论", "电视摄像", "电视节目编辑", "广播电视新闻", "纪录片创作", "播音主持", "影视艺术"]),
            ("广告学", "050303", "培养从事广告策划、创意、设计的专业人才",
             ["广告学概论", "广告策划", "广告创意", "广告设计", "广告文案", "广告调查", "品牌营销"]),
            ("传播学", "050304", "培养从事传播学研究和实务的专业人才",
             ["传播学概论", "传播研究方法", "大众传播", "人际传播", "组织传播", "跨文化传播", "新媒体传播"]),
            ("编辑出版学", "050305", "培养从事编辑出版工作的专业人才",
             ["编辑出版学", "图书编辑", "期刊编辑", "数字出版", "出版经营", "版权贸易", "校对实务"]),
            ("网络与新媒体", "050306T", "培养从事网络与新媒体工作的专业人才",
             ["新媒体概论", "网络传播", "网页设计", "数字媒体技术", "数据新闻", "社交媒体", "新媒体运营"]),
            ("数字出版", "050307T", "培养从事数字出版工作的专业人才",
             ["数字出版概论", "电子书制作", "数字内容管理", "出版技术", "版权管理", "数字营销", "阅读器技术"]),
            ("时尚传播", "050308T", "培养从事时尚传播的专业人才",
             ["时尚传播概论", "时尚产业", "时尚媒体", "品牌传播", "视觉传达", "时尚摄影", "时尚写作"]),
            ("国际新闻与传播", "050309T", "培养从事国际新闻与传播的专业人才",
             ["国际新闻", "国际传播", "全球媒体", "对外报道", "国际政治", "跨文化传播", "英语新闻写作"]),
            ("会展", "050310T", "培养从事会展策划与管理的复合型人才",
             ["会展概论", "会展策划", "会展营销", "会展设计", "会展管理", "活动管理", "节庆管理"]),
        ]
        for name, code, desc, courses in majors_data3:
            create_major_if_not_exists(db, name, code, category3.id, desc, 4, courses)
        
        print("\n=== 文学类（中国语言文学与新闻传播）数据初始化完成 ===")
        
    finally:
        db.close()

if __name__ == "__main__":
    init_literature_chinese_data()
