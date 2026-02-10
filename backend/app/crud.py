from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from typing import List, Optional
import json
from . import database, schemas
from . import models  # 直接从models导入模型类

# 学科门类CRUD
def create_discipline(db: Session, discipline: schemas.DisciplineCreate):
    db_discipline = models.Discipline(**discipline.dict())
    db.add(db_discipline)
    db.commit()
    db.refresh(db_discipline)
    return db_discipline

def get_disciplines(db: Session, skip: int = 0, limit: int = 100):
    """获取学科门类列表，包含专业类和专业信息"""
    return db.query(models.Discipline).options(
        joinedload(models.Discipline.major_categories).joinedload(models.MajorCategory.majors)
    ).offset(skip).limit(limit).all()

def get_discipline(db: Session, discipline_id: int):
    """获取单个学科门类，包含专业类和专业信息"""
    return db.query(models.Discipline).options(
        joinedload(models.Discipline.major_categories).joinedload(models.MajorCategory.majors)
    ).filter(models.Discipline.id == discipline_id).first()

# 专业类CRUD
def create_major_category(db: Session, major_category: schemas.MajorCategoryCreate):
    db_major_category = models.MajorCategory(**major_category.dict())
    db.add(db_major_category)
    db.commit()
    db.refresh(db_major_category)
    return db_major_category

