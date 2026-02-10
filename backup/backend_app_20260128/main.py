from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
import json
from . import crud, schemas, database
from .database import get_db, create_tables

# 创建数据库表
create_tables()

# 创建FastAPI应用
app = FastAPI(
    title="职业规划导航API",
    description="为高中生和大学生提供专业选择与职业发展的API服务",
    version="1.0.0"
)

# 配置CORS
# 在生产环境中，应该将allow_origins设置为具体的域名列表
# 例如: allow_origins=["http://localhost:3000", "https://yourdomain.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: 生产环境需要配置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 根路径
@app.get("/")
def read_root():
    return {"message": "欢迎来到职业规划导航API", "version": "1.0.0"}

# 学科门类相关接口
@app.get("/api/disciplines", response_model=schemas.ResponseModel)
def read_disciplines(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    disciplines = crud.get_disciplines(db, skip=skip, limit=limit)
    return schemas.ResponseModel(data={"disciplines": disciplines})

@app.post("/api/disciplines", response_model=schemas.ResponseModel)
def create_discipline(discipline: schemas.DisciplineCreate, db: Session = Depends(get_db)):
    db_discipline = crud.create_discipline(db, discipline)
    return schemas.ResponseModel(data={"discipline": db_discipline})

@app.get("/api/disciplines/{discipline_id}", response_model=schemas.ResponseModel)
def read_discipline(discipline_id: int, db: Session = Depends(get_db)):
    discipline = crud.get_discipline(db, discipline_id)
    if not discipline:
        raise HTTPException(status_code=404, detail="学科门类不存在")
    return schemas.ResponseModel(data={"discipline": discipline})

# 专业相关接口
@app.get("/api/majors", response_model=schemas.ResponseModel)
def read_majors(
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    majors = crud.get_majors(db, category_id=category_id, skip=skip, limit=limit)
    return schemas.ResponseModel(data={"majors": majors})

@app.post("/api/majors", response_model=schemas.ResponseModel)
def create_major(major: schemas.MajorCreate, db: Session = Depends(get_db)):
    db_major = crud.create_major(db, major)
    return schemas.ResponseModel(data={"major": db_major})

@app.get("/api/majors/{major_id}", response_model=schemas.ResponseModel)
def read_major(major_id: int, db: Session = Depends(get_db)):
    major_detail = crud.get_major_detail(db, major_id)
    if not major_detail:
        raise HTTPException(status_code=404, detail="专业不存在")
    return schemas.ResponseModel(data=major_detail)

@app.get("/api/majors/search", response_model=schemas.ResponseModel)
def search_majors(q: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    majors = crud.search_majors(db, q, skip=skip, limit=limit)
    return schemas.ResponseModel(data={"majors": majors})

# 职业相关接口
@app.get("/api/occupations", response_model=schemas.ResponseModel)
def read_occupations(
    industry: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    occupations = crud.get_occupations(db, industry=industry, skip=skip, limit=limit)
    return schemas.ResponseModel(data={"occupations": occupations})

@app.post("/api/occupations", response_model=schemas.ResponseModel)
def create_occupation(occupation: schemas.OccupationCreate, db: Session = Depends(get_db)):
    db_occupation = crud.create_occupation(db, occupation)
    return schemas.ResponseModel(data={"occupation": db_occupation})

@app.get("/api/occupations/{occupation_id}", response_model=schemas.ResponseModel)
def read_occupation(occupation_id: int, db: Session = Depends(get_db)):
    occupation_detail = crud.get_occupation_detail(db, occupation_id)
    if not occupation_detail:
        raise HTTPException(status_code=404, detail="职业不存在")
    return schemas.ResponseModel(data=occupation_detail)

# 职业路径接口
@app.get("/api/career-paths/{occupation_id}", response_model=schemas.ResponseModel)
def read_career_paths(occupation_id: int, db: Session = Depends(get_db)):
    career_paths = crud.get_career_paths(db, occupation_id)
    return schemas.ResponseModel(data={"career_paths": career_paths})

@app.post("/api/career-paths", response_model=schemas.ResponseModel)
def create_career_path(career_path: schemas.CareerPathCreate, db: Session = Depends(get_db)):
    db_career_path = crud.create_career_path(db, career_path)
    return schemas.ResponseModel(data={"career_path": db_career_path})

# 推荐系统接口
@app.get("/api/recommendations/majors/{major_id}/occupations", response_model=schemas.ResponseModel)
def get_major_recommendations(major_id: int, limit: int = 10, db: Session = Depends(get_db)):
    occupations = crud.get_recommended_occupations(db, major_id, limit)
    return schemas.ResponseModel(data={"occupations": occupations})

# 个人经历接口
@app.get("/api/experiences", response_model=schemas.ResponseModel)
def read_personal_experiences(
    major_id: Optional[int] = None,
    school_name: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    result = crud.get_personal_experiences(
        db, major_id=major_id, school_name=school_name, skip=skip, limit=limit
    )
    return schemas.ResponseModel(data=result)

@app.post("/api/experiences", response_model=schemas.ResponseModel)
def create_personal_experience(experience: schemas.PersonalExperienceCreate, db: Session = Depends(get_db)):
    db_experience = crud.create_personal_experience(db, experience)
    return schemas.ResponseModel(data={"experience": db_experience})

@app.get("/api/experiences/{experience_id}", response_model=schemas.ResponseModel)
def read_personal_experience(experience_id: int, db: Session = Depends(get_db)):
    experience = crud.get_personal_experience(db, experience_id)
    if not experience:
        raise HTTPException(status_code=404, detail="个人经历不存在")
    return schemas.ResponseModel(data={"experience": experience})

@app.get("/api/experiences/major/{major_id}", response_model=schemas.ResponseModel)
def get_major_experiences(major_id: int, db: Session = Depends(get_db)):
    experiences = crud.get_personal_experiences(db, major_id=major_id)
    return schemas.ResponseModel(data=experiences)

# 经验分享接口
@app.get("/api/experiences/{experience_id}/shares", response_model=schemas.ResponseModel)
def read_experience_shares(
    experience_id: int,
    page: int = 1,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    skip = (page - 1) * limit
    result = crud.get_experience_shares(db, experience_id, skip=skip, limit=limit)
    return schemas.ResponseModel(data=result)

@app.post("/api/experiences/{experience_id}/shares", response_model=schemas.ResponseModel)
def create_experience_share(
    experience_id: int,
    share: schemas.ExperienceShareCreate,
    db: Session = Depends(get_db)
):
    # 验证个人经历是否存在
    experience = crud.get_personal_experience(db, experience_id)
    if not experience:
        raise HTTPException(status_code=404, detail="个人经历不存在")
    
    db_share = crud.create_experience_share(db, share)
    return schemas.ResponseModel(data={"share": db_share})

@app.post("/api/experiences/shares/{share_id}/like", response_model=schemas.ResponseModel)
def like_experience_share(share_id: int, db: Session = Depends(get_db)):
    share = crud.like_experience_share(db, share_id)
    if not share:
        raise HTTPException(status_code=404, detail="经验分享不存在")
    return schemas.ResponseModel(data={"share": share})

# 初始化数据接口
@app.post("/api/init-data", response_model=schemas.ResponseModel)
def init_database(db: Session = Depends(get_db)):
    """初始化示例数据"""
    try:
        # 创建学科门类
        disciplines = [
            {"name": "哲学", "code": "01", "description": "哲学学科门类"},
            {"name": "经济学", "code": "02", "description": "经济学学科门类"},
            {"name": "工学", "code": "08", "description": "工学学科门类"},
            {"name": "艺术学", "code": "13", "description": "艺术学学科门类"},
        ]
        
        created_disciplines = []
        for discipline_data in disciplines:
            discipline = crud.create_discipline(db, schemas.DisciplineCreate(**discipline_data))
            created_disciplines.append(discipline)
        
        # 创建专业类
        categories = [
            {"name": "哲学类", "code": "0101", "discipline_id": created_disciplines[0].id},
            {"name": "经济学类", "code": "0201", "discipline_id": created_disciplines[1].id},
            {"name": "金融学类", "code": "0203", "discipline_id": created_disciplines[1].id},
            {"name": "计算机类", "code": "0809", "discipline_id": created_disciplines[2].id},
            {"name": "电子信息类", "code": "0807", "discipline_id": created_disciplines[2].id},
            {"name": "设计学类", "code": "1305", "discipline_id": created_disciplines[3].id},
        ]
        
        created_categories = []
        for category_data in categories:
            category = crud.create_major_category(db, schemas.MajorCategoryCreate(**category_data))
            created_categories.append(category)
        
        # 创建专业
        majors = [
            {
                "name": "哲学", "code": "010101", "category_id": created_categories[0].id,
                "description": "培养具有系统哲学知识和理论思维能力的人才",
                "duration": 4, "main_courses":json.dumps (["哲学导论", "逻辑学", "伦理学"],ensure_ascii=False)
            },
            {
                "name": "经济学", "code": "020101", "category_id": created_categories[1].id,
                "description": "培养具备经济学理论基础和应用能力的专业人才",
                "duration": 4, "main_courses": json.dumps (["微观经济学", "宏观经济学", "计量经济学"],ensure_ascii=False)
            },
            {
                "name": "金融学", "code": "020301", "category_id": created_categories[2].id,
                "description": "培养金融市场分析和投资管理的专业人才",
                "duration": 4, "main_courses": json.dumps (["货币银行学", "证券投资学", "公司金融"],ensure_ascii=False)
            },
            {
                "name": "计算机科学与技术", "code": "080901", "category_id": created_categories[3].id,
                "description": "培养掌握计算机科学理论和技术的专业人才",
                "duration": 4, "main_courses": json.dumps (["数据结构", "计算机网络", "操作系统", "数据库原理"],ensure_ascii=False)
            },
            {
                "name": "软件工程", "code": "080902", "category_id": created_categories[3].id,
                "description": "培养软件开发和项目管理的工程人才",
                "duration": 4, "main_courses": json.dumps (["软件工程导论", "面向对象程序设计", "软件测试"],ensure_ascii=False)
            },
            {
                "name": "电子信息工程", "code": "080701", "category_id": created_categories[4].id,
                "description": "培养电子技术和信息处理的专业人才",
                "duration": 4, "main_courses": json.dumps (["电路分析", "信号与系统", "数字信号处理"],ensure_ascii=False)
            },
            {
                "name": "视觉传达设计", "code": "130502", "category_id": created_categories[5].id,
                "description": "培养视觉传达和数字媒体设计的创意人才",
                "duration": 4, "main_courses": json.dumps (["设计基础", "平面设计", "UI/UX设计"],ensure_ascii=False)
            }
        ]
        
        created_majors = []
        for major_data in majors:
            major = crud.create_major(db, schemas.MajorCreate(**major_data))
            created_majors.append(major)
        
        # 创建职业
        occupations = [
            {
                "name": "软件工程师", "industry": "IT互联网",
                "description": "负责软件系统的设计、开发、测试和维护工作",
                "requirements": ["编程能力", "算法基础", "团队协作", "持续学习"],
                "salary_min": 12000, "salary_max": 50000
            },
            {
                "name": "数据分析师", "industry": "IT互联网",
                "description": "负责数据收集、处理、分析和可视化",
                "requirements": ["统计学", "编程能力", "数据可视化", "业务理解"],
                "salary_min": 10000, "salary_max": 40000
            },
            {
                "name": "金融分析师", "industry": "金融服务",
                "description": "负责金融市场分析、投资研究和风险评估",
                "requirements": ["金融知识", "分析能力", "数学统计", "沟通能力"],
                "salary_min": 15000, "salary_max": 60000
            }
        ]
        
        created_occupations = []
        for occupation_data in occupations:
            occupation = crud.create_occupation(db, schemas.OccupationCreate(**occupation_data))
            created_occupations.append(occupation)
        
        # 创建专业职业关联
        major_occupation_links = [
            (3, 0, 95),  # 计算机科学与技术 -> 软件工程师
            (3, 1, 85),  # 计算机科学与技术 -> 数据分析师
            (4, 0, 90),  # 软件工程 -> 软件工程师
            (1, 2, 80),  # 经济学 -> 金融分析师
            (2, 2, 90),  # 金融学 -> 金融分析师
        ]
        
        for major_idx, occupation_idx, score in major_occupation_links:
            crud.create_major_occupation(
                db, 
                created_majors[major_idx].id, 
                created_occupations[occupation_idx].id, 
                score
            )
        
        # 创建职业路径
        career_paths = [
            # 软件工程师职业路径
            {"occupation_id": created_occupations[0].id, "level": "初级", "title": "初级软件工程师", "experience_min": 0, "experience_max": 2, "avg_salary": 15000},
            {"occupation_id": created_occupations[0].id, "level": "中级", "title": "软件工程师", "experience_min": 2, "experience_max": 5, "avg_salary": 25000},
            {"occupation_id": created_occupations[0].id, "level": "高级", "title": "高级软件工程师", "experience_min": 5, "experience_max": 8, "avg_salary": 35000},
            {"occupation_id": created_occupations[0].id, "level": "专家", "title": "技术专家", "experience_min": 8, "experience_max": 15, "avg_salary": 50000},
            
            # 数据分析师职业路径
            {"occupation_id": created_occupations[1].id, "level": "初级", "title": "数据分析师", "experience_min": 0, "experience_max": 2, "avg_salary": 12000},
            {"occupation_id": created_occupations[1].id, "level": "中级", "title": "高级数据分析师", "experience_min": 2, "experience_max": 5, "avg_salary": 20000},
            {"occupation_id": created_occupations[1].id, "level": "高级", "title": "数据科学家", "experience_min": 5, "experience_max": 8, "avg_salary": 30000},
            
            # 金融分析师职业路径
            {"occupation_id": created_occupations[2].id, "level": "初级", "title": "分析师助理", "experience_min": 0, "experience_max": 2, "avg_salary": 18000},
            {"occupation_id": created_occupations[2].id, "level": "中级", "title": "金融分析师", "experience_min": 2, "experience_max": 5, "avg_salary": 30000},
            {"occupation_id": created_occupations[2].id, "level": "高级", "title": "高级分析师", "experience_min": 5, "experience_max": 8, "avg_salary": 45000},
        ]
        
        for path_data in career_paths:
            crud.create_career_path(db, schemas.CareerPathCreate(**path_data))
        
        return schemas.ResponseModel(
            data={
                "message": "数据库初始化成功",
                "disciplines": len(created_disciplines),
                "majors": len(created_majors),
                "occupations": len(created_occupations)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库初始化失败: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)