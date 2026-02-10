// 职业规划网站主要JavaScript逻辑

// 全局变量
let selectedMajor = null;
let filteredMajors = [];
let disciplines = [];
let occupations = [];

// DOM加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// 初始化应用
async function initializeApp() {
    try {
        console.log('[App] 开始初始化...');
        
        // 初始化API服务
        await loadApiService();
        console.log('[App] API服务加载完成');
        
        // 加载数据
        await loadInitialData();
        console.log('[App] 数据加载完成, disciplines数量:', disciplines ? disciplines.length : 0);
        
        // 确保disciplines是数组
        if (!disciplines || !Array.isArray(disciplines)) {
            console.warn('[App] disciplines数据异常，使用模拟数据');
            useMockData();
        }
        
        // 渲染界面
        renderUI();
        console.log('[App] 界面渲染完成');
        
    } catch (error) {
        console.error('应用初始化失败:', error);
        // 使用模拟数据
        useMockData();
        // 渲染界面
        renderUI();
    }
}

// 渲染UI界面
function renderUI() {
    // 渲染界面
    renderMajorTree();
    renderPopularMajors();
    setupSearchFunctionality();
    setupScrollAnimations();
    
    // 添加页面加载动画
    if (typeof anime !== 'undefined') {
        anime({
            targets: '.fade-in',
            opacity: [0, 1],
            translateY: [20, 0],
            duration: 800,
            delay: anime.stagger(200),
            easing: 'easeOutQuart'
        });
    }
}

// 加载API服务
async function loadApiService() {
    return new Promise((resolve) => {
        const script = document.createElement('script');
        script.src = 'api-service.js';
        script.onload = () => resolve();
        script.onerror = () => resolve(); // 如果加载失败也继续
        document.head.appendChild(script);
    });
}

// 加载初始数据
async function loadInitialData() {
    try {
        console.log('[Data] 开始加载数据...');
        
        if (window.apiService && window.apiService.getDisciplines) {
            console.log('[Data] 从API获取数据...');
            
            // 获取学科门类数据
            disciplines = await window.apiService.getDisciplines();
            console.log('[Data] API返回disciplines:', disciplines ? disciplines.length : 0);
            
            if (disciplines && disciplines.length > 0) {
                console.log('[Data] 第一个学科门类:', disciplines[0].name);
                console.log('[Data] majorCategories:', disciplines[0].majorCategories ? '存在' : '不存在');
            }
            
            // 获取职业数据
            occupations = await window.apiService.getOccupations();
            console.log('[Data] API返回occupations:', occupations ? occupations.length : 0);
        } else {
            console.log('[Data] API服务不可用，使用模拟数据');
            // 使用模拟数据
            useMockData();
        }
    } catch (error) {
        console.error('数据加载失败:', error);
        console.log('[Data] 使用模拟数据作为后备');
        // 使用模拟数据
        useMockData();
    }
}

