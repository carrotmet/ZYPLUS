// 信息管理页面JavaScript逻辑

let currentFormType = 'major';
let majorCourses = [];
let occupationRequirements = [];

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializePage();
});

// 初始化页面
function initializePage() {
    setupFormHandlers();
    setupTagInputs();
    setupScrollAnimations();
    setupRealTimePreview();
    
    // 添加页面加载动画
    anime({
        targets: '.fade-in',
        opacity: [0, 1],
        translateY: [20, 0],
        duration: 800,
        delay: anime.stagger(200),
        easing: 'easeOutQuart'
    });
}

// 切换表单类型
function toggleForm(type) {
    currentFormType = type;
    
    // 更新按钮状态
    document.querySelectorAll('.toggle-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // 隐藏所有表单
    document.getElementById('majorForm').classList.add('hidden');
    document.getElementById('occupationForm').classList.add('hidden');
    document.getElementById('experienceForm').classList.add('hidden');
    
    if (type === 'major') {
        document.getElementById('majorBtn').classList.add('active');
        document.getElementById('majorForm').classList.remove('hidden');
    } else if (type === 'occupation') {
        document.getElementById('occupationBtn').classList.add('active');
        document.getElementById('occupationForm').classList.remove('hidden');
    } else {
        document.getElementById('experienceBtn').classList.add('active');
        document.getElementById('experienceForm').classList.remove('hidden');
    }
    
    // 清空预览
    clearPreview();
}

// 设置表单处理器
function setupFormHandlers() {
    // 专业表单
    document.getElementById('majorInfoForm').addEventListener('submit', function(e) {
        e.preventDefault();
        submitMajorForm();
    });
    
    // 职业表单
    document.getElementById('occupationInfoForm').addEventListener('submit', function(e) {
        e.preventDefault();
        submitOccupationForm();
    });
    
    // 个人经历表单
    document.getElementById('experienceInfoForm').addEventListener('submit', function(e) {
        e.preventDefault();
        submitExperienceForm();
    });
}

// 设置标签输入
function setupTagInputs() {
    // 专业课程标签
    const majorCourseInput = document.getElementById('majorCourseInput');
    majorCourseInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const value = this.value.trim();
            if (value) {
                addMajorCourse(value);
                this.value = '';
            }
        }
    });
    
    // 职业要求标签
    const occupationRequirementInput = document.getElementById('occupationRequirementInput');
    occupationRequirementInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const value = this.value.trim();
            if (value) {
                addOccupationRequirement(value);
                this.value = '';
            }
        }
    });
}

// 设置实时预览
function setupRealTimePreview() {
    // 专业表单实时预览
    document.getElementById('majorName').addEventListener('input', updateMajorPreview);
    document.getElementById('majorDescription').addEventListener('input', updateMajorPreview);
    document.getElementById('majorDiscipline').addEventListener('change', updateMajorPreview);
    document.getElementById('majorDuration').addEventListener('change', updateMajorPreview);
    
    // 职业表单实时预览
    document.getElementById('occupationName').addEventListener('input', updateOccupationPreview);
    document.getElementById('occupationDescription').addEventListener('input', updateOccupationPreview);
    document.getElementById('occupationIndustry').addEventListener('change', updateOccupationPreview);
    document.getElementById('salaryMin').addEventListener('input', updateOccupationPreview);
    document.getElementById('salaryMax').addEventListener('input', updateOccupationPreview);
    
    // 个人经历表单实时预览
    document.getElementById('experienceNickname').addEventListener('input', updateExperiencePreview);
    document.getElementById('experienceDetail').addEventListener('input', updateExperiencePreview);
    document.getElementById('experienceEducation').addEventListener('change', updateExperiencePreview);
    document.getElementById('experienceMajor').addEventListener('change', updateExperiencePreview);
    document.getElementById('experienceSchool').addEventListener('input', updateExperiencePreview);
    document.getElementById('experienceDegree').addEventListener('input', updateExperiencePreview);
}

// 添加专业课程
function addMajorCourse(course) {
    if (majorCourses.includes(course)) return;
    
    majorCourses.push(course);
    updateMajorCoursesDisplay();
    updateMajorPreview();
}

// 移除专业课程
function removeMajorCourse(course) {
    majorCourses = majorCourses.filter(c => c !== course);
    updateMajorCoursesDisplay();
    updateMajorPreview();
}

