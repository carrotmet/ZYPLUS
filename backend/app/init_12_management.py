# -*- coding: utf-8 -*-
"""
12 学科门类：管理学 - 初始化脚本
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
        d = db.query(models.Discipline).filter(models.Discipline.code == "12").first()
        if not d:
            d = models.Discipline(name="管理学", code="12", description="管理学学科门类")
            db.add(d); db.commit(); db.refresh(d)
        print(f"学科门类: {d.name} (ID: {d.id})")
        
        # 1202 工商管理类
        c = db.query(models.MajorCategory).filter(models.MajorCategory.code == "1202").first()
        if not c:
            c = models.MajorCategory(name="工商管理类", code="1202", discipline_id=d.id, description="研究工商管理")
            db.add(c); db.commit(); db.refresh(c)
        
        majors = [
            ("工商管理", "120201K", 4, ["管理学", "微观经济学", "宏观经济学", "会计学", "财务管理", "市场营销", "人力资源管理", "战略管理"]),
            ("市场营销", "120202", 4, ["市场营销学", "消费者行为学", "市场调查", "广告学", "销售管理", "品牌管理", "数字营销"]),
            ("会计学", "120203K", 4, ["会计学原理", "财务会计", "成本会计", "管理会计", "审计学", "财务管理", "税法"]),
            ("财务管理", "120204", 4, ["财务管理", "财务会计", "成本管理", "投资管理", "财务分析", "风险管理", "公司理财"]),
            ("人力资源管理", "120206", 4, ["人力资源管理", "组织行为学", "劳动经济学", "薪酬管理", "绩效管理", "招聘与培训", "劳动法"]),
        ]
        for name, code, dur, courses in majors:
            if not db.query(models.Major).filter(models.Major.code == code).first():
                m = models.Major(name=name, code=code, category_id=c.id, description=f"培养{name}专业人才",
                               duration=dur, main_courses=json.dumps(courses, ensure_ascii=False))
                db.add(m); db.commit()
                print(f"  创建: {name}")
        
        print("\n管理学类数据初始化完成")
    finally:
        db.close()

if __name__ == "__main__":
    init_data()