def get_major_categories(db: Session, discipline_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    query = db.query(models.MajorCategory)
    if discipline_id:
        query = query.filter(models.MajorCategory.discipline_id == discipline_id)
    return query.offset(skip).limit(limit).all()

# 专业CRUD
def create_major(db: Session, major: schemas.MajorCreate):
    major_dict = major.dict()
    # 序列化main_courses为JSON字符串
    if 'main_courses' in major_dict and isinstance(major_dict['main_courses'], list):
        major_dict['main_courses'] = json.dumps(major_dict['main_courses'], ensure_ascii=False)
    db_major = models.Major(**major_dict)
    db.add(db_major)
    db.commit()
    db.refresh(db_major)
    return db_major

def get_majors(db: Session, category_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Major)
    if category_id:
        query = query.filter(models.Major.category_id == category_id)
    majors = query.offset(skip).limit(limit).all()
    # 反序列化main_courses
    for major in majors:
        if major.main_courses:
            try:
                major.main_courses = json.loads(major.main_courses)
            except (json.JSONDecodeError, TypeError):
                major.main_courses = []
    return majors

def get_major(db: Session, major_id: int):
    major = db.query(models.Major).filter(models.Major.id == major_id).first()
    if major and major.main_courses:
        try:
            major.main_courses = json.loads(major.main_courses)
        except (json.JSONDecodeError, TypeError):
            major.main_courses = []
    return major

def search_majors(db: Session, query: str, skip: int = 0, limit: int = 100):
    majors = db.query(models.Major).filter(
        or_(
            models.Major.name.contains(query),
            models.Major.description.contains(query)
        )
    ).offset(skip).limit(limit).all()
    # 反序列化main_courses
    for major in majors:
        if major.main_courses:
            try:
                major.main_courses = json.loads(major.main_courses)
            except (json.JSONDecodeError, TypeError):
                major.main_courses = []
    return majors

# 职业CRUD
def create_occupation(db: Session, occupation: schemas.OccupationCreate):
    occupation_dict = occupation.dict()
    # 序列化requirements为JSON字符串
    if 'requirements' in occupation_dict and isinstance(occupation_dict['requirements'], list):
        occupation_dict['requirements'] = json.dumps(occupation_dict['requirements'], ensure_ascii=False)
    db_occupation = models.Occupation(**occupation_dict)
    db.add(db_occupation)
    db.commit()
    db.refresh(db_occupation)
    return db_occupation

def get_occupations(db: Session, industry: Optional[str] = None, skip: int = 0, limit: int = 100):
    query = db.query(models.Occupation)
    if industry:
        query = query.filter(models.Occupation.industry == industry)
    occupations = query.offset(skip).limit(limit).all()
    # 反序列化requirements
    for occupation in occupations:
        if occupation.requirements:
            try:
                occupation.requirements = json.loads(occupation.requirements)
            except (json.JSONDecodeError, TypeError):
                occupation.requirements = []
    return occupations

def get_occupation(db: Session, occupation_id: int):
    occupation = db.query(models.Occupation).filter(models.Occupation.id == occupation_id).first()
    if occupation and occupation.requirements:
        try:
            occupation.requirements = json.loads(occupation.requirements)
        except (json.JSONDecodeError, TypeError):
            occupation.requirements = []
    return occupation

# 职业路径CRUD
def create_career_path(db: Session, career_path: schemas.CareerPathCreate):
    db_career_path = models.CareerPath(**career_path.dict())
    db.add(db_career_path)
    db.commit()
    db.refresh(db_career_path)
    return db_career_path

def get_career_paths(db: Session, occupation_id: int):
    return db.query(models.CareerPath).filter(
        models.CareerPath.occupation_id == occupation_id
    ).order_by(models.CareerPath.experience_min).all()

# 专业职业关联CRUD
def create_major_occupation(db: Session, major_id: int, occupation_id: int, match_score: int = 80):
    db_major_occupation = models.MajorOccupation(
        major_id=major_id,
        occupation_id=occupation_id,
        match_score=match_score
    )
    db.add(db_major_occupation)
    db.commit()
    db.refresh(db_major_occupation)
    return db_major_occupation

def get_major_occupations(db: Session, major_id: Optional[int] = None, occupation_id: Optional[int] = None):
    query = db.query(models.MajorOccupation)
    if major_id:
        query = query.filter(models.MajorOccupation.major_id == major_id)
    if occupation_id:
        query = query.filter(models.MajorOccupation.occupation_id == occupation_id)
    return query.all()

# 推荐系统
def get_recommended_occupations(db: Session, major_id: int, limit: int = 10):
    occupations = db.query(models.Occupation).join(
        models.MajorOccupation,
        models.MajorOccupation.occupation_id == models.Occupation.id
    ).filter(
        models.MajorOccupation.major_id == major_id
    ).order_by(
        models.MajorOccupation.match_score.desc()
    ).limit(limit).all()
    # 反序列化requirements
    for occupation in occupations:
        if occupation.requirements:
            try:
                occupation.requirements = json.loads(occupation.requirements)
            except (json.JSONDecodeError, TypeError):
                occupation.requirements = []
    return occupations

# 个人经历CRUD
def create_personal_experience(db: Session, experience: schemas.PersonalExperienceCreate):
    db_experience = models.PersonalExperience(**experience.dict())
    db.add(db_experience)
    db.commit()
    db.refresh(db_experience)
    return db_experience

def get_personal_experiences(db: Session, major_id: Optional[int] = None, 
                           school_name: Optional[str] = None,
                           skip: int = 0, limit: int = 10):
    query = db.query(models.PersonalExperience)
    
    if major_id:
        query = query.filter(models.PersonalExperience.major_id == major_id)
    if school_name:
        query = query.filter(models.PersonalExperience.school_name.contains(school_name))
    
    total = query.count()
    items = query.order_by(models.PersonalExperience.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "items": items,
        "total": total,
        "page": skip // limit + 1,
        "limit": limit
    }

def get_personal_experience(db: Session, experience_id: int):
    return db.query(models.PersonalExperience).filter(
        models.PersonalExperience.id == experience_id
    ).first()

# 经验分享CRUD
def create_experience_share(db: Session, share: schemas.ExperienceShareCreate):
    db_share = models.ExperienceShare(**share.dict())
    db.add(db_share)
    db.commit()
    db.refresh(db_share)
    return db_share

def get_experience_shares(db: Session, experience_id: int, skip: int = 0, limit: int = 10):
    query = db.query(models.ExperienceShare).filter(
        models.ExperienceShare.experience_id == experience_id
    )
    
    total = query.count()
    items = query.order_by(models.ExperienceShare.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "items": items,
        "total": total,
        "page": skip // limit + 1,
        "limit": limit
    }

def like_experience_share(db: Session, share_id: int):
    share = db.query(models.ExperienceShare).filter(
        models.ExperienceShare.id == share_id
    ).first()
    if share:
        share.likes += 1
        db.commit()
        db.refresh(share)
    return share

# 获取专业详情（包含相关职业）
def get_major_detail(db: Session, major_id: int):
    major = db.query(models.Major).filter(models.Major.id == major_id).first()
    if not major:
        return None
    
    # 反序列化main_courses
    if major.main_courses:
        try:
            major.main_courses = json.loads(major.main_courses)
        except (json.JSONDecodeError, TypeError):
            major.main_courses = []
    
    # 获取相关职业
    related_occupations = get_recommended_occupations(db, major_id)
    
    return {
        "major": major,
        "related_occupations": related_occupations
    }

# 获取职业详情（包含职业路径）
def get_occupation_detail(db: Session, occupation_id: int):
    occupation = db.query(models.Occupation).filter(
        models.Occupation.id == occupation_id
    ).first()
    if not occupation:
        return None
    
    # 反序列化requirements
    if occupation.requirements:
        try:
            occupation.requirements = json.loads(occupation.requirements)
        except (json.JSONDecodeError, TypeError):
            occupation.requirements = []
    
    # 获取职业路径
    career_paths = get_career_paths(db, occupation_id)
    
    return {
        "occupation": occupation,
        "career_paths": career_paths
    }