// 使用模拟数据
function useMockData() {
    disciplines = [
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
                        { id: 10101, name: '哲学', code: '010101', duration: 4, description: '培养具有系统哲学知识和理论思维能力的人才', mainCourses: ['哲学导论', '逻辑学', '伦理学', '美学', '宗教学'] },
                        { id: 10102, name: '逻辑学', code: '010102', duration: 4, description: '研究思维形式和规律的学科', mainCourses: ['数理逻辑', '哲学逻辑', '计算逻辑', '语言逻辑', '认知逻辑'] }
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
                        { id: 20101, name: '经济学', code: '020101', duration: 4, description: '培养具备经济学理论基础和应用能力的专业人才', mainCourses: ['微观经济学', '宏观经济学', '计量经济学', '国际经济学', '金融学'] },
                        { id: 20102, name: '国际经济与贸易', code: '020401', duration: 4, description: '培养国际贸易和跨国经营的专业人才', mainCourses: ['国际贸易学', '国际金融', '跨国公司经营', '国际商法', '外贸英语'] }
                    ]
                },
                {
                    id: 202,
                    name: '金融学类',
                    code: '0203',
                    majors: [
                        { id: 20201, name: '金融学', code: '020301', duration: 4, description: '培养金融市场分析和投资管理的专业人才', mainCourses: ['货币银行学', '证券投资学', '公司金融', '金融工程', '风险管理'] },
                        { id: 20202, name: '保险学', code: '020303', duration: 4, description: '培养保险业务和风险评估的专业人才', mainCourses: ['保险学原理', '风险管理', '精算学', '财产保险', '人身保险'] }
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
                        { 
                            id: 80101, 
                            name: '计算机科学与技术', 
                            code: '080901', 
                            duration: 4, 
                            description: '培养掌握计算机科学理论和技术的专业人才，具备软件开发、系统设计和算法分析能力', 
                            mainCourses: ['数据结构', '计算机网络', '操作系统', '数据库原理', '软件工程', '算法设计', '计算机组成原理', '编译原理'] 
                        },
                        { 
                            id: 80102, 
                            name: '软件工程', 
                            code: '080902', 
                            duration: 4, 
                            description: '培养软件开发和项目管理的工程人才，注重实践能力和团队协作', 
                            mainCourses: ['软件工程导论', '面向对象程序设计', '软件测试', '项目管理', '系统分析与设计', '软件架构', 'DevOps', '敏捷开发'] 
                        },
                        { 
                            id: 80103, 
                            name: '网络工程', 
                            code: '080903', 
                            duration: 4, 
                            description: '培养网络技术和网络安全的专业人才', 
                            mainCourses: ['计算机网络', '网络安全', '路由与交换技术', '网络协议分析', '网络编程', '云计算技术', '物联网技术', '网络管理'] 
                        }
                    ]
                },
                {
                    id: 802,
                    name: '电子信息类',
                    code: '0807',
                    majors: [
                        { 
                            id: 80201, 
                            name: '电子信息工程', 
                            code: '080701', 
                            duration: 4, 
                            description: '培养电子技术和信息处理的专业人才', 
                            mainCourses: ['电路分析', '信号与系统', '数字信号处理', '通信原理', '微机原理', '嵌入式系统', '图像处理', '人工智能'] 
                        },
                        { 
                            id: 80202, 
                            name: '通信工程', 
                            code: '080703', 
                            duration: 4, 
                            description: '培养现代通信技术和系统的专业人才', 
                            mainCourses: ['通信原理', '移动通信', '光纤通信', '卫星通信', '信息论', '编码理论', '无线通信', '5G技术'] 
                        }
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
                        { 
                            id: 120101, 
                            name: '视觉传达设计',
                            code: '130502', 
                            duration: 4, 
                            description: '培养视觉传达和数字媒体设计的创意人才', 
                            mainCourses: ['设计基础', '平面设计', 'UI/UX设计', '品牌设计', '广告设计', '包装设计', '数字媒体设计', '交互设计'] 
                        },
                        { 
                            id: 120102, 
                            name: '环境设计', 
                            code: '130503', 
                            duration: 4, 
                            description: '培养室内外环境设计的专业人才', 
                            mainCourses: ['设计素描', '色彩构成', '空间设计', '室内设计', '景观设计', '建筑制图', '材料与工艺', '照明设计'] 
                        }
                    ]
                }
            ]
        }
    ];
    
    occupations = [
        {
            id: 1,
            name: '软件工程师',
            industry: 'IT互联网',
            description: '负责软件系统的设计、开发、测试和维护工作，需要具备扎实的编程基础和良好的逻辑思维能力',
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
            description: '负责数据收集、处理、分析和可视化，为决策提供数据支持，需要统计学基础和编程能力',
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
            name: 'UI/UX设计师',
            industry: 'IT互联网',
            description: '负责用户界面和用户体验设计，提升产品易用性和美观度，需要创意和用户研究能力',
            requirements: ['设计能力', '用户研究', '原型设计', '团队协作'],
            salaryMin: 8000,
            salaryMax: 30000,
            careerPath: [
                { level: '初级', title: 'UI设计师', experienceMin: 0, experienceMax: 2, avgSalary: 10000 },
                { level: '中级', title: '高级UI设计师', experienceMin: 2, experienceMax: 5, avgSalary: 18000 },
                { level: '高级', title: 'UX设计师', experienceMin: 5, experienceMax: 8, avgSalary: 25000 },
                { level: '专家', title: '设计总监', experienceMin: 8, experienceMax: 15, avgSalary: 30000 }
            ]
        },
        {
            id: 4,
            name: '金融分析师',
            industry: '金融服务',
            description: '负责金融市场分析、投资研究和风险评估，为投资决策提供专业建议',
            requirements: ['金融知识', '分析能力', '数学统计', '沟通能力'],
            salaryMin: 15000,
            salaryMax: 60000,
            careerPath: [
                { level: '初级', title: '分析师助理', experienceMin: 0, experienceMax: 2, avgSalary: 18000 },
                { level: '中级', title: '金融分析师', experienceMin: 2, experienceMax: 5, avgSalary: 30000 },
                { level: '高级', title: '高级分析师', experienceMin: 5, experienceMax: 8, avgSalary: 45000 },
                { level: '专家', title: '首席分析师', experienceMin: 8, experienceMax: 15, avgSalary: 60000 }
            ]
        },
        {
            id: 5,
            name: '网络工程师',
            industry: 'IT互联网',
            description: '负责网络系统的设计、实施、维护和优化，确保网络系统的稳定运行',
            requirements: ['网络技术', '系统管理', '安全防护', '故障排查'],
            salaryMin: 10000,
            salaryMax: 35000,
            careerPath: [
                { level: '初级', title: '网络管理员', experienceMin: 0, experienceMax: 2, avgSalary: 12000 },
                { level: '中级', title: '网络工程师', experienceMin: 2, experienceMax: 5, avgSalary: 20000 },
                { level: '高级', title: '高级网络工程师', experienceMin: 5, experienceMax: 8, avgSalary: 28000 },
                { level: '专家', title: '网络架构师', experienceMin: 8, experienceMax: 15, avgSalary: 35000 }
            ]
        },
        {
            id: 6,
            name: '产品经理',
            industry: 'IT互联网',
            description: '负责产品规划、需求分析、项目管理和产品运营，协调各方资源推动产品发展',
            requirements: ['产品思维', '用户研究', '项目管理', '数据分析'],
            salaryMin: 12000,
            salaryMax: 45000,
            careerPath: [
                { level: '初级', title: '产品专员', experienceMin: 0, experienceMax: 2, avgSalary: 14000 },
                { level: '中级', title: '产品经理', experienceMin: 2, experienceMax: 5, avgSalary: 25000 },
                { level: '高级', title: '高级产品经理', experienceMin: 5, experienceMax: 8, avgSalary: 35000 },
                { level: '专家', title: '产品总监', experienceMin: 8, experienceMax: 15, avgSalary: 45000 }
            ]
        }
    ];
}

