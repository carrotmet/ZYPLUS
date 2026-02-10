// API服务 - 与后端API交互
// 支持环境变量配置，适应不同开发环境
class ApiService {
    constructor() {
        // 支持环境变量覆盖默认配置
        this.baseURL = this._getApiBaseUrl();
        this.useMockData = false;
        this.init();
    }

    _getApiBaseUrl() {
        // 优先使用环境变量
        if (typeof process !== 'undefined' && process.env && process.env.API_URL) {
            return process.env.API_URL;
        }
        // 检查本地存储的配置
        const savedConfig = localStorage.getItem('apiBaseUrl');
        if (savedConfig) {
            return savedConfig;
        }
        // 默认配置
        return 'http://localhost:8000/api';
    }

    // 保存API地址配置
    saveApiBaseUrl(url) {
        this.baseURL = url;
        localStorage.setItem('apiBaseUrl', url);
        console.log(`[ApiService] API地址已更新: ${url}`);
    }

    // 获取当前API地址
    getApiBaseUrl() {
        return this.baseURL;
    }

    // 重置为默认配置
    resetApiBaseUrl() {
        this.baseURL = 'http://localhost:8000/api';
        localStorage.removeItem('apiBaseUrl');
        console.log('[ApiService] API地址已重置为默认值');
    }

    init() {
        // 检查API是否可用
        this.checkAPI().then(available => {
            if (!available) {
                console.log('[ApiService] API服务不可用，使用本地模拟数据');
                this.useMockData = true;
            } else {
                console.log('[ApiService] API服务已连接');
            }
        });
    }

    async checkAPI() {
        try {
            // 检查根路径
            const response = await fetch(`${this.baseURL.replace('/api', '')}/`);
            return response.ok;
        } catch (error) {
            console.log('[ApiService] API连接检查失败:', error.message);
            return false;
        }
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
        };

