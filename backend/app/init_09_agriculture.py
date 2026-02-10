# -*- coding: utf-8 -*-
"""
09 学科门类：农学 - 初始化脚本
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
        d = db.query(models.Discipline).filter(models.Discipline.code == "09").first()
        if not d:
            d = models.Discipline(name="农学", code="09", description="农学学科门类")
            db.add(d); db.commit(); db.refresh(d)
        print(f"学科门类: {d.name} (ID: {d.id})")
        
        # 0901 植物生产类
        c = db.query(models.MajorCategory).filter(models.MajorCategory.code == "0901").first()
        if not c:
            c = models.MajorCategory(name="植物生产类", code="0901", discipline_id=d.id, description="研究植物生产")
            db.add(c); db.commit(); db.refresh(c)
        
        majors = [
            ("农学", "090101", 4, ["作物栽培", "作物育种", "土壤肥料", "植物保护", "农业生态", "种子学", "耕作学"]),
            ("园艺", "090102", 4, ["果树学", "蔬菜学", "观赏园艺", "设施园艺", "园艺产品贮藏", "园艺植物育种", "植物保护"]),
            ("植物保护", "090103", 4, ["普通植物病理学", "普通昆虫学", "农业植物病理学", "农业昆虫学", "农药学", "生物防治", "植物检疫"]),
            ("植物科学与技术", "090104", 4, ["植物学", "植物生理学", "遗传学", "分子生物学", "植物育种", "植物生产", "植物生物技术"]),
            ("种子科学与工程", "090105", 4, ["种子生物学", "种子生产", "种子加工", "种子检验", "种子贮藏", "种子经营管理", "品种选育"]),
        ]
        for name, code, dur, courses in majors:
            if not db.query(models.Major).filter(models.Major.code == code).first():
                m = models.Major(name=name, code=code, category_id=c.id, description=f"培养{name}专业人才",
                               duration=dur, main_courses=json.dumps(courses, ensure_ascii=False))
                db.add(m); db.commit()
                print(f"  创建: {name}")
        
        print("\n农学类数据初始化完成")
    finally:
        db.close()

if __name__ == "__main__":
    init_data()
