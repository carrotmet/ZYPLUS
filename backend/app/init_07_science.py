# -*- coding: utf-8 -*-
"""
07 学科门类：理学 - 初始化脚本
包含：数学类、物理学类、化学类、天文学类、地理科学类、大气科学类、
      海洋科学类、地球物理学类、地质学类、生物科学类、心理学类、统计学类
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

def init_science_data():
    print("=== 初始化 07 理学类数据 ===\n")
    db = SessionLocal()
    
    try:
        discipline = get_or_create_discipline(
            db, "理学", "07",
            "理学学科门类，包含数学、物理、化学、天文、地理、大气、海洋、地球物理、地质、生物、心理、统计等专业类"
        )
        
        # 0701 数学类
        category = get_or_create_category(db, "数学类", "0701", discipline.id, "研究数量、结构、变化及其规律的学科")
        majors_data = [
            ("数学与应用数学", "070101", "培养掌握数学科学基本理论与方法的高级专门人才",
             ["数学分析", "高等代数", "解析几何", "常微分方程", "实变函数", "概率论", "数理统计", "数值分析"]),
            ("信息与计算科学", "070102", "培养具备信息科学和计算科学能力的复合型人才",
             ["数学分析", "高等代数", "数据结构", "算法设计与分析", "数值计算方法", "数据库原理", "机器学习"]),
            ("数理基础科学", "070103T", "培养从事数理基础科学研究和教学的专业人才",
             ["数学分析", "高等代数", "普通物理", "理论力学", "量子力学", "电动力学", "热力学与统计物理"]),
            ("数据计算及应用", "070104T", "培养从事数据计算及应用的专业人才",
             ["数学分析", "高等代数", "数据科学导论", "大数据分析", "数据挖掘", "机器学习", "数据可视化"]),
        ]
        for name, code, desc, courses in majors_data:
            create_major_if_not_exists(db, name, code, category.id, desc, 4, courses)
        
        # 0702 物理学类
        category2 = get_or_create_category(db, "物理学类", "0702", discipline.id, "研究物质运动规律和基本结构的学科")
        majors_data2 = [
            ("物理学", "070201", "培养从事物理学研究和教学的专业人才",
             ["力学", "热学", "电磁学", "光学", "原子物理", "理论力学", "电动力学", "量子力学", "热力学与统计物理"]),
            ("应用物理学", "070202", "培养从事应用物理学研究和开发的专业人才",
             ["普通物理", "理论物理", "固体物理", "激光原理", "光电子学", "材料物理", "计算物理"]),
            ("核物理", "070203", "培养从事核物理研究和应用的专业人才",
             ["原子物理", "核物理", "粒子物理", "辐射探测", "核电子学", "核技术", "辐射防护"]),
            ("声学", "070204T", "培养从事声学研究的专业人才",
             ["声学基础", "电声学", "超声学", "水声学", "建筑声学", "噪声控制", "信号处理"]),
            ("系统科学与工程", "070205T", "培养从事系统科学与工程的专业人才",
             ["系统科学导论", "运筹学", "控制理论", "系统工程", "复杂系统", "系统建模与仿真", "决策科学"]),
            ("量子信息科学", "070206T", "培养从事量子信息科学研究的专业人才",
             ["量子力学", "量子信息导论", "量子计算", "量子通信", "量子密码", "光学", "固体物理"]),
        ]
        for name, code, desc, courses in majors_data2:
            create_major_if_not_exists(db, name, code, category2.id, desc, 4, courses)
        
        # 0703 化学类
        category3 = get_or_create_category(db, "化学类", "0703", discipline.id, "研究物质的组成、结构、性质及其变化规律的学科")
        majors_data3 = [
            ("化学", "070301", "培养从事化学研究和教学的专业人才",
             ["无机化学", "有机化学", "分析化学", "物理化学", "结构化学", "仪器分析", "高分子化学"]),
            ("应用化学", "070302", "培养从事应用化学研究和开发的专业人才",
             ["无机化学", "有机化学", "分析化学", "物理化学", "化工原理", "精细化工", "材料化学"]),
            ("化学生物学", "070303T", "培养从事化学生物学研究的专业人才",
             ["无机化学", "有机化学", "生物化学", "分子生物学", "化学生物学", "药物化学", "生物有机化学"]),
            ("分子科学与工程", "070304T", "培养从事分子科学与工程的专业人才",
             ["无机化学", "有机化学", "物理化学", "高分子化学", "分子设计", "材料化学", "纳米材料"]),
            ("能源化学", "070305T", "培养从事能源化学研究的专业人才",
             ["无机化学", "有机化学", "电化学", "能源化学", "电池技术", "燃料电池", "太阳能电池"]),
            ("化学测量学与技术", "070306T", "培养从事化学测量学与技术的专业人才",
             ["分析化学", "仪器分析", "化学计量学", "测量技术", "质量控制", "标准物质", "实验室管理"]),
            ("资源化学", "070307T", "培养从事资源化学的专业人才",
             ["无机化学", "有机化学", "资源化学", "矿产化学", "海洋化学", "环境化学", "资源利用"]),
        ]
        for name, code, desc, courses in majors_data3:
            create_major_if_not_exists(db, name, code, category3.id, desc, 4, courses)
        
        # 0704 天文学类
        category4 = get_or_create_category(db, "天文学类", "0704", discipline.id, "研究天体和宇宙的学科")
        majors_data4 = [
            ("天文学", "070401", "培养从事天文学研究的专业人才",
             ["普通天文学", "天体力学", "天体物理", "星系天文学", "宇宙学", "观测天文学", "数据处理"]),
        ]
        for name, code, desc, courses in majors_data4:
            create_major_if_not_exists(db, name, code, category4.id, desc, 4, courses)
        
        # 0705 地理科学类
        category5 = get_or_create_category(db, "地理科学类", "0705", discipline.id, "研究地理环境及其与人类活动关系的学科")
        majors_data5 = [
            ("地理科学", "070501", "培养从事地理科学研究和教学的专业人才",
             ["自然地理学", "人文地理学", "地图学", "遥感概论", "地理信息系统", "中国地理", "世界地理"]),
            ("自然地理与资源环境", "070502", "培养从事自然地理与资源环境研究的专业人才",
             ["自然地理学", "资源学", "环境学", "生态学", "遥感技术", "地理信息系统", "资源管理"]),
            ("人文地理与城乡规划", "070503", "培养从事人文地理与城乡规划的专业人才",
             ["人文地理学", "城市规划原理", "区域规划", "土地利用规划", "地理信息系统", "城市设计", "乡村规划"]),
            ("地理信息科学", "070504", "培养从事地理信息科学研究的专业人才",
             ["地理信息系统", "遥感原理", "地图学", "空间数据库", "GIS软件开发", "卫星导航", "空间分析"]),
        ]
        for name, code, desc, courses in majors_data5:
            create_major_if_not_exists(db, name, code, category5.id, desc, 4, courses)
        
        # 0706 大气科学类
        category6 = get_or_create_category(db, "大气科学类", "0706", discipline.id, "研究大气运动规律的学科")
        majors_data6 = [
            ("大气科学", "070601", "培养从事大气科学研究的专业人才",
             ["大气物理学", "大气探测学", "天气学", "动力气象学", "气候学", "数值天气预报", "雷达气象"]),
            ("应用气象学", "070602", "培养从事应用气象工作的专业人才",
             ["气象学", "农业气象学", "航空气象", "海洋气象", "环境气象", "能源气象", "气象服务"]),
            ("气象技术与工程", "070603T", "培养从事气象技术与工程的专业人才",
             ["气象探测技术", "卫星气象", "雷达技术", "气象仪器", "气象信息系统", "气象数据处理", "气象服务工程"]),
            ("地球系统科学", "070604T", "培养从事地球系统科学研究的专业人才",
             ["地球系统科学导论", "大气科学", "海洋科学", "陆地科学", "全球变化", "气候系统", "地球系统模拟"]),
        ]
        for name, code, desc, courses in majors_data6:
            create_major_if_not_exists(db, name, code, category6.id, desc, 4, courses)
        
        # 0707 海洋科学类
        category7 = get_or_create_category(db, "海洋科学类", "0707", discipline.id, "研究海洋自然现象和过程的学科")
        majors_data7 = [
            ("海洋科学", "070701", "培养从事海洋科学研究的专业人才",
             ["海洋学", "物理海洋学", "海洋化学", "海洋生物学", "海洋地质学", "卫星海洋学", "海洋调查"]),
            ("海洋技术", "070702", "培养从事海洋技术开发的专业人才",
             ["海洋学", "海洋探测技术", "海洋遥感", "声学技术", "海洋信息技术", "海洋观测系统", "海洋仪器"]),
            ("海洋资源与环境", "070703T", "培养从事海洋资源与环境研究的专业人才",
             ["海洋学", "海洋生态学", "海洋资源学", "海洋环境学", "海洋法", "资源评估", "环境保护"]),
            ("军事海洋学", "070704T", "培养从事军事海洋学研究的专业人才",
             ["军事海洋学", "海洋环境预报", "水声环境", "海底地形", "海洋战术", "海上导航", "海洋情报"]),
            ("海洋科学与技术", "070705T", "培养从事海洋科学与技术研究的专业人才",
             ["海洋科学", "海洋工程", "海洋技术", "海洋观测", "海洋数据分析", "海洋装备", "海洋信息系统"]),
        ]
        for name, code, desc, courses in majors_data7:
            create_major_if_not_exists(db, name, code, category7.id, desc, 4, courses)
        
        # 0708 地球物理学类
        category8 = get_or_create_category(db, "地球物理学类", "0708", discipline.id, "研究地球物理场及其应用的学科")
        majors_data8 = [
            ("地球物理学", "070801", "培养从事地球物理学研究的专业人才",
             ["固体地球物理学", "地球动力学", "地震学", "重力学", "地磁学", "地热学", "地球物理勘探"]),
            ("空间科学与技术", "070802", "培养从事空间科学与技术研究的专业人才",
             ["空间物理学", "空间探测", "卫星技术", "空间天气", "航天器设计", "轨道力学", "遥感技术"]),
            ("防灾减灾科学与工程", "070803T", "培养从事防灾减灾科学与工程的专业人才",
             ["灾害学", "地震工程", "地质灾害", "气象灾害", "洪水灾害", "应急管理", "风险评估"]),
            ("行星科学", "070804TK", "培养从事行星科学研究的专业人才",
             ["行星科学导论", "行星地质学", "行星大气", "天体生物学", "空间探测", "比较行星学", "深空探测"]),
        ]
        for name, code, desc, courses in majors_data8:
            create_major_if_not_exists(db, name, code, category8.id, desc, 4, courses)
        
        # 0709 地质学类
        category9 = get_or_create_category(db, "地质学类", "0709", discipline.id, "研究地球物质组成、结构构造的学科")
        majors_data9 = [
            ("地质学", "070901", "培养从事地质学研究的专业人才",
             ["普通地质学", "结晶学与矿物学", "岩石学", "构造地质学", "古生物学", "地史学", "矿床学"]),
            ("地球化学", "070902", "培养从事地球化学研究的专业人才",
             ["地球化学", "分析化学", "同位素地球化学", "有机地球化学", "环境地球化学", "矿床地球化学", "宇宙化学"]),
            ("地球信息科学与技术", "070903T", "培养从事地球信息科学与技术的专业人才",
             ["地质学", "地理信息系统", "遥感技术", "地球信息科学", "空间数据库", "地学数据分析", "地学可视化"]),
            ("古生物学", "070904T", "培养从事古生物学研究的专业人才",
             ["古生物学", "地史学", "进化生物学", "化石鉴定", "古生态学", "地层学", "分子古生物学"]),
        ]
        for name, code, desc, courses in majors_data9:
            create_major_if_not_exists(db, name, code, category9.id, desc, 4, courses)
        
        # 0710 生物科学类
        category10 = get_or_create_category(db, "生物科学类", "0710", discipline.id, "研究生命现象和生命活动规律的学科")
        majors_data10 = [
            ("生物科学", "071001", "培养从事生物科学研究的专业人才",
             ["植物学", "动物学", "微生物学", "细胞生物学", "遗传学", "生物化学", "分子生物学", "生态学"]),
            ("生物技术", "071002", "培养从事生物技术开发的专业人才",
             ["生物化学", "分子生物学", "细胞工程", "基因工程", "发酵工程", "酶工程", "生物信息学"]),
            ("生物信息学", "071003", "培养从事生物信息学研究的专业人才",
             ["生物化学", "分子生物学", "基因组学", "生物统计学", "生物信息学", "数据挖掘", "机器学习"]),
            ("生态学", "071004", "培养从事生态学研究的专业人才",
             ["普通生态学", "植物生态学", "动物生态学", "生态系统生态学", "景观生态学", "保护生物学", "环境科学"]),
            ("整合科学", "071005T", "培养从事整合科学研究的专业人才",
             ["数学", "物理", "化学", "生物", "计算方法", "建模与仿真", "跨学科研究"]),
            ("神经科学", "071006T", "培养从事神经科学研究的专业人才",
             ["神经生物学", "认知神经科学", "系统神经科学", "计算神经科学", "神经解剖学", "神经生理学", "神经病理学"]),
        ]
        for name, code, desc, courses in majors_data10:
            create_major_if_not_exists(db, name, code, category10.id, desc, 4, courses)
        
        # 0711 心理学类
        category11 = get_or_create_category(db, "心理学类", "0711", discipline.id, "研究心理现象及其规律的学科")
        majors_data11 = [
            ("心理学", "071101", "培养从事心理学研究和应用的专业人才",
             ["普通心理学", "发展心理学", "社会心理学", "认知心理学", "生理心理学", "心理测量", "实验心理学", "心理咨询"]),
            ("应用心理学", "071102", "培养从事应用心理学工作的专业人才",
             ["心理学导论", "心理测量", "心理咨询", "组织行为学", "人力资源管理", "广告心理学", "司法心理学"]),
        ]
        for name, code, desc, courses in majors_data11:
            create_major_if_not_exists(db, name, code, category11.id, desc, 4, courses)
        
        # 0712 统计学类
        category12 = get_or_create_category(db, "统计学类", "0712", discipline.id, "研究数据收集、分析和推断的学科")
        majors_data12 = [
            ("统计学", "071201", "培养从事统计学研究的专业人才",
             ["数学分析", "高等代数", "概率论", "数理统计", "回归分析", "多元统计分析", "时间序列分析", "抽样调查"]),
            ("应用统计学", "071202", "培养从事应用统计工作的专业人才",
             ["统计学", "统计软件", "数据分析", "经济统计", "金融统计", "生物统计", "社会统计"]),
            ("数据科学", "071203T", "培养从事数据科学研究的专业人才",
             ["数据科学导论", "机器学习", "数据挖掘", "大数据技术", "数据可视化", "统计计算", "数据伦理"]),
            ("生物统计学", "071204T", "培养从事生物统计学研究的专业人才",
             ["概率论", "数理统计", "生物统计", "流行病学", "临床试验", "遗传统计", "生存分析"]),
        ]
        for name, code, desc, courses in majors_data12:
            create_major_if_not_exists(db, name, code, category12.id, desc, 4, courses)
        
        print("\n=== 理学类数据初始化完成 ===")
        
    finally:
        db.close()

if __name__ == "__main__":
    init_science_data()