// 渲染专业树
function renderMajorTree() {
    console.log('[UI] 开始渲染专业树...');
    
    const treeContainer = document.getElementById('majorTree');
    treeContainer.innerHTML = '';
    
    // 确保disciplines是数组
    if (!disciplines || !Array.isArray(disciplines)) {
        console.warn('[UI] disciplines不是数组，无法渲染专业树');
        treeContainer.innerHTML = '<div class="text-center py-8 text-gray-500"><i class="fas fa-exclamation-triangle text-2xl mb-2"></i><p>暂无专业数据</p></div>';
        return;
    }
    
    if (disciplines.length === 0) {
        console.warn('[UI] disciplines为空数组');
        treeContainer.innerHTML = '<div class="text-center py-8 text-gray-500"><i class="fas fa-folder-open text-2xl mb-2"></i><p>暂无专业数据，请先初始化数据库</p></div>';
        return;
    }
    
    console.log('[UI] 渲染专业树，disciplines数量:', disciplines.length);
    
    disciplines.forEach(discipline => {
        const disciplineDiv = document.createElement('div');
        disciplineDiv.className = 'mb-4';
        
        const disciplineHeader = document.createElement('div');
        disciplineHeader.className = 'tree-item p-3 rounded-lg font-semibold text-gray-800 flex items-center justify-between';
        disciplineHeader.innerHTML = `
            <span>${discipline.name}</span>
            <i class="fas fa-chevron-down text-sm transition-transform duration-300"></i>
        `;
        
        const categoriesDiv = document.createElement('div');
        categoriesDiv.className = 'ml-4 mt-2 hidden';
        
        const majorCategories = discipline.majorCategories || [];
        console.log('[UI] 学科门类:', discipline.name, '- 专业类数量:', majorCategories.length);
        
        majorCategories.forEach(category => {
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'mb-3';
            
            const categoryHeader = document.createElement('div');
            categoryHeader.className = 'tree-item p-2 rounded-lg font-medium text-gray-700 flex items-center justify-between';
            categoryHeader.innerHTML = `
                <span class="text-sm">${category.name}</span>
                <i class="fas fa-chevron-down text-xs transition-transform duration-300"></i>
            `;
            
            const majorsDiv = document.createElement('div');
            majorsDiv.className = 'ml-4 mt-1 hidden';
            
            const majors = category.majors || [];
            console.log('[UI]   专业类:', category.name, '- 专业数量:', majors.length);
            
            majors.forEach(major => {
                const majorItem = document.createElement('div');
                majorItem.className = 'tree-item p-2 rounded-lg text-sm text-gray-600 cursor-pointer hover:bg-blue-50';
                majorItem.textContent = major.name;
                majorItem.addEventListener('click', () => selectMajor(major));
                majorsDiv.appendChild(majorItem);
            });
            
            categoryHeader.addEventListener('click', () => toggleTreeItem(categoryHeader, majorsDiv));
            categoryDiv.appendChild(categoryHeader);
            categoryDiv.appendChild(majorsDiv);
            categoriesDiv.appendChild(categoryDiv);
        });
        
        disciplineHeader.addEventListener('click', () => toggleTreeItem(disciplineHeader, categoriesDiv));
        disciplineDiv.appendChild(disciplineHeader);
        disciplineDiv.appendChild(categoriesDiv);
        treeContainer.appendChild(disciplineDiv);
    });
}

