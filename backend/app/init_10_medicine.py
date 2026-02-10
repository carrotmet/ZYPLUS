# -*- coding: utf-8 -*-
"""
10 学科门类：医学 - 初始化脚本
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
        d = db.query(models.Discipline).filter(models.Discipline.code == "10").first()
        if not d:
            d = models.Discipline(name="医学", code="10", description="医学学科门类")
            db.add(d); db.commit(); db.refresh(d)
        print(f"学科门类: {d.name} (ID: {d.id})")
        
        # 1002 临床医学类
        c = db.query(models.MajorCategory).filter(models.MajorCategory.code == "1002").first()
        if not c:
            c = models.MajorCategory(name="临床医学类", code="1002", discipline_id=d.id, description="研究临床医学")
            db.add(c); db.commit(); db.refresh(c)
        
        majors = [
            ("临床医学", "100201K", 5, ["人体解剖学", "生理学", "病理学", "药理学", "诊断学", "内科学", "外科学", "妇产科学", "儿科学"]),
            ("麻醉学", "100202TK", 5, ["麻醉解剖学", "麻醉生理学", "麻醉药理学", "临床麻醉学", "危重病医学", "疼痛诊疗学", "急救医学"]),
            ("医学影像学", "100203TK", 5, ["影像物理学", "人体解剖学", "病理学", "诊断学", "影像诊断学", "超声诊断学", "核医学"]),
        ]
        for name, code, dur, courses in majors:
            if not db.query(models.Major).filter(models.Major.code == code).first():
                m = models.Major(name=name, code=code, category_id=c.id, description=f"培养{name}专业人才",
                               duration=dur, main_courses=json.dumps(courses, ensure_ascii=False))
                db.add(m); db.commit()
                print(f"  创建: {name}")
        
        print("\n医学类数据初始化完成")
    finally:
        db.close()

if __name__ == "__main__":
    init_data()
