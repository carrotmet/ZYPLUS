from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional
import json
from . import database, schemas

# 学科门类CRUD
def create_discipline(db: Session, discipline: schemas.DisciplineCreate):
    db_discipline = database.Discipline(**discipline.dict())
    db.add(db_discipline)
    db.commit()
    db.refresh(db_discipline)
    return db_discipline

def get_disciplines(db: Session, skip: int = 0, limit: int = 100):
    return db.query(database.Discipline).offset(skip).limit(limit).all()

def get_discipline(db: Session, discipline_id: int):
    return db.query(database.Discipline).filter(database.Discipline.id == discipline_id).first()

# 专业类CRUD
def create_major_category(db: Session, major_category: schemas.MajorCategoryCreate):
    db_major_category = database.MajorCategory(**major_category.dict())
    db.add(db_major_category)
    db.commit()
    db.refresh(db_major_category)
    return db_major_category

def get_major_categories(db: Session, discipline_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    query = db.query(database.MajorCategory)
    if discipline_id:
        query = query.filter(database.MajorCategory.discipline_id == discipline_id)
    return query.offset(skip).limit(limit).all()

# 专业CRUD
def create_major(db: Session, major: schemas.MajorCreate):
    major_dict = major.dict()
    # 序列化main_courses为JSON字符串
    if 'main_courses' in major_dict and isinstance(major_dict['main_courses'], list):
        major_dict['main_courses'] = json.dumps(major_dict['main_courses'], ensure_ascii=False)
    db_major = database.Major(**major_dict)
    db.add(db_major)
    db.commit()
    db.refresh(db_major)
    return db_major

def get_majors(db: Session, category_id: Optional[int] = None, skip: int = 0, limit: int = 100):
    query = db.query(database.Major)
    if category_id:
        query = query.filter(database.Major.category_id == category_id)
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
    major = db.query(database.Major).filter(database.Major.id == major_id).first()
    if major and major.main_courses:
        try:
            major.main_courses = json.loads(major.main_courses)
        except (json.JSONDecodeError, TypeError):
            major.main_courses = []
    return major

def search_majors(db: Session, query: str, skip: int = 0, limit: int = 100):
    majors = db.query(database.Major).filter(
        or_(
            database.Major.name.contains(query),
            database.Major.description.contains(query)
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
    db_occupation = database.Occupation(**occupation_dict)
    db.add(db_occupation)
    db.commit()
    db.refresh(db_occupation)
    return db_occupation

def get_occupations(db: Session, industry: Optional[str] = None, skip: int = 0, limit: int = 100):
    query = db.query(database.Occupation)
    if industry:
        query = query.filter(database.Occupation.industry == industry)
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
    occupation = db.query(database.Occupation).filter(database.Occupation.id == occupation_id).first()
    if occupation and occupation.requirements:
        try:
            occupation.requirements = json.loads(occupation.requirements)
        except (json.JSONDecodeError, TypeError):
            occupation.requirements = []
    return occupation

# 职业路径CRUD
def create_career_path(db: Session, career_path: schemas.CareerPathCreate):
    db_career_path = database.CareerPath(**career_path.dict())
    db.add(db_career_path)
    db.commit()
    db.refresh(db_career_path)
    return db_career_path

def get_career_paths(db: Session, occupation_id: int):
    return db.query(database.CareerPath).filter(
        database.CareerPath.occupation_id == occupation_id
    ).order_by(database.CareerPath.experience_min).all()

# 专业职业关联CRUD
def create_major_occupation(db: Session, major_id: int, occupation_id: int, match_score: int = 80):
    db_major_occupation = database.MajorOccupation(
        major_id=major_id,
        occupation_id=occupation_id,
        match_score=match_score
    )
    db.add(db_major_occupation)
    db.commit()
    db.refresh(db_major_occupation)
    return db_major_occupation

def get_major_occupations(db: Session, major_id: Optional[int] = None, occupation_id: Optional[int] = None):
    query = db.query(database.MajorOccupation)
    if major_id:
        query = query.filter(database.MajorOccupation.major_id == major_id)
    if occupation_id:
        query = query.filter(database.MajorOccupation.occupation_id == occupation_id)
    return query.all()

# 推荐系统
def get_recommended_occupations(db: Session, major_id: int, limit: int = 10):
    occupations = db.query(database.Occupation).join(
        database.MajorOccupation,
        database.MajorOccupation.occupation_id == database.Occupation.id
    ).filter(
        database.MajorOccupation.major_id == major_id
    ).order_by(
        database.MajorOccupation.match_score.desc()
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
    db_experience = database.PersonalExperience(**experience.dict())
    db.add(db_experience)
    db.commit()
    db.refresh(db_experience)
    return db_experience

def get_personal_experiences(db: Session, major_id: Optional[int] = None, 
                           school_name: Optional[str] = None,
                           skip: int = 0, limit: int = 10):
    query = db.query(database.PersonalExperience)
    
    if major_id:
        query = query.filter(database.PersonalExperience.major_id == major_id)
    if school_name:
        query = query.filter(database.PersonalExperience.school_name.contains(school_name))
    
    total = query.count()
    items = query.order_by(database.PersonalExperience.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "items": items,
        "total": total,
        "page": skip // limit + 1,
        "limit": limit
    }

def get_personal_experience(db: Session, experience_id: int):
    return db.query(database.PersonalExperience).filter(
        database.PersonalExperience.id == experience_id
    ).first()

# 经验分享CRUD
def create_experience_share(db: Session, share: schemas.ExperienceShareCreate):
    db_share = database.ExperienceShare(**share.dict())
    db.add(db_share)
    db.commit()
    db.refresh(db_share)
    return db_share

def get_experience_shares(db: Session, experience_id: int, skip: int = 0, limit: int = 10):
    query = db.query(database.ExperienceShare).filter(
        database.ExperienceShare.experience_id == experience_id
    )
    
    total = query.count()
    items = query.order_by(database.ExperienceShare.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "items": items,
        "total": total,
        "page": skip // limit + 1,
        "limit": limit
    }

def like_experience_share(db: Session, share_id: int):
    share = db.query(database.ExperienceShare).filter(
        database.ExperienceShare.id == share_id
    ).first()
    if share:
        share.likes += 1
        db.commit()
        db.refresh(share)
    return share

# 获取专业详情（包含相关职业）
def get_major_detail(db: Session, major_id: int):
    major = db.query(database.Major).filter(database.Major.id == major_id).first()
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
    occupation = db.query(database.Occupation).filter(
        database.Occupation.id == occupation_id
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