// 切换树形项目
function toggleTreeItem(header, content) {
    const icon = header.querySelector('i');
    const isExpanded = !content.classList.contains('hidden');
    
    if (isExpanded) {
        content.classList.add('hidden');
        icon.style.transform = 'rotate(0deg)';
    } else {
        content.classList.remove('hidden');
        icon.style.transform = 'rotate(180deg)';
    }
}

// 选择专业
function selectMajor(major) {
    selectedMajor = major;
    renderMajorDetails(major);
    
    // 更新树项选中状态
    document.querySelectorAll('.tree-item').forEach(item => {
        item.classList.remove('active');
    });
    event.target.classList.add('active');
}

// 渲染专业详情
function renderMajorDetails(major) {
    const detailsContainer = document.getElementById('majorDetails');
    const template = document.getElementById('majorDetailTemplate');
    
    // 克隆模板并显示
    const detailsElement = template.content.cloneNode(true).firstElementChild;
    detailsElement.id = 'majorDetailContent';
    detailsElement.classList.remove('hidden');
    
    // 填充专业信息
    detailsElement.querySelector('#majorName').textContent = major.name;
    detailsElement.querySelector('#majorCode').textContent = `专业代码：${major.code}`;
    detailsElement.querySelector('#majorDuration').textContent = `${major.duration}年制`;
    detailsElement.querySelector('#majorDescription').textContent = major.description;
    
    // 渲染课程
    const coursesContainer = detailsElement.querySelector('#majorCourses');
    const courses = major.mainCourses || [];
    courses.forEach(course => {
        const courseTag = document.createElement('span');
        courseTag.className = 'bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm';
        courseTag.textContent = course;
        coursesContainer.appendChild(courseTag);
    });
    
    // 渲染相关职业
    const relatedOccupations = getRelatedOccupations(major);
    
    const occupationsContainer = detailsElement.querySelector('#relatedOccupations');
    relatedOccupations.forEach(occupation => {
        const occupationCard = document.createElement('div');
        occupationCard.className = 'bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors cursor-pointer';
        occupationCard.innerHTML = `
            <div class="flex items-center justify-between mb-2">
                <h4 class="font-semibold text-gray-800">${occupation.name}</h4>
                <span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">${occupation.industry}</span>
            </div>
            <p class="text-sm text-gray-600 mb-3">${occupation.description}</p>
            <div class="flex items-center justify-between text-sm">
                <span class="text-gray-500">薪资范围：</span>
                <span class="font-medium text-green-600">¥${occupation.salaryMin/1000}k - ¥${occupation.salaryMax/1000}k</span>
            </div>
        `;
        
        occupationCard.addEventListener('click', () => {
            // 跳转到职业详情页
            window.location.href = `major-detail.html?occupation=${occupation.id}`;
        });
        
        occupationsContainer.appendChild(occupationCard);
    });
    
    // 替换内容
    detailsContainer.innerHTML = '';
    detailsContainer.appendChild(detailsElement);
    
    // 添加动画效果
    anime({
        targets: detailsElement,
        opacity: [0, 1],
        translateY: [20, 0],
        duration: 600,
        easing: 'easeOutQuart'
    });
}

