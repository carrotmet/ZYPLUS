# -*- coding: utf-8 -*-
"""
13 学科门类：艺术学 - 初始化脚本
"""
import sys, os, json
backend_path = 'D:/github.com/carrotmet/zyplusv2/backend'
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)
os.chdir(backend_path)
from app.database import SessionLocal
from app import models

def init_data():
    db = SessionLocal()
    try:
        d = db.query(models.Discipline).filter(models.Discipline.code == "13").first()
        if not d:
            d = models.Discipline(name="艺术学", code="13", description="艺术学学科门类")
            db.add(d); db.commit(); db.refresh(d)
        print(f"学科门类: {d.name} (ID: {d.id})")
        
        # 1302 音乐与舞蹈学类
        c = db.query(models.MajorCategory).filter(models.MajorCategory.code == "1302").first()
        if not c:
            c = models.MajorCategory(name="音乐与舞蹈学类", code="1302", discipline_id=d.id, description="研究音乐与舞蹈艺术")
            db.add(c); db.commit(); db.refresh(c)
        
        majors = [
            ("音乐表演", "130201", 4, ["声乐", "器乐", "乐理", "视唱练耳", "和声学", "曲式分析", "音乐史", "舞台表演"]),
            ("音乐学", "130202", 4, ["音乐理论", "音乐史", "民族音乐学", "音乐教育", "作曲技术", "音乐美学", "音乐心理学"]),
            ("舞蹈表演", "130204", 4, ["芭蕾基训", "中国古典舞", "民族民间舞", "现代舞", "舞蹈编导", "舞蹈史", "舞蹈美学"]),
            ("舞蹈学", "130205", 4, ["舞蹈理论", "舞蹈史", "舞蹈编导", "舞蹈教学", "舞蹈解剖学", "舞蹈心理学", "民族舞蹈"]),
        ]
        for name, code, dur, courses in majors:
            if not db.query(models.Major).filter(models.Major.code == code).first():
                m = models.Major(name=name, code=code, category_id=c.id, description=f"培养{name}专业人才",
                               duration=dur, main_courses=json.dumps(courses, ensure_ascii=False))
                db.add(m); db.commit()
                print(f"  创建: {name}")
        
        # 1303 戏剧与影视学类
        c2 = db.query(models.MajorCategory).filter(models.MajorCategory.code == "1303").first()
        if not c2:
            c2 = models.MajorCategory(name="戏剧与影视学类", code="1303", discipline_id=d.id, description="研究戏剧与影视")
            db.add(c2); db.commit(); db.refresh(c2)
        
        majors2 = [
            ("表演", "130301", 4, ["表演基础", "台词", "形体", "声乐", "角色创作", "戏剧概论", "影视表演"]),
            ("戏剧影视文学", "130304", 4, ["戏剧概论", "电影概论", "编剧技巧", "剧本创作", "影视写作", "中外戏剧史", "文学基础"]),
            ("广播电视编导", "130305", 4, ["电视艺术概论", "导演基础", "摄影构图", "电视节目制作", "编剧", "广播电视史", "新媒体"]),
            ("播音与主持艺术", "130309", 4, ["播音发声", "播音创作", "广播电视播音", "新闻播音", "节目主持", "配音艺术", "口语传播"]),
            ("动画", "130310", 4, ["动画概论", "动画造型", "原画设计", "动画运动规律", "三维动画", "动画后期", "故事板"]),
        ]
        for name, code, dur, courses in majors2:
            if not db.query(models.Major).filter(models.Major.code == code).first():
                m = models.Major(name=name, code=code, category_id=c2.id, description=f"培养{name}专业人才",
                               duration=dur, main_courses=json.dumps(courses, ensure_ascii=False))
                db.add(m); db.commit()
                print(f"  创建: {name}")
        
        print("\n艺术学类数据初始化完成")
    finally:
        db.close()

if __name__ == "__main__":
    init_data()
