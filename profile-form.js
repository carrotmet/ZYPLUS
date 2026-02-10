/**
 * 用户画像表单模块 - Profile Form Module
 * 
 * 功能：
 * 1. 提供独立的用户画像结构化数据编辑表单
 * 2. 支持用户主动调用（点击按钮打开表单）
 * 3. 支持AI隐式调用（通过API直接提交）
 * 4. 表单提交后自动更新数据库和UI
 * 
 * 设计理念：
 * - 模块独立：不依赖具体页面，可在任何页面引入使用
 * - 双向调用：支持用户交互和程序化调用
 * - 可扩展：易于添加新的表单字段
 */

// ==================== 配置 ====================
const PROFILE_FORM_CONFIG = {
    API_BASE_URL: 'http://localhost:8000/api',
    // 字段分类配置
    fields: {
        // 可选项 - 有预设选项的字段
        selectable: {
            holland_code: {
                label: '霍兰德代码',
                type: 'select',
                placeholder: '选择你的霍兰德代码',
                description: '如：RIA、SEC等，不了解可跳过',
                options: [
                    { value: '', label: '未设置' },
                    { value: 'RIA', label: 'RIA - 实用型+研究型+艺术型' },
                    { value: 'RIS', label: 'RIS - 实用型+研究型+社会型' },
                    { value: 'RIE', label: 'RIE - 实用型+研究型+企业型' },
                    { value: 'SEC', label: 'SEC - 社会型+企业型+常规型' },
                    { value: 'SIA', label: 'SIA - 社会型+研究型+艺术型' },
                    { value: 'SAE', label: 'SAE - 社会型+艺术型+企业型' },
                    { value: 'EIS', label: 'EIS - 企业型+研究型+社会型' },
                    { value: 'ECS', label: 'ECS - 企业型+常规型+社会型' },
                    { value: 'CAS', label: 'CAS - 常规型+艺术型+社会型' },
                    { value: 'CIE', label: 'CIE - 常规型+研究型+企业型' },
                    { value: 'AIS', label: 'AIS - 艺术型+研究型+社会型' },
                    { value: 'AEC', label: 'AEC - 艺术型+企业型+常规型' },
                ]
            },
            mbti_type: {
                label: 'MBTI类型',
                type: 'select',
                placeholder: '选择你的MBTI类型',
                description: '如：INTJ、ENFP等，不了解可跳过',
                options: [
                    { value: '', label: '未设置' },
                    { value: 'INTJ', label: 'INTJ - 建筑师' },
                    { value: 'INTP', label: 'INTP - 逻辑学家' },
                    { value: 'ENTJ', label: 'ENTJ - 指挥官' },
                    { value: 'ENTP', label: 'ENTP - 辩论家' },
                    { value: 'INFJ', label: 'INFJ - 提倡者' },
                    { value: 'INFP', label: 'INFP - 调停者' },
                    { value: 'ENFJ', label: 'ENFJ - 主人公' },
                    { value: 'ENFP', label: 'ENFP - 竞选者' },
                    { value: 'ISTJ', label: 'ISTJ - 检查员' },
                    { value: 'ISFJ', label: 'ISFJ - 保护者' },
                    { value: 'ESTJ', label: 'ESTJ - 总经理' },
                    { value: 'ESFJ', label: 'ESFJ - ' },
                    { value: 'ISTP', label: 'ISTP - 鉴赏家' },
                    { value: 'ISFP', label: 'ISFP - 探险家' },
                    { value: 'ESTP', label: 'ESTP - 企业家' },
                    { value: 'ESFP', label: 'ESFP - 表演者' },
                ]
            },
            career_path_preference: {
                label: '职业路径偏好',
                type: 'select',
                placeholder: '选择你偏好的职业发展路径',
                description: '你更倾向于哪种职业发展方向？',
                options: [
                    { value: '', label: '未设置' },
                    { value: 'technical', label: '技术专家路径 - 深耕专业技术领域' },
                    { value: 'management', label: '管理领导路径 - 带领团队达成目标' },
                    { value: 'professional', label: '专业方向路径 - 成为行业专家/顾问' },
                    { value: 'public_welfare', label: '公益方向路径 - 服务社会、帮助他人' },
                ]
            },
            current_casve_stage: {
                label: '当前决策阶段',
                type: 'select',
                placeholder: '你目前处于哪个决策阶段？',
                description: 'CASVE决策模型阶段',
                options: [
                    { value: 'communication', label: 'C-沟通 - 识别决策需求，感知理想与现实差距' },
                    { value: 'analysis', label: 'A-分析 - 系统梳理自我认知与选项信息' },
                    { value: 'synthesis', label: 'S-综合 - 生成可能的解决方案' },
                    { value: 'evaluation', label: 'V-评估 - 权衡各选项的优劣后果' },
                    { value: 'execution', label: 'E-执行 - 将选择转化为行动计划' },
                ]
            }
        },
        // 可填项 - 需要用户输入的字段
        fillable: {
            value_priorities: {
                label: '价值观优先级',
                type: 'multi-select',
                placeholder: '选择你最看重的价值观（可多选）',
                description: '工作中你最看重什么？',
                options: [
                    { value: '成就感', label: '成就感 - 实现自我价值' },
                    { value: '稳定', label: '稳定 - 工作安稳、有保障' },
                    { value: '创新', label: '创新 - 创造新事物、有新鲜感' },
                    { value: '自由', label: '自由 - 灵活自主、不受约束' },
                    { value: '收入', label: '收入 - 高薪资、好待遇' },
                    { value: '平衡', label: '平衡 - 工作生活平衡' },
                    { value: '成长', label: '成长 - 学习进步、能力提升' },
                    { value: '影响', label: '影响 - 改变他人、贡献社会' },
                    { value: '帮助', label: '帮助 - 服务他人、关怀他人' },
                ],
                max: 5
            },
            ability_assessment: {
                label: '能力自评',
                type: 'slider-group',
                description: '请为你的各项能力打分（1-10分）',
                sliders: [
                    { key: 'logic', label: '逻辑推理', min: 1, max: 10 },
                    { key: 'creativity', label: '创造力', min: 1, max: 10 },
                    { key: 'communication', label: '沟通能力', min: 1, max: 10 },
                    { key: 'teamwork', label: '团队协作', min: 1, max: 10 },
                    { key: 'leadership', label: '领导力', min: 1, max: 10 },
                    { key: 'analysis', label: '分析能力', min: 1, max: 10 },
                ]
            },
            universal_skills: {
                label: '通用技能',
                type: 'slider-group',
                description: '请为你的通用技能打分（1-10分）',
                sliders: [
                    { key: 'communication', label: '沟通表达', min: 1, max: 10 },
                    { key: 'teamwork', label: '团队协作', min: 1, max: 10 },
                    { key: 'critical_thinking', label: '批判思维', min: 1, max: 10 },
                    { key: 'creativity', label: '创造力', min: 1, max: 10 },
                    { key: 'problem_solving', label: '问题解决', min: 1, max: 10 },
                    { key: 'adaptability', label: '适应能力', min: 1, max: 10 },
                ]
            },
            resilience_score: {
                label: '职业弹性',
                type: 'slider',
                description: '你认为自己应对职业挫折的能力有多强？（1-10分）',
                min: 1,
                max: 10
            }
        }
    }
};