// 获取相关职业
function getRelatedOccupations(major) {
    // 根据专业ID匹配相关职业
    const majorOccupationMap = {
        80101: [1, 2], // 计算机科学与技术 -> 软件工程师, 数据分析师
        80102: [1],    // 软件工程 -> 软件工程师
        20101: [4],    // 经济学 -> 金融分析师
        20201: [4],    // 金融学 -> 金融分析师
        120101: [3]    // 视觉传达设计 -> UI/UX设计师
    };
    
    const relatedIds = majorOccupationMap[major.id] || [];
    return occupations.filter(occ => relatedIds.includes(occ.id));
}

// 渲染热门专业
function renderPopularMajors() {
    const container = document.getElementById('popularMajors');
    
    const popularMajors = [
        { id: 80101, name: '计算机科学与技术', category: '工学', description: '最热门的工科专业，就业前景广阔' },
        { id: 20101, name: '经济学', category: '经济学', description: '理论基础扎实，就业面广' },
        { id: 20201, name: '金融学', category: '经济学', description: '金融行业的核心专业，薪资水平较高' },
        { id: 120101, name: '视觉传达设计', category: '艺术学', description: '创意产业发展迅速，需求量大' }
    ];
    
    popularMajors.forEach(major => {
        const majorData = getMajorById(major.id);
        if (majorData) {
            const card = document.createElement('div');
            card.className = 'major-card p-6 cursor-pointer';
            card.innerHTML = `
                <div class="text-center">
                    <div class="w-16 h-16 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <i class="fas fa-graduation-cap text-2xl text-blue-600"></i>
                    </div>
                    <h3 class="font-bold text-gray-800 mb-2">${majorData.name}</h3>
                    <p class="text-sm text-blue-600 mb-3">${major.category}</p>
                    <p class="text-sm text-gray-600 mb-4">${major.description}</p>
                    <button class="btn-primary w-full py-2 text-sm">
                        查看详情
                    </button>
                </div>
            `;
            
            card.addEventListener('click', () => selectMajor(majorData));
            container.appendChild(card);
        }
    });
}

// 根据ID获取专业信息
function getMajorById(id) {
    for (const discipline of disciplines) {
        for (const category of discipline.majorCategories) {
            const major = category.majors.find(m => m.id === id);
            if (major) return major;
        }
    }
    return null;
}