        try {
            const response = await fetch(url, config);
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.message || '请求失败');
            }
            
            // 后端返回格式: {code, message, data: {...}}
            // 返回完整响应对象，包含 code, message, data
            return result;
        } catch (error) {
            console.error('API请求失败:', error);
            throw error;
        }
    }

    // 通用 GET 请求方法
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    // 通用 POST 请求方法
    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // 通用 PUT 请求方法
    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    // 通用 DELETE 请求方法
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    // 转换蛇形命名为驼峰命名
    _convertToCamelCase(obj) {
        if (Array.isArray(obj)) {
            return obj.map(item => this._convertToCamelCase(item));
        }
        if (obj === null || typeof obj !== 'object') {
            return obj;
        }
        const result = {};
        for (const [key, value] of Object.entries(obj)) {
            // 将蛇形命名转换为驼峰命名
            const camelKey = key.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
            result[camelKey] = this._convertToCamelCase(value);
        }
        return result;
    }

    // 学科门类相关API
    async getDisciplines() {
        try {
            const response = await this.request('/disciplines');
            // 转换字段名为驼峰命名
            return this._convertToCamelCase(response.disciplines || []);
        } catch (error) {
            return this.getMockDisciplines();
        }
    }

    // 专业相关API
    async getMajors(categoryId = null) {
        try {
            const endpoint = categoryId ? `/majors?category_id=${categoryId}` : '/majors';
            const response = await this.request(endpoint);
            return response.majors || [];
        } catch (error) {
            return this.getMockMajors(categoryId);
        }
    }

    async getMajor(majorId) {
        try {
            const response = await this.request(`/majors/${majorId}`);
            return response;
        } catch (error) {
            return this.getMockMajor(majorId);
        }
    }

    async searchMajors(query) {
        try {
            const response = await this.request(`/majors/search?q=${encodeURIComponent(query)}`);
            return response.majors || [];
        } catch (error) {
            return this.searchMockMajors(query);
        }
    }

    async createMajor(majorData) {
        try {
            const response = await this.request('/majors', {
                method: 'POST',
                body: JSON.stringify(majorData)
            });
            return response.major;
        } catch (error) {
            return this.createMockMajor(majorData);
        }
    }

    // 职业相关API
    async getOccupations(industry = null) {
        try {
            const endpoint = industry ? `/occupations?industry=${encodeURIComponent(industry)}` : '/occupations';
            const response = await this.request(endpoint);
            return response.occupations || [];
        } catch (error) {
            return this.getMockOccupations(industry);
        }
    }

    async getOccupation(occupationId) {
        try {
            const response = await this.request(`/occupations/${occupationId}`);
            return response;
        } catch (error) {
            return this.getMockOccupation(occupationId);
        }
    }

    async createOccupation(occupationData) {
        try {
            const response = await this.request('/occupations', {
                method: 'POST',
                body: JSON.stringify(occupationData)
            });
            return response.occupation;
        } catch (error) {
            return this.createMockOccupation(occupationData);
        }
    }

    // 职业路径API
    async getCareerPaths(occupationId) {
        try {
            const response = await this.request(`/career-paths/${occupationId}`);
            return response.career_paths || [];
        } catch (error) {
            return this.getMockCareerPaths(occupationId);
        }
    }

    async createCareerPath(careerPathData) {
        try {
            const response = await this.request('/career-paths', {
                method: 'POST',
                body: JSON.stringify(careerPathData)
            });
            return response.career_path;
        } catch (error) {
            return this.createMockCareerPath(careerPathData);
        }
    }

    // 推荐系统API
    async getRecommendedOccupations(majorId, limit = 10) {
        try {
            const response = await this.request(`/recommendations/majors/${majorId}/occupations?limit=${limit}`);
            return response.occupations || [];
        } catch (error) {
            return this.getMockRecommendedOccupations(majorId);
        }
    }

    // 个人经历API
    async getPersonalExperiences(params = {}) {
        try {
            const queryString = new URLSearchParams(params).toString();
            const endpoint = queryString ? `/experiences?${queryString}` : '/experiences';
            const response = await this.request(endpoint);
            return response;
        } catch (error) {
            return this.getMockPersonalExperiences(params);
        }
    }

    async getPersonalExperience(experienceId) {
        try {
            const response = await this.request(`/experiences/${experienceId}`);
            return response.experience;
        } catch (error) {
            return this.getMockPersonalExperience(experienceId);
        }
    }

    async createPersonalExperience(experienceData) {
        try {
            const response = await this.request('/experiences', {
                method: 'POST',
                body: JSON.stringify(experienceData)
            });
            return response.experience;
        } catch (error) {
            return this.createMockPersonalExperience(experienceData);
        }
    }

    async getMajorExperiences(majorId) {
        try {
            const response = await this.request(`/experiences/major/${majorId}`);
            return response;
        } catch (error) {
            return this.getMockMajorExperiences(majorId);
        }
    }

    // 经验分享API
    async getExperienceShares(experienceId, params = {}) {
        try {
            const queryString = new URLSearchParams(params).toString();
            const endpoint = queryString ? 
                `/experiences/${experienceId}/shares?${queryString}` : 
                `/experiences/${experienceId}/shares`;
            const response = await this.request(endpoint);
            return response;
        } catch (error) {
            return this.getMockExperienceShares(experienceId);
        }
    }

    async createExperienceShare(experienceId, shareData) {
        try {
            const response = await this.request(`/experiences/${experienceId}/shares`, {
                method: 'POST',
                body: JSON.stringify(shareData)
            });
            return response.share;
        } catch (error) {
            return this.createMockExperienceShare(experienceId, shareData);
        }
    }

    async likeExperienceShare(shareId) {
        try {
            const response = await this.request(`/experiences/shares/${shareId}/like`, {
                method: 'POST'
            });
            return response.share;
        } catch (error) {
            return this.likeMockExperienceShare(shareId);
        }
    }

    // 初始化数据
    async initDatabase() {
        try {
            const response = await this.request('/init-data', {
                method: 'POST'
            });
            return response;
        } catch (error) {
            console.log('使用模拟数据');
            return { message: '使用模拟数据' };
        }
    }

    // 模拟数据方法
    getMockDisciplines() {
        return [
            {
                id: 1,
                name: '哲学',
                code: '01',
                description: '哲学学科门类',
                majorCategories: [
                    {
                        id: 101,
                        name: '哲学类',
                        code: '0101',
                        majors: [
                            { id: 10101, name: '哲学', code: '010101', duration: 4, description: '培养具有系统哲学知识和理论思维能力的人才', courses: ['哲学导论', '逻辑学', '伦理学', '美学', '宗教学'] },
                            { id: 10102, name: '逻辑学', code: '010102', duration: 4, description: '研究思维形式和规律的学科', courses: ['数理逻辑', '哲学逻辑', '计算逻辑', '语言逻辑', '认知逻辑'] }
                        ]
                    }
                ]
            },
            {
                id: 2,
                name: '经济学',
                code: '02',
                description: '经济学学科门类',
                majorCategories: [
                    {
                        id: 201,
                        name: '经济学类',
                        code: '0201',
                        majors: [
                            { id: 20101, name: '经济学', code: '020101', duration: 4, description: '培养具备经济学理论基础和应用能力的专业人才', courses: ['微观经济学', '宏观经济学', '计量经济学', '国际经济学', '金融学'] },
                            { id: 20102, name: '国际经济与贸易', code: '020401', duration: 4, description: '培养国际贸易和跨国经营的专业人才', courses: ['国际贸易学', '国际金融', '跨国公司经营', '国际商法', '外贸英语'] }
                        ]
                    },
                    {
                        id: 202,
                        name: '金融学类',
                        code: '0203',
                        majors: [
                            { id: 20201, name: '金融学', code: '020301', duration: 4, description: '培养金融市场分析和投资管理的专业人才', courses: ['货币银行学', '证券投资学', '公司金融', '金融工程', '风险管理'] },
                            { id: 20202, name: '保险学', code: '020303', duration: 4, description: '培养保险业务和风险评估的专业人才', courses: ['保险学原理', '风险管理', '精算学', '财产保险', '人身保险'] }
                        ]
                    }
                ]
            },
            {
                id: 8,
                name: '工学',
                code: '08',
                description: '工学学科门类',
                majorCategories: [
                    {
                        id: 801,
                        name: '计算机类',
                        code: '0809',
                        majors: [
                            { id: 80101, name: '计算机科学与技术', code: '080901', duration: 4, description: '培养掌握计算机科学理论和技术的专业人才', courses: ['数据结构', '计算机网络', '操作系统', '数据库原理', '软件工程'] },
                            { id: 80102, name: '软件工程', code: '080902', duration: 4, description: '培养软件开发和项目管理的工程人才', courses: ['软件工程导论', '面向对象程序设计', '软件测试', '项目管理', '系统分析与设计'] },
                            { id: 80103, name: '网络工程', code: '080903', duration: 4, description: '培养网络技术和网络安全的专业人才', courses: ['计算机网络', '网络安全', '路由与交换技术', '网络协议分析', '云计算技术'] }
                        ]
                    },
                    {
                        id: 802,
                        name: '电子信息类',
                        code: '0807',
                        majors: [
                            { id: 80201, name: '电子信息工程', code: '080701', duration: 4, description: '培养电子技术和信息处理的专业人才', courses: ['电路分析', '信号与系统', '数字信号处理', '通信原理', '嵌入式系统'] },
                            { id: 80202, name: '通信工程', code: '080703', duration: 4, description: '培养现代通信技术和系统的专业人才', courses: ['通信原理', '移动通信', '光纤通信', '信息论', '无线通信'] }
                        ]
                    }
                ]
            },
            {
                id: 12,
                name: '艺术学',
                code: '13',
                description: '艺术学学科门类',
                majorCategories: [
                    {
                        id: 1201,
                        name: '设计学类',
                        code: '1305',
                        majors: [
                            { id: 120101, name: '视觉传达设计', code: '130502', duration: 4, description: '培养视觉传达和数字媒体设计的创意人才', courses: ['设计基础', '平面设计', 'UI/UX设计', '品牌设计', '数字媒体设计'] },
                            { id: 120102, name: '环境设计', code: '130503', duration: 4, description: '培养室内外环境设计的专业人才', courses: ['设计素描', '色彩构成', '空间设计', '室内设计', '景观设计'] }
                        ]
                    }
                ]
            }
        ];
    }

    getMockMajors(categoryId = null) {
        const allMajors = [
            { id: 10101, name: '哲学', code: '010101', category_id: 1, description: '培养具有系统哲学知识和理论思维能力的人才', duration: 4, main_courses: ['哲学导论', '逻辑学', '伦理学'] },
            { id: 20101, name: '经济学', code: '020101', category_id: 2, description: '培养具备经济学理论基础和应用能力的专业人才', duration: 4, main_courses: ['微观经济学', '宏观经济学', '计量经济学'] },
            { id: 80101, name: '计算机科学与技术', code: '080901', category_id: 3, description: '培养掌握计算机科学理论和技术的专业人才', duration: 4, main_courses: ['数据结构', '计算机网络', '操作系统', '数据库原理'] },
            { id: 80102, name: '软件工程', code: '080902', category_id: 3, description: '培养软件开发和项目管理的工程人才', duration: 4, main_courses: ['软件工程导论', '面向对象程序设计', '软件测试'] }
        ];
        
        return categoryId ? allMajors.filter(m => m.category_id === categoryId) : allMajors;
    }

    getMockMajor(majorId) {
        const majors = this.getMockMajors();
        return majors.find(m => m.id === majorId) || null;
    }

    searchMockMajors(query) {
        const majors = this.getMockMajors();
        return majors.filter(m => 
            m.name.toLowerCase().includes(query.toLowerCase()) ||
            m.description.toLowerCase().includes(query.toLowerCase())
        );
    }

    createMockMajor(majorData) {
        return {
            id: Date.now(),
            ...majorData,
            created_at: new Date().toISOString()
        };
    }

    getMockOccupations(industry = null) {
        const allOccupations = [
            { 
                id: 1, 
                name: '软件工程师', 
                industry: 'IT互联网', 
                description: '负责软件系统的设计、开发、测试和维护工作', 
                requirements: ['编程能力', '算法基础', '团队协作', '持续学习'], 
                salaryMin: 12000, 
                salaryMax: 50000,
                careerPath: [
                    { level: '初级', title: '初级软件工程师', experienceMin: 0, experienceMax: 2, avgSalary: 15000 },
                    { level: '中级', title: '软件工程师', experienceMin: 2, experienceMax: 5, avgSalary: 25000 },
                    { level: '高级', title: '高级软件工程师', experienceMin: 5, experienceMax: 8, avgSalary: 35000 },
                    { level: '专家', title: '技术专家/架构师', experienceMin: 8, experienceMax: 15, avgSalary: 50000 }
                ]
            },
            { 
                id: 2, 
                name: '数据分析师', 
                industry: 'IT互联网', 
                description: '负责数据收集、处理、分析和可视化', 
                requirements: ['统计学', '编程能力', '数据可视化', '业务理解'], 
                salaryMin: 10000, 
                salaryMax: 40000,
                careerPath: [
                    { level: '初级', title: '数据分析师', experienceMin: 0, experienceMax: 2, avgSalary: 12000 },
                    { level: '中级', title: '高级数据分析师', experienceMin: 2, experienceMax: 5, avgSalary: 20000 },
                    { level: '高级', title: '数据科学家', experienceMin: 5, experienceMax: 8, avgSalary: 30000 },
                    { level: '专家', title: '首席数据科学家', experienceMin: 8, experienceMax: 15, avgSalary: 40000 }
                ]
            },
            { 
                id: 3, 
                name: '金融分析师', 
                industry: '金融服务', 
                description: '负责金融市场分析、投资研究和风险评估', 
                requirements: ['金融知识', '分析能力', '数学统计', '沟通能力'], 
                salaryMin: 15000, 
                salaryMax: 60000,
                careerPath: [
                    { level: '初级', title: '分析师助理', experienceMin: 0, experienceMax: 2, avgSalary: 18000 },
                    { level: '中级', title: '金融分析师', experienceMin: 2, experienceMax: 5, avgSalary: 30000 },
                    { level: '高级', title: '高级分析师', experienceMin: 5, experienceMax: 8, avgSalary: 45000 },
                    { level: '专家', title: '首席分析师', experienceMin: 8, experienceMax: 15, avgSalary: 60000 }
                ]
            }
        ];
        
        return industry ? allOccupations.filter(o => o.industry === industry) : allOccupations;
    }

    getMockOccupation(occupationId) {
        const occupations = this.getMockOccupations();
        return occupations.find(o => o.id === occupationId) || null;
    }

    createMockOccupation(occupationData) {
        return {
            id: Date.now(),
            ...occupationData,
            created_at: new Date().toISOString()
        };
    }

    getMockCareerPaths(occupationId) {
        const careerPaths = {
            1: [
                { id: 1, level: '初级', title: '初级软件工程师', experience_min: 0, experience_max: 2, avg_salary: 15000 },
                { id: 2, level: '中级', title: '软件工程师', experience_min: 2, experience_max: 5, avg_salary: 25000 },
                { id: 3, level: '高级', title: '高级软件工程师', experience_min: 5, experience_max: 8, avg_salary: 35000 },
                { id: 4, level: '专家', title: '技术专家', experience_min: 8, experience_max: 15, avg_salary: 50000 }
            ],
            2: [
                { id: 5, level: '初级', title: '数据分析师', experience_min: 0, experience_max: 2, avg_salary: 12000 },
                { id: 6, level: '中级', title: '高级数据分析师', experience_min: 2, experience_max: 5, avg_salary: 20000 },
                { id: 7, level: '高级', title: '数据科学家', experience_min: 5, experience_max: 8, avg_salary: 30000 }
            ]
        };
        
        return careerPaths[occupationId] || [];
    }

    createMockCareerPath(careerPathData) {
        return {
            id: Date.now(),
            ...careerPathData
        };
    }

    getMockRecommendedOccupations(majorId) {
        const recommendations = {
            80101: [
                { id: 1, name: '软件工程师', industry: 'IT互联网', match_score: 95 },
                { id: 2, name: '数据分析师', industry: 'IT互联网', match_score: 85 }
            ],
            20101: [
                { id: 3, name: '金融分析师', industry: '金融服务', match_score: 90 }
            ]
        };
        
        return recommendations[majorId] || [];
    }

    getMockPersonalExperiences(params = {}) {
        const experiences = [
            {
                id: 1,
                nickname: '张同学',
                major_id: 80101,
                major_name: '计算机科学与技术',
                education: '学士',
                school_name: '清华大学',
                degree: '计算机科学与技术学士',
                experience: '毕业后进入某互联网公司工作，从初级开发工程师做起，现在已经是高级软件工程师，主要负责后端系统开发。',
                is_anonymous: false,
                created_at: '2024-10-23T10:00:00Z'
            },
            {
                id: 2,
                nickname: '匿名用户',
                major_id: 20101,
                major_name: '经济学',
                education: '硕士',
                school_name: '北京大学',
                degree: '经济学硕士',
                experience: '在银行工作了3年，主要从事风险控制工作，现在是一家金融科技公司的高级分析师。',
                is_anonymous: true,
                created_at: '2024-10-22T15:30:00Z'
            }
        ];
        
        return {
            items: experiences,
            total: experiences.length,
            page: 1,
            limit: 10
        };
    }

    getMockPersonalExperience(experienceId) {
        const experiences = this.getMockPersonalExperiences().items;
        return experiences.find(e => e.id === experienceId) || null;
    }

    createMockPersonalExperience(experienceData) {
        return {
            id: Date.now(),
            ...experienceData,
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
        };
    }

    getMockMajorExperiences(majorId) {
        const experiences = this.getMockPersonalExperiences().items;
        return {
            items: experiences.filter(e => e.major_id === majorId),
            total: experiences.filter(e => e.major_id === majorId).length,
            page: 1,
            limit: 10
        };
    }

    getMockExperienceShares(experienceId) {
        return {
            items: [
                {
                    id: 1,
                    experience_id: experienceId,
                    title: '职业发展建议',
                    content: '建议学弟学妹们多参加实习，积累项目经验。',
                    tags: ['实习', '项目经验'],
                    likes: 15,
                    created_at: '2024-10-23T12:00:00Z'
                }
            ],
            total: 1,
            page: 1,
            limit: 10
        };
    }

    createMockExperienceShare(experienceId, shareData) {
        return {
            id: Date.now(),
            experience_id: experienceId,
            ...shareData,
            likes: 0,
            created_at: new Date().toISOString()
        };
    }

    likeMockExperienceShare(shareId) {
        return { id: shareId, likes: Math.floor(Math.random() * 100) };
    }
}

// 创建全局API服务实例
window.apiService = new ApiService();