// ==================== 表单状态管理 ====================
const ProfileFormState = {
    isOpen: false,
    currentData: {},
    originalData: {},
    userId: null,
    onSubmitCallback: null,
    
    // 深拷贝辅助函数
    _deepCopy(obj) {
        if (obj === null || typeof obj !== 'object') return obj;
        if (Array.isArray(obj)) return obj.map(item => this._deepCopy(item));
        const copy = {};
        for (const key in obj) {
            if (obj.hasOwnProperty(key)) {
                copy[key] = this._deepCopy(obj[key]);
            }
        }
        return copy;
    },
    
    init(userId, initialData = {}) {
        this.userId = userId;
        // 使用深拷贝避免对象引用问题
        this.originalData = this._deepCopy(initialData);
        this.currentData = this._deepCopy(initialData);
    },
    
    updateField(field, value) {
        this.currentData[field] = value;
    },
    
    getChanges() {
        const changes = {};
        console.log('[ProfileFormState] Checking changes...');
        console.log('  currentData:', this.currentData);
        console.log('  originalData:', this.originalData);
        for (const key in this.currentData) {
            const currentVal = this.currentData[key];
            const originalVal = this.originalData[key];
            const isDifferent = JSON.stringify(currentVal) !== JSON.stringify(originalVal);
            console.log(`  ${key}: current=${JSON.stringify(currentVal)}, original=${JSON.stringify(originalVal)}, changed=${isDifferent}`);
            if (isDifferent) {
                changes[key] = currentVal;
            }
        }
        console.log('[ProfileFormState] Changes detected:', changes);
        return changes;
    },
    
    hasChanges() {
        return Object.keys(this.getChanges()).length > 0;
    },
    
    reset() {
        this.currentData = this._deepCopy(this.originalData);
    }
};