// 更新专业课程显示
function updateMajorCoursesDisplay() {
    const container = document.getElementById('majorCoursesContainer');
    const input = container.querySelector('input');
    
    // 清除现有标签
    container.querySelectorAll('.tag').forEach(tag => tag.remove());
    
    // 添加标签
    majorCourses.forEach(course => {
        const tag = document.createElement('div');
        tag.className = 'tag';
        
        // 安全地转义特殊字符
        const escapedCourse = course.replace(/'/g, "\\'").replace(/"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        const courseText = document.createTextNode(course);
        const button = document.createElement('button');
        button.type = 'button';
        button.textContent = '×';
        button.addEventListener('click', () => removeMajorCourse(course));
        
        tag.appendChild(courseText);
        tag.appendChild(button);
        container.insertBefore(tag, input);
    });
}

// 添加职业要求
function addOccupationRequirement(requirement) {
    if (occupationRequirements.includes(requirement)) return;
    
    occupationRequirements.push(requirement);
    updateOccupationRequirementsDisplay();
    updateOccupationPreview();
}

// 移除职业要求
function removeOccupationRequirement(requirement) {
    occupationRequirements = occupationRequirements.filter(r => r !== requirement);
    updateOccupationRequirementsDisplay();
    updateOccupationPreview();
}

// 更新职业要求显示
function updateOccupationRequirementsDisplay() {
    const container = document.getElementById('occupationRequirementsContainer');
    const input = container.querySelector('input');
    
    // 清除现有标签
    container.querySelectorAll('.tag').forEach(tag => tag.remove());
    
    // 添加标签
    occupationRequirements.forEach(requirement => {
        const tag = document.createElement('div');
        tag.className = 'tag';
        
        // 安全地创建元素
        const requirementText = document.createTextNode(requirement);
        const button = document.createElement('button');
        button.type = 'button';
        button.textContent = '×';
        button.addEventListener('click', () => removeOccupationRequirement(requirement));
        
        tag.appendChild(requirementText);
        tag.appendChild(button);
        container.insertBefore(tag, input);
    });
}

// 更新专业预览
function updateMajorPreview() {
    if (currentFormType !== 'major') return;
    
    const name = document.getElementById('majorName').value;
    const description = document.getElementById('majorDescription').value;
    const discipline = document.getElementById('majorDiscipline').value;
    const duration = document.getElementById('majorDuration').value;
    
    if (!name && !description) {
        clearPreview();
        return;
    }
    
    const previewCard = document.getElementById('previewCard');
    previewCard.classList.add('has-content');
    
    previewCard.innerHTML = `
        <div class="w-full">
            <div class="flex items-start justify-between mb-4">
                <div>
                    <h3 class="text-xl font-bold text-gray-800 mb-1">${name || '专业名称'}</h3>
                    <p class="text-sm text-blue-600">${discipline || '学科门类'}</p>
                </div>
                ${duration ? `<span class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">${duration}年制</span>` : ''}
            </div>
            
            ${description ? `<p class="text-gray-600 text-sm mb-4 leading-relaxed">${description}</p>` : ''}
            
            ${majorCourses.length > 0 ? `
                <div>
                    <h4 class="text-sm font-semibold text-gray-800 mb-2">主要课程：</h4>
                    <div class="flex flex-wrap gap-1">
                        ${majorCourses.map(course => 
                            `<span class="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">${course}</span>`
                        ).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;
}

// 更新职业预览
function updateOccupationPreview() {
    if (currentFormType !== 'occupation') return;
    
    const name = document.getElementById('occupationName').value;
    const description = document.getElementById('occupationDescription').value;
    const industry = document.getElementById('occupationIndustry').value;
    const salaryMin = document.getElementById('salaryMin').value;
    const salaryMax = document.getElementById('salaryMax').value;
    
    if (!name && !description) {
        clearPreview();
        return;
    }
    
    const previewCard = document.getElementById('previewCard');
    previewCard.classList.add('has-content');
    
    previewCard.innerHTML = `
        <div class="w-full">
            <div class="flex items-start justify-between mb-4">
                <div>
                    <h3 class="text-xl font-bold text-gray-800 mb-1">${name || '职业名称'}</h3>
                    <p class="text-sm text-blue-600">${industry || '所属行业'}</p>
                </div>
                ${salaryMin && salaryMax ? 
                    `<div class="text-right">
                        <div class="text-lg font-bold text-green-600">¥${parseInt(salaryMin)/1000}k - ¥${parseInt(salaryMax)/1000}k</div>
                        <div class="text-xs text-gray-500">月薪范围</div>
                    </div>` : ''
                }
            </div>
            
            ${description ? `<p class="text-gray-600 text-sm mb-4 leading-relaxed">${description}</p>` : ''}
            
            ${occupationRequirements.length > 0 ? `
                <div>
                    <h4 class="text-sm font-semibold text-gray-800 mb-2">核心要求：</h4>
                    <div class="flex flex-wrap gap-1">
                        ${occupationRequirements.map(req => 
                            `<span class="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">${req}</span>`
                        ).join('')}
                    </div>
                </div>
            ` : ''}
        </div>
    `;
}

// 更新个人经历预览
function updateExperiencePreview() {
    if (currentFormType !== 'experience') return;
    
    const nickname = document.getElementById('experienceNickname').value;
    const education = document.getElementById('experienceEducation').value;
    const major = document.getElementById('experienceMajor');
    const majorText = major.options[major.selectedIndex]?.text || '';
    const school = document.getElementById('experienceSchool').value;
    const degree = document.getElementById('experienceDegree').value;
    const experience = document.getElementById('experienceDetail').value;
    const isAnonymous = document.getElementById('experienceAnonymous').checked;
    
    if (!nickname && !experience) {
        clearPreview();
        return;
    }
    
    const previewCard = document.getElementById('previewCard');
    previewCard.classList.add('has-content');
    
    const displayName = isAnonymous ? '匿名用户' : (nickname || '用户昵称');
    
    previewCard.innerHTML = `
        <div class="w-full">
            <div class="flex items-center justify-between mb-4">
                <div class="flex items-center">
                    <div class="w-12 h-12 bg-gradient-to-br from-purple-100 to-pink-100 rounded-full flex items-center justify-center mr-3">
                        <i class="fas fa-user text-purple-600"></i>
                    </div>
                    <div>
                        <h3 class="text-lg font-bold text-gray-800">${displayName}</h3>
                        <p class="text-sm text-gray-600">${education || '学历'} · ${majorText || '专业'}</p>
                    </div>
                </div>
                ${isAnonymous ? '<span class="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">匿名</span>' : ''}
            </div>
            
            ${school ? `<p class="text-sm text-gray-600 mb-2"><i class="fas fa-school mr-2"></i>${school}</p>` : ''}
            ${degree ? `<p class="text-sm text-gray-600 mb-4"><i class="fas fa-graduation-cap mr-2"></i>${degree}</p>` : ''}
            
            ${experience ? `
                <div>
                    <h4 class="text-sm font-semibold text-gray-800 mb-2">个人经历：</h4>
                    <p class="text-sm text-gray-600 leading-relaxed">${experience}</p>
                </div>
            ` : ''}
        </div>
    `;
}

// 清空预览
function clearPreview() {
    const previewCard = document.getElementById('previewCard');
    previewCard.classList.remove('has-content');
    previewCard.innerHTML = `
        <div class="text-center text-gray-500">
            <i class="fas fa-pencil-alt text-4xl mb-4"></i>
            <p>填写左侧表单查看预览效果</p>
        </div>
    `;
}

// 提交专业表单
async function submitMajorForm() {
    const name = document.getElementById('majorName').value;
    const code = document.getElementById('majorCode').value;
    const discipline = document.getElementById('majorDiscipline').value;
    const duration = document.getElementById('majorDuration').value;
    const description = document.getElementById('majorDescription').value;
    
    if (!name || !discipline || !duration || !description || majorCourses.length === 0) {
        showError('请填写完整的专业信息，包括至少一门课程！');
        return;
    }
    
    const majorData = {
        name,
        code,
        discipline,
        duration: parseInt(duration),
        description,
        courses: majorCourses
    };
    
    try {
        let createdMajor;
        if (window.apiService) {
            const result = await window.apiService.createMajor(majorData);
            createdMajor = result;
            showSuccess('专业信息添加成功！感谢您的贡献。');
        } else {
            // 模拟数据创建
            createdMajor = {
                id: Date.now(),
                ...majorData,
                created_at: new Date().toISOString()
            };
            showSuccess('专业信息添加成功！(模拟数据)');
        }
        
        // 添加到主页显示
        if (window.opener && window.opener.addNewMajorToDisplay) {
            window.opener.addNewMajorToDisplay(createdMajor);
        } else if (window.addNewMajorToDisplay) {
            window.addNewMajorToDisplay(createdMajor);
        }
        
        // 重置表单
        setTimeout(() => {
            resetMajorForm();
        }, 2000);
    } catch (error) {
        showError('提交失败，请重试！');
    }
}

// 提交职业表单
async function submitOccupationForm() {
    const name = document.getElementById('occupationName').value;
    const industry = document.getElementById('occupationIndustry').value;
    const salaryMin = document.getElementById('salaryMin').value;
    const salaryMax = document.getElementById('salaryMax').value;
    const description = document.getElementById('occupationDescription').value;
    
    if (!name || !industry || !salaryMin || !salaryMax || !description || occupationRequirements.length === 0) {
        showError('请填写完整的职业信息，包括至少一项核心要求！');
        return;
    }
    
    if (parseInt(salaryMin) >= parseInt(salaryMax)) {
        showError('最高薪资必须高于最低薪资！');
        return;
    }
    
    const occupationData = {
        name,
        industry,
        salary_min: parseInt(salaryMin),
        salary_max: parseInt(salaryMax),
        description,
        requirements: occupationRequirements
    };
    
    try {
        let createdOccupation;
        if (window.apiService) {
            const result = await window.apiService.createOccupation(occupationData);
            createdOccupation = result;
            showSuccess('职业信息添加成功！感谢您的贡献。');
        } else {
            // 模拟数据创建
            createdOccupation = {
                id: Date.now(),
                ...occupationData,
                salaryMin: occupationData.salary_min,
                salaryMax: occupationData.salary_max,
                created_at: new Date().toISOString()
            };
            showSuccess('职业信息添加成功！(模拟数据)');
        }
        
        // 添加到职业详情页显示
        if (window.opener && window.opener.addNewOccupationToDisplay) {
            window.opener.addNewOccupationToDisplay(createdOccupation);
        } else if (window.addNewOccupationToDisplay) {
            window.addNewOccupationToDisplay(createdOccupation);
        }
        
        // 重置表单
        setTimeout(() => {
            resetOccupationForm();
        }, 2000);
    } catch (error) {
        showError('提交失败，请重试！');
    }
}

// 提交个人经历表单
async function submitExperienceForm() {
    const nickname = document.getElementById('experienceNickname').value;
    const education = document.getElementById('experienceEducation').value;
    const majorId = document.getElementById('experienceMajor').value;
    const schoolName = document.getElementById('experienceSchool').value;
    const degree = document.getElementById('experienceDegree').value;
    const experience = document.getElementById('experienceDetail').value;
    const isAnonymous = document.getElementById('experienceAnonymous').checked;
    
    if (!nickname || !education || !majorId || !schoolName || !experience) {
        showError('请填写完整的个人经历信息！');
        return;
    }
    
    const experienceData = {
        nickname,
        major_id: parseInt(majorId),
        education,
        school_name: schoolName,
        degree,
        experience,
        is_anonymous: isAnonymous
    };
    
    try {
        let createdExperience;
        if (window.apiService) {
            const result = await window.apiService.createPersonalExperience(experienceData);
            createdExperience = result;
            showSuccess('个人经历添加成功！感谢您的分享。');
        } else {
            // 模拟数据创建
            createdExperience = {
                id: Date.now(),
                ...experienceData,
                major_name: document.getElementById('experienceMajor').options[document.getElementById('experienceMajor').selectedIndex].text,
                created_at: new Date().toISOString()
            };
            showSuccess('个人经历添加成功！(模拟数据)');
        }
        
        // 添加到经历分享页面显示
        if (window.opener && window.opener.addNewExperienceToDisplay) {
            window.opener.addNewExperienceToDisplay(createdExperience);
        } else if (window.addNewExperienceToDisplay) {
            window.addNewExperienceToDisplay(createdExperience);
        }
        
        // 重置表单
        setTimeout(() => {
            resetExperienceForm();
        }, 2000);
    } catch (error) {
        showError('提交失败，请重试！');
    }
}

// 重置专业表单
function resetMajorForm() {
    document.getElementById('majorInfoForm').reset();
    majorCourses = [];
    updateMajorCoursesDisplay();
    clearPreview();
    hideMessages();
}

// 重置职业表单
function resetOccupationForm() {
    document.getElementById('occupationInfoForm').reset();
    occupationRequirements = [];
    updateOccupationRequirementsDisplay();
    clearPreview();
    hideMessages();
}

// 重置个人经历表单
function resetExperienceForm() {
    document.getElementById('experienceInfoForm').reset();
    clearPreview();
    hideMessages();
}

// 显示成功消息
function showSuccess(message) {
    const successMessage = document.getElementById('successMessage');
    const successText = document.getElementById('successText');
    
    successText.textContent = message;
    successMessage.style.display = 'block';
    
    // 自动隐藏
    setTimeout(() => {
        successMessage.style.display = 'none';
    }, 5000);
}

// 显示错误消息
function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    const errorText = document.getElementById('errorText');
    
    errorText.textContent = message;
    errorMessage.style.display = 'block';
    
    // 自动隐藏
    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 5000);
}

// 隐藏消息
function hideMessages() {
    document.getElementById('successMessage').style.display = 'none';
    document.getElementById('errorMessage').style.display = 'none';
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