// 设置搜索功能
function setupSearchFunctionality() {
    const searchInput = document.getElementById('searchInput');
    
    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.toLowerCase().trim();
        
        if (query === '') {
            // 恢复原始树形结构
            renderMajorTree();
            return;
        }
        
        // 搜索专业
        const searchResults = searchMajors(query);
        renderSearchResults(searchResults);
    });
}

// 搜索专业
function searchMajors(query) {
    const results = [];
    
    for (const discipline of disciplines) {
        for (const category of discipline.majorCategories) {
            for (const major of category.majors) {
                if (major.name.toLowerCase().includes(query) || 
                    major.description.toLowerCase().includes(query)) {
                    results.push({
                        discipline: discipline.name,
                        category: category.name,
                        major: major
                    });
                }
            }
        }
    }
    
    return results;
}

// 渲染搜索结果
function renderSearchResults(results) {
    const treeContainer = document.getElementById('majorTree');
    treeContainer.innerHTML = '';
    
    if (results.length === 0) {
        treeContainer.innerHTML = `
            <div class="text-center py-8 text-gray-500">
                <i class="fas fa-search text-2xl mb-2"></i>
                <p>未找到相关专业</p>
            </div>
        `;
        return;
    }
    
    const resultsDiv = document.createElement('div');
    resultsDiv.className = 'space-y-2';
    
    results.forEach(result => {
        const resultItem = document.createElement('div');
        resultItem.className = 'tree-item p-3 rounded-lg cursor-pointer';
        resultItem.innerHTML = `
            <div class="font-medium text-gray-800">${result.major.name}</div>
            <div class="text-sm text-gray-600">${result.discipline} · ${result.category}</div>
        `;
        
        resultItem.addEventListener('click', () => selectMajor(result.major));
        resultsDiv.appendChild(resultItem);
    });
    
    treeContainer.appendChild(resultsDiv);
}

// 设置滚动动画
function setupScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);
    
    document.querySelectorAll('.fade-in').forEach(el => {
        observer.observe(el);
    });
}

// 新增专业显示功能
let newlyAddedMajors = [];

// 添加新专业到显示列表
function addNewMajorToDisplay(major) {
    newlyAddedMajors.push(major);
    updateNewlyAddedMajorsDisplay();
}

// 更新新增专业显示
function updateNewlyAddedMajorsDisplay() {
    const container = document.getElementById('newlyAddedMajors');
    if (!container) return;
    
    // 清除现有内容
    container.innerHTML = '';
    
    if (newlyAddedMajors.length === 0) return;
    
    const title = document.createElement('h3');
    title.className = 'text-lg font-bold text-gray-800 mb-4';
    title.innerHTML = '<i class="fas fa-plus-circle text-green-500 mr-2"></i>最新添加的专业';
    container.appendChild(title);
    
    const grid = document.createElement('div');
    grid.className = 'grid grid-cols-1 gap-4';
    
    newlyAddedMajors.slice(-3).forEach(major => {
        const card = document.createElement('div');
        card.className = 'bg-green-50 border border-green-200 rounded-lg p-4 cursor-pointer hover:bg-green-100 transition-colors';
        card.innerHTML = `
            <div class="flex items-center justify-between">
                <div>
                    <h4 class="font-semibold text-gray-800">${major.name}</h4>
                    <p class="text-sm text-gray-600">${major.description.substring(0, 50)}...</p>
                </div>
                <span class="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">新增</span>
            </div>
        `;
        card.addEventListener('click', () => selectMajor(major));
        grid.appendChild(card);
    });
    
    container.appendChild(grid);
    
    // 添加动画效果
    anime({
        targets: container,
        opacity: [0, 1],
        translateY: [20, 0],
        duration: 600,
        easing: 'easeOutQuart'
    });
}

// 导出全局函数供HTML调用
window.selectMajor = selectMajor;
window.toggleTreeItem = toggleTreeItem;
window.addNewMajorToDisplay = addNewMajorToDisplay;