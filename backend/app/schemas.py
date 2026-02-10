from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

# 基础响应模型
class ResponseModel(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[dict] = None

# 学科门类模型
class DisciplineBase(BaseModel):
    name: str = Field(..., description="学科门类名称")
    code: str = Field(..., description="学科代码")
    description: Optional[str] = None

class DisciplineCreate(DisciplineBase):
    pass

class DisciplineUpdate(DisciplineBase):
    pass

class Discipline(DisciplineBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 专业类模型
class MajorCategoryBase(BaseModel):
    name: str = Field(..., description="专业类名称")
    code: str = Field(..., description="专业类代码")
    discipline_id: int = Field(..., description="所属学科ID")
    description: Optional[str] = None

class MajorCategoryCreate(MajorCategoryBase):
    pass

class MajorCategoryUpdate(MajorCategoryBase):
    pass

class MajorCategory(MajorCategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 专业模型
class MajorBase(BaseModel):
    name: str = Field(..., description="专业名称")
    code: str = Field(..., description="专业代码")
    category_id: int = Field(..., description="所属专业类ID")
    description: str = Field(..., description="专业描述")
    duration: int = Field(..., description="学制年限")
    main_courses: List[str] = Field(default_factory=list, description="主要课程")

class MajorCreate(MajorBase):
    pass

class MajorUpdate(MajorBase):
    pass

class Major(MajorBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 职业模型
class OccupationBase(BaseModel):
    name: str = Field(..., description="职业名称")
    industry: Optional[str] = None
    description: str = Field(..., description="职业描述")
    requirements: List[str] = Field(default_factory=list, description="要求")
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None

class OccupationCreate(OccupationBase):
    pass

class OccupationUpdate(OccupationBase):
    pass

class Occupation(OccupationBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 职业路径模型
class CareerPathBase(BaseModel):
    occupation_id: int = Field(..., description="职业ID")
    level: str = Field(..., description="职级")
    title: str = Field(..., description="职位名称")
    experience_min: Optional[int] = None
    experience_max: Optional[int] = None
    avg_salary: Optional[int] = None

class CareerPathCreate(CareerPathBase):
    pass

class CareerPathUpdate(CareerPathBase):
    pass

class CareerPath(CareerPathBase):
    id: int
    
    class Config:
        from_attributes = True

# 个人经历模型
class PersonalExperienceBase(BaseModel):
    nickname: str = Field(..., description="用户昵称")
    major_id: int = Field(..., description="专业ID")
    education: str = Field(..., description="学历")
    school_name: str = Field(..., description="学校名称")
    degree: Optional[str] = None
    experience: str = Field(..., description="个人经历")
    is_anonymous: bool = Field(default=False, description="是否匿名")

class PersonalExperienceCreate(PersonalExperienceBase):
    pass

class PersonalExperienceUpdate(PersonalExperienceBase):
    pass

class PersonalExperience(PersonalExperienceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# 个人经历详情模型
class PersonalExperienceDetail(PersonalExperience):
    major_name: str = Field(..., description="专业名称")

# 经验分享模型
class ExperienceShareBase(BaseModel):
    experience_id: int = Field(..., description="个人经历ID")
    title: str = Field(..., description="分享标题")
    content: str = Field(..., description="分享内容")
    tags: List[str] = Field(default_factory=list, description="标签")

class ExperienceShareCreate(ExperienceShareBase):
    pass

class ExperienceShareUpdate(ExperienceShareBase):
    pass

class ExperienceShare(ExperienceShareBase):
    id: int
    likes: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 专业详情模型（包含相关职业）
class MajorDetail(Major):
    category_name: str = Field(..., description="专业类名称")
    discipline_name: str = Field(..., description="学科门类名称")
    related_occupations: List[Occupation] = Field(default_factory=list)

# 职业详情模型（包含职业路径）
class OccupationDetail(Occupation):
    career_paths: List[CareerPath] = Field(default_factory=list)

# 搜索响应模型
class SearchResult(BaseModel):
    discipline: str
    category: str
    major: Major

# 树形导航用嵌套模型
class MajorTree(Major):
    """用于树形导航的专业模型"""
    pass

class MajorCategoryTree(MajorCategory):
    """用于树形导航的专业类模型，包含专业列表"""
    majors: List[MajorTree] = Field(default_factory=list)

class DisciplineTree(Discipline):
    """用于树形导航的学科门类模型，包含专业类和专业列表"""
    major_categories: List[MajorCategoryTree] = Field(default_factory=list)

# 分页响应模型
class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    limit: int


# ==================== 用户认证模型 ====================

class UserRegister(BaseModel):
    """用户注册"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    nickname: Optional[str] = Field(None, description="昵称")


class UserLogin(BaseModel):
    """用户登录"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserInfo(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: Optional[str]
    phone: Optional[str]
    nickname: Optional[str]
    avatar_url: Optional[str]
    user_profile_id: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """登录响应"""
    token: str = Field(..., description="登录令牌")
    user: UserInfo
    user_profile_id: str = Field(..., description="用户画像ID")