// ==================== 表单渲染器 ====================
const ProfileFormRenderer = {
    // 创建表单HTML
    createFormHTML() {
        const config = PROFILE_FORM_CONFIG.fields;
        
        return `
            <div id="profile-form-overlay" class="fixed inset-0 bg-black bg-opacity-50 z-50 hidden flex items-center justify-center p-4">
                <div id="profile-form-container" class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col">
                    <!-- 头部 -->
                    <div class="bg-gradient-to-r from-blue-500 to-blue-600 px-6 py-4 flex justify-between items-center">
                        <div class="flex items-center text-white">
                            <i class="fas fa-edit text-xl mr-3"></i>
                            <div>
                                <h3 class="font-semibold">完善用户画像</h3>
                                <p class="text-xs text-blue-100">填写你的职业规划相关信息</p>
                            </div>
                        </div>
                        <button onclick="ProfileForm.close()" class="text-white hover:text-blue-100 transition-colors">
                            <i class="fas fa-times text-xl"></i>
                        </button>
                    </div>
                    
                    <!-- 表单内容 -->
                    <div class="flex-1 overflow-y-auto p-6">
                        <!-- 可选项区域 -->
                        <div class="mb-8">
                            <h4 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4 flex items-center">
                                <i class="fas fa-list-check mr-2"></i>可选信息（测试工具结果）
                            </h4>
                            <div class="space-y-4">
                                ${this.renderSelectableFields(config.selectable)}
                            </div>
                        </div>
                        
                        <!-- 可填项区域 -->
                        <div>
                            <h4 class="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4 flex items-center">
                                <i class="fas fa-pen-to-square mr-2"></i>可填信息（自我评估）
                            </h4>
                            <div class="space-y-6">
                                ${this.renderFillableFields(config.fillable)}
                            </div>
                        </div>
                    </div>
                    
                    <!-- 底部按钮 -->
                    <div class="border-t px-6 py-4 bg-gray-50 flex justify-between items-center">
                        <button onclick="ProfileForm.reset()" class="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors">
                            <i class="fas fa-rotate-left mr-2"></i>重置
                        </button>
                        <div class="space-x-3">
                            <button onclick="ProfileForm.close()" class="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-100 transition-colors">
                                取消
                            </button>
                            <button onclick="ProfileForm.submit()" id="profile-form-submit" class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors flex items-center">
                                <i class="fas fa-save mr-2"></i>保存
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },
    
    // 渲染可选项字段
    renderSelectableFields(fields) {
        return Object.entries(fields).map(([key, config]) => {
            return `
                <div class="form-field-group">
                    <label class="block text-sm font-medium text-gray-700 mb-1">
                        ${config.label}
                        <span class="text-xs text-gray-400 ml-1">(可选)</span>
                    </label>
                    <p class="text-xs text-gray-500 mb-2">${config.description}</p>
                    <select 
                        id="form-field-${key}" 
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        onchange="ProfileForm.handleFieldChange('${key}', this.value)"
                    >
                        ${config.options.map(opt => `
                            <option value="${opt.value}">${opt.label}</option>
                        `).join('')}
                    </select>
                </div>
            `;
        }).join('');
    },
    
    // 渲染可填项字段
    renderFillableFields(fields) {
        return Object.entries(fields).map(([key, config]) => {
            if (config.type === 'multi-select') {
                return this.renderMultiSelectField(key, config);
            } else if (config.type === 'slider-group') {
                return this.renderSliderGroupField(key, config);
            } else if (config.type === 'slider') {
                return this.renderSliderField(key, config);
            }
            return '';
        }).join('');
    },
    
    // 渲染多选字段
    renderMultiSelectField(key, config) {
        return `
            <div class="form-field-group">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                    ${config.label}
                </label>
                <p class="text-xs text-gray-500 mb-2">${config.description}</p>
                <div class="flex flex-wrap gap-2" id="form-field-${key}-container">
                    ${config.options.map(opt => `
                        <button 
                            type="button"
                            class="multi-select-option px-3 py-1.5 rounded-full border border-gray-300 text-sm transition-colors hover:border-blue-400"
                            data-value="${opt.value}"
                            onclick="ProfileForm.handleMultiSelect('${key}', '${opt.value}', this)"
                        >
                            ${opt.label}
                        </button>
                    `).join('')}
                </div>
                <input type="hidden" id="form-field-${key}" value="">
            </div>
        `;
    },
    
    // 渲染滑块组字段
    renderSliderGroupField(key, config) {
        return `
            <div class="form-field-group bg-gray-50 rounded-lg p-4">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                    ${config.label}
                </label>
                <p class="text-xs text-gray-500 mb-4">${config.description}</p>
                <div class="space-y-4">
                    ${config.sliders.map(slider => `
                        <div class="slider-item">
                            <div class="flex justify-between mb-1">
                                <span class="text-sm text-gray-600">${slider.label}</span>
                                <span class="text-sm font-medium text-blue-600" id="form-field-${key}-${slider.key}-value">5</span>
                            </div>
                            <input 
                                type="range" 
                                id="form-field-${key}-${slider.key}"
                                min="${slider.min}" 
                                max="${slider.max}" 
                                value="5"
                                class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-500"
                                oninput="ProfileForm.handleSliderGroupChange('${key}', '${slider.key}', this.value)"
                            >
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    },
    
    // 渲染单个滑块字段
    renderSliderField(key, config) {
        return `
            <div class="form-field-group">
                <label class="block text-sm font-medium text-gray-700 mb-1">
                    ${config.label}
                </label>
                <p class="text-xs text-gray-500 mb-2">${config.description}</p>
                <div class="flex items-center space-x-4">
                    <span class="text-sm text-gray-500">${config.min}</span>
                    <input 
                        type="range" 
                        id="form-field-${key}"
                        min="${config.min}" 
                        max="${config.max}" 
                        value="5"
                        class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-500"
                        oninput="ProfileForm.handleSliderChange('${key}', this.value)"
                    >
                    <span class="text-sm text-gray-500">${config.max}</span>
                    <span class="text-lg font-medium text-blue-600 w-8 text-center" id="form-field-${key}-display">5</span>
                </div>
            </div>
        `;
    }
};

// ==================== 表单主控制器 ====================
const ProfileForm = {
    // 初始化表单模块
    init(userId, initialData = {}) {
        ProfileFormState.init(userId, initialData);
        
        // 如果表单DOM不存在，则创建
        if (!document.getElementById('profile-form-overlay')) {
            this.injectFormDOM();
        }
        
        console.log('[ProfileForm] Initialized with userId:', userId);
    },
    
    // 注入表单DOM到页面
    injectFormDOM() {
        const formHTML = ProfileFormRenderer.createFormHTML();
        const div = document.createElement('div');
        div.id = 'profile-form-module';
        div.innerHTML = formHTML;
        document.body.appendChild(div);
        
        // 添加样式
        this.injectStyles();
    },
    
    // 注入样式
    injectStyles() {
        if (document.getElementById('profile-form-styles')) return;
        
        const styles = document.createElement('style');
        styles.id = 'profile-form-styles';
        styles.textContent = `
            #profile-form-overlay {
                animation: fadeIn 0.2s ease;
            }
            #profile-form-container {
                animation: slideUp 0.3s ease;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes slideUp {
                from { transform: translateY(20px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            .multi-select-option.selected {
                background-color: #3B82F6;
                color: white;
                border-color: #3B82F6;
            }
            .form-field-group {
                transition: all 0.2s ease;
            }
            .form-field-group:focus-within {
                transform: translateX(4px);
            }
            input[type="range"]::-webkit-slider-thumb {
                width: 16px;
                height: 16px;
                border-radius: 50%;
                background: #3B82F6;
                cursor: pointer;
            }
        `;
        document.head.appendChild(styles);
    },
    
    // 打开表单（用户主动调用）
    open(userId, initialData = {}, onSubmit = null) {
        this.init(userId, initialData);
        ProfileFormState.onSubmitCallback = onSubmit;
        
        const overlay = document.getElementById('profile-form-overlay');
        if (overlay) {
            overlay.classList.remove('hidden');
            ProfileFormState.isOpen = true;
            this.populateFormValues(initialData);
        }
    },
    
    // 关闭表单
    close() {
        const overlay = document.getElementById('profile-form-overlay');
        if (overlay) {
            overlay.classList.add('hidden');
            ProfileFormState.isOpen = false;
        }
    },
    
    // 填充表单值
    populateFormValues(data) {
        // 填充可选项
        Object.keys(PROFILE_FORM_CONFIG.fields.selectable).forEach(key => {
            const el = document.getElementById(`form-field-${key}`);
            if (el && data[key]) {
                el.value = data[key];
            }
        });
        
        // 填充多选
        if (data.value_priorities && Array.isArray(data.value_priorities)) {
            const container = document.getElementById('form-field-value_priorities-container');
            if (container) {
                const buttons = container.querySelectorAll('.multi-select-option');
                buttons.forEach(btn => {
                    if (data.value_priorities.includes(btn.dataset.value)) {
                        btn.classList.add('selected');
                    }
                });
            }
            document.getElementById('form-field-value_priorities').value = JSON.stringify(data.value_priorities);
        }
        
        // 填充滑块组
        if (data.ability_assessment) {
            Object.entries(data.ability_assessment).forEach(([k, v]) => {
                const el = document.getElementById(`form-field-ability_assessment-${k}`);
                const display = document.getElementById(`form-field-ability_assessment-${k}-value`);
                if (el) el.value = v;
                if (display) display.textContent = v;
            });
            ProfileFormState.currentData.ability_assessment = data.ability_assessment;
        }
        
        if (data.universal_skills) {
            Object.entries(data.universal_skills).forEach(([k, v]) => {
                const el = document.getElementById(`form-field-universal_skills-${k}`);
                const display = document.getElementById(`form-field-universal_skills-${k}-value`);
                if (el) el.value = v;
                if (display) display.textContent = v;
            });
            ProfileFormState.currentData.universal_skills = data.universal_skills;
        }
        
        // 填充单个滑块
        if (data.resilience_score) {
            const el = document.getElementById('form-field-resilience_score');
            const display = document.getElementById('form-field-resilience_score-display');
            if (el) el.value = data.resilience_score;
            if (display) display.textContent = data.resilience_score;
            ProfileFormState.currentData.resilience_score = data.resilience_score;
        }
    },
    
    // 处理字段变更
    handleFieldChange(field, value) {
        ProfileFormState.updateField(field, value || null);
    },
    
    // 处理多选
    handleMultiSelect(field, value, btn) {
        btn.classList.toggle('selected');
        
        const container = document.getElementById(`form-field-${field}-container`);
        const selected = container.querySelectorAll('.multi-select-option.selected');
        const values = Array.from(selected).map(b => b.dataset.value);
        
        document.getElementById(`form-field-${field}`).value = JSON.stringify(values);
        ProfileFormState.updateField(field, values);
    },
    
    // 处理滑块组变更
    handleSliderGroupChange(field, subKey, value) {
        const display = document.getElementById(`form-field-${field}-${subKey}-value`);
        if (display) display.textContent = value;
        
        // 创建新对象避免引用问题
        const current = { ...(ProfileFormState.currentData[field] || {}) };
        current[subKey] = parseInt(value);
        ProfileFormState.updateField(field, current);
        
        console.log(`[ProfileForm] ${field}.${subKey} changed to ${value}:`, ProfileFormState.currentData[field]);
    },
    
    // 处理滑块变更
    handleSliderChange(field, value) {
        const display = document.getElementById(`form-field-${field}-display`);
        if (display) display.textContent = value;
        ProfileFormState.updateField(field, parseInt(value));
    },
    
    // 重置表单
    reset() {
        ProfileFormState.reset();
        this.populateFormValues(ProfileFormState.originalData);
    },
    
    // 提交表单
    async submit() {
        const changes = ProfileFormState.getChanges();
        
        if (Object.keys(changes).length === 0) {
            this.close();
            return;
        }
        
        const submitBtn = document.getElementById('profile-form-submit');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>保存中...';
        }
        
        try {
            const result = await this.submitToAPI(ProfileFormState.userId, changes);
            
            if (result.success) {
                // 显示成功提示
                this.showNotification('保存成功！画像已更新', 'success');
                
                // 调用回调
                if (ProfileFormState.onSubmitCallback) {
                    ProfileFormState.onSubmitCallback(result.data);
                }
                
                // 关闭表单
                this.close();
                
                return result;
            } else {
                throw new Error(result.message || '保存失败');
            }
        } catch (error) {
            console.error('[ProfileForm] Submit error:', error);
            this.showNotification('保存失败：' + error.message, 'error');
        } finally {
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-save mr-2"></i>保存';
            }
        }
    },
    
    // 提交到API
    async submitToAPI(userId, data) {
        const url = `${PROFILE_FORM_CONFIG.API_BASE_URL}/user-profiles/${userId}/form-update`;
        
        console.log('[ProfileForm] Submitting to API:', url);
        console.log('[ProfileForm] Data:', data);
        
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ updates: data })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.message || `HTTP ${response.status}`);
        }
        
        return await response.json();
    },
    
    // AI隐式调用接口（程序化调用，不打开表单）
    async updateByAI(userId, updates, reason = 'AI自动提取') {
        console.log('[ProfileForm] AI updating profile:', updates);
        
        try {
            // 使用专门的AI更新端点
            const url = `${PROFILE_FORM_CONFIG.API_BASE_URL}/user-profiles/${userId}/ai-update`;
            
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    updates: updates,
                    reason: reason,
                    source: 'ai_extraction'
                })
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || `HTTP ${response.status}`);
            }
            
            const result = await response.json();
            
            // 显示AI更新提示
            if (result.data && result.data.updated_fields) {
                this.showNotification(
                    `AI已自动记录：${result.data.updated_fields.join('、')}`, 
                    'info'
                );
            }
            
            return result;
        } catch (error) {
            console.error('[ProfileForm] AI update error:', error);
            // AI更新失败不显示错误提示，静默处理
            return { success: false, error: error.message };
        }
    },
    
    // 显示通知
    showNotification(message, type = 'info') {
        const colors = {
            success: 'from-green-500 to-green-600',
            error: 'from-red-500 to-red-600',
            info: 'from-blue-500 to-blue-600'
        };
        
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 bg-gradient-to-r ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-[60] animate-fade-in`;
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'} mr-2"></i>
                <span>${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transform = 'translateX(100%)';
            notification.style.transition = 'all 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
};

// 导出模块
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { ProfileForm, ProfileFormState, ProfileFormConfig: PROFILE_FORM_CONFIG };
}
