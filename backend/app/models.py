from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# 学科门类表
class Discipline(Base):
    __tablename__ = "disciplines"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    major_categories = relationship("MajorCategory", back_populates="discipline")

# 专业类表
class MajorCategory(Base):
    __tablename__ = "major_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), nullable=False)
    discipline_id = Column(Integer, ForeignKey("disciplines.id"), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    discipline = relationship("Discipline", back_populates="major_categories")
    majors = relationship("Major", back_populates="category")

# 专业表
class Major(Base):
    __tablename__ = "majors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), nullable=False, unique=True)
    category_id = Column(Integer, ForeignKey("major_categories.id"), nullable=False)
    description = Column(Text)
    duration = Column(Integer)  # 学制年限
    main_courses = Column(Text)  # 主要课程（JSON格式）
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    category = relationship("MajorCategory", back_populates="majors")
    occupations = relationship("Occupation", secondary="major_occupations", back_populates="majors")
    experiences = relationship("PersonalExperience", back_populates="major")

# 职业表
class Occupation(Base):
    __tablename__ = "occupations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    industry = Column(String(100))
    description = Column(Text)
    requirements = Column(Text)  # 要求（JSON格式）
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    majors = relationship("Major", secondary="major_occupations", back_populates="occupations")
    career_paths = relationship("CareerPath", back_populates="occupation")

# 专业职业关联表
class MajorOccupation(Base):
    __tablename__ = "major_occupations"
    
    id = Column(Integer, primary_key=True, index=True)
    major_id = Column(Integer, ForeignKey("majors.id"), nullable=False)
    occupation_id = Column(Integer, ForeignKey("occupations.id"), nullable=False)
    match_score = Column(Integer, default=80)  # 匹配度

# 职业路径表
class CareerPath(Base):
    __tablename__ = "career_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    occupation_id = Column(Integer, ForeignKey("occupations.id"), nullable=False)
    level = Column(String(50), nullable=False)  # 职级
    title = Column(String(100), nullable=False)  # 职位名称
    experience_min = Column(Integer)
    experience_max = Column(Integer)
    avg_salary = Column(Integer)
    
    # 关系
    occupation = relationship("Occupation", back_populates="career_paths")

# 个人经历表
class PersonalExperience(Base):
    __tablename__ = "personal_experiences"
    
    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String(100), nullable=False)
    major_id = Column(Integer, ForeignKey("majors.id"), nullable=False)
    education = Column(String(50), nullable=False)  # 学历
    school_name = Column(String(200), nullable=False)
    degree = Column(String(100))
    experience = Column(Text, nullable=False)
    is_anonymous = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    major = relationship("Major", back_populates="experiences")
    shares = relationship("ExperienceShare", back_populates="experience")

# 经验分享表
class ExperienceShare(Base):
    __tablename__ = "experience_shares"
    
    id = Column(Integer, primary_key=True, index=True)
    experience_id = Column(Integer, ForeignKey("personal_experiences.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    tags = Column(Text)  # 标签（JSON格式）
    likes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    experience = relationship("PersonalExperience", back_populates="shares")

# 用户表
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True)  # 登录账号
    password_hash = Column(String(255), nullable=False)  # 密码哈希
    email = Column(String(100))
    phone = Column(String(20))
    nickname = Column(String(100))  # 昵称
    avatar_url = Column(String(255))  # 头像URL
    user_profile_id = Column(String(100), unique=True)  # 关联用户画像的ID
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)


# 所有模型类列表
__all__ = [
    'Discipline',
    'MajorCategory', 
    'Major',
    'Occupation',
    'MajorOccupation',
    'CareerPath',
    'PersonalExperience',
    'ExperienceShare',
    'User'
]