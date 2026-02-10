/**
 * 用户画像模块 - 前端逻辑
 * 基于Career-Planning SKILL三层模型
 */

// 配置
const CONFIG = {
    API_BASE_URL: 'http://localhost:8000/api',
    USER_ID: localStorage.getItem('user_id'),
    MAX_CHAT_HISTORY: 50
};

// 全局状态
const state = {
    profile: null,
    chatHistory: [],
    currentCasveStage: 'communication',
    isLoading: false
};

// 检查登录状态
function checkAuth() {
    const token = localStorage.getItem('auth_token');
    const userId = localStorage.getItem('user_id');
    
    if (!token || !userId) {
        // 未登录，显示提示并跳转
        showLoginPrompt();
        return false;
    }
    
    // 已登录，更新配置
    CONFIG.USER_ID = userId;
    return true;
}

// 显示登录提示
function showLoginPrompt() {
    const chatHistory = document.getElementById('chat-history');
    if (chatHistory) {
        chatHistory.innerHTML = `
            <div class="flex flex-col items-center justify-center h-full text-center p-8">
                <div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                    <i class="fas fa-user-lock text-2xl text-blue-500"></i>
                </div>
                <h3 class="text-lg font-semibold text-gray-800 mb-2">请先登录</h3>
                <p class="text-gray-600 mb-4">登录后即可使用职业规划助手</p>
                <button onclick="goToLogin()" 
                        class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                    去登录
                </button>
            </div>
        `;
    }
    
    // 禁用输入框
    const input = document.getElementById('chat-input');
    if (input) {
        input.disabled = true;
        input.placeholder = '请先登录...';
    }
}

// 跳转到登录页面
function goToLogin() {
    window.location.href = 'index.html';
}

// 初始化
function init() {
    // 检查登录状态
    if (!checkAuth()) {
        return;
    }
    
    // 初始化用户画像
    initProfile();
    
    // 加载历史对话
    loadChatHistory();
    
    // 更新UI
    updateUIFromState();
    
    console.log('[UserProfile] Initialized with user_id:', CONFIG.USER_ID);
}

// 初始化用户画像
async function initProfile() {
    try {
        // 尝试获取现有画像
        let response = await fetch(`${CONFIG.API_BASE_URL}/user-profiles/${CONFIG.USER_ID}`);
        
        if (response.status === 404) {
            // 创建新画像
            response = await fetch(`${CONFIG.API_BASE_URL}/user-profiles`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: CONFIG.USER_ID,
                    nickname: `用户${CONFIG.USER_ID.substr(-6)}`
                })
            });
        }
        
        if (response.ok) {
            state.profile = await response.json();
            updateUIFromProfile();
        }
    } catch (error) {
        console.error('[UserProfile] Init error:', error);
        showToast('连接服务器失败，部分功能可能不可用', 'error');
    }
}

// ==================== 聊天功能 ====================

// TypeChat配置（从环境变量或配置中获取）
const TYPECHAT_CONFIG = {
    apiKey: localStorage.getItem('openai_api_key') || '', // 用户可配置
    enabled: true // 默认启用轻量级预处理（不依赖外部API）
};

/**
 * 轻量级前端意图识别与实体提取器
 * 模拟TypeChat功能，在浏览器端进行预处理
 */
class LightweightTypeChatProcessor {
    constructor() {
        this.intentPatterns = {
            interest_explore: {
                keywords: ['喜欢', '爱好', '兴趣', '热爱', '享受', '感兴趣', '想', '热情', '爱', '痴迷'],
                patterns: [/喜欢(.+)/, /对(.+)感兴趣/, /爱好是(.+)/, /想(学|做|成为)/],
                weight: 1.0
            },
            ability_assess: {
                keywords: ['擅长', '能力', '技能', '优势', '会', '能做', '强', '厉害', '熟练', '精通'],
                patterns: [/擅长(.+)/, /会(.+)/, /(.+)比较好/, /(.+)能力强/],
                weight: 1.0
            },
            value_clarify: {
                keywords: ['价值', '意义', '重要', '在乎', '追求', '想要', '重视', '看重', '认为'],
                patterns: [/重要的是(.+)/, /追求(.+)/, /想要(.+)生活/, /在乎(.+)/],
                weight: 1.0
            },
            career_advice: {
                keywords: ['职业', '工作', '行业', '前景', '发展', '建议', '怎么样', '推荐', '适合'],
                patterns: [/(.+)职业怎么样/, /(.+)行业前景/, /建议(.+)/, /适合(.+)/],
                weight: 1.0
            },
            path_planning: {
                keywords: ['路径', '规划', '方向', '怎么选', '怎么走', '未来', '计划', '目标', ' roadmap'],
                patterns: [/规划(.+)/, /(.+)方向/, /(.+)计划/, /(.+)目标/],
                weight: 1.0
            },
            casve_guidance: {
                keywords: ['决策', '选择', '犹豫', '纠结', '怎么办', '选哪个', '不确定', '难决定', '困惑'],
                patterns: [/纠结(.+)/, /犹豫(.+)/, /不知道(.+)/, /(.+)和(.+)选/],
                weight: 1.0
            },
            emotional_support: {
                keywords: ['焦虑', '担心', '害怕', '迷茫', '无助', '压力', '困扰', '烦恼', '累', '痛苦'],
                patterns: [/很(焦虑|担心|害怕)/, /(.+)压力/, /(.+)迷茫/],
                weight: 1.0
            }
        };
        
        this.emotionalPatterns = {
            anxious: ['焦虑', '担心', '害怕', '紧张', '压力', '恐惧'],
            confident: ['自信', '确定', '清楚', '明白', '没问题'],
            curious: ['好奇', '想', '问问', '了解', '想知道'],
            frustrated: ['烦', '累', '失望', '沮丧', '郁闷', '痛苦'],
            neutral: []
        };
        
        this.entityPatterns = {
            interest: {
                domain: [/喜欢(.+?)[，。]/, /对(.+?)感兴趣/, /爱好(.+?)[，。]/],
                sentiment: { positive: ['喜欢', '爱', '热爱', '享受'], negative: ['讨厌', '不喜欢', '烦'] }
            },
            ability: {
                skill: [/擅长(.+?)[，。]/, /会(.+?)[，。]/, /(.+?)能力强/],
                level: {
                    beginner: ['初学', '刚学', '入门', '新手'],
                    intermediate: ['还行', '一般', '还可以'],
                    advanced: ['精通', '熟练', '擅长', '专家']
                }
            },
            constraint: {
                time: ['没时间', '忙', '时间不够', '紧张'],
                resource: ['没钱', '资源', '条件', '经济'],
                skill: ['不会', '不懂', '基础差', '没学过']
            }
        };
    }

    /**
     * 预处理用户输入
     */
    async preprocess(rawText, conversationHistory = []) {
        const cleanedText = rawText.trim();
        
        // 意图识别
        const intent = this._detectIntent(cleanedText);
        
        // 实体提取
        const entities = this._extractEntities(cleanedText);
        
        // 情感分析
        const emotionalState = this._detectEmotion(cleanedText);
        
        // 上下文分析
        const contextSummary = this._generateContextSummary(cleanedText, conversationHistory);
        
        // 建议处理方式
        const suggestedApproach = this._suggestApproach(intent, entities, emotionalState);
        
        return {
            rawText,
            cleanedText,
            intent: {
                type: intent.type,
                confidence: intent.confidence,
                subType: intent.subType,
                contextSignals: intent.signals,
                emotionalState
            },
            entities,
            contextSummary,
            suggestedApproach
        };
    }

    /**
     * 检测意图
     */
    _detectIntent(text) {
        const lowerText = text.toLowerCase();
        let bestIntent = 'general_chat';
        let maxScore = 0;
        let signals = [];
        let subType = null;

        for (const [intentType, config] of Object.entries(this.intentPatterns)) {
            let score = 0;
            let matchedKeywords = [];
            
            // 关键词匹配
            for (const keyword of config.keywords) {
                if (lowerText.includes(keyword)) {
                    score += config.weight;
                    matchedKeywords.push(keyword);
                }
            }
            
            // 模式匹配
            for (const pattern of config.patterns) {
                const match = text.match(pattern);
                if (match) {
                    score += config.weight * 1.5;
                    if (match[1]) {
                        signals.push(`${intentType}:${match[1].trim()}`);
                    }
                }
            }
            
            if (score > maxScore) {
                maxScore = score;
                bestIntent = intentType;
                if (matchedKeywords.length > 0) {
                    signals = [...new Set([...signals, ...matchedKeywords])];
                }
            }
        }

        // 计算置信度
        const confidence = Math.min(maxScore / 3, 0.95);
        
        // 检测子意图
        if (bestIntent === 'interest_explore') {
            if (/音乐|绘画|艺术|设计/.test(text)) subType = 'artistic';
            else if (/编程|计算机|技术|工程/.test(text)) subType = 'technical';
            else if (/写作|阅读|文学/.test(text)) subType = 'literary';
        }

        return {
            type: bestIntent,
            confidence,
            subType,
            signals: signals.slice(0, 5) // 最多5个信号
        };
    }

    /**
     * 提取实体
     */
    _extractEntities(text) {
        const entities = {
            interests: [],
            abilities: [],
            values: [],
            constraints: []
        };

        // 提取兴趣
        const interestPatterns = [
            /喜欢(.+?)[，。；,.]/g,
            /对(.+?)感兴趣/g,
            /爱好(.+?)[，。；,.]/g,
            /热爱(.+?)[，。；,.]/g
        ];
        
        for (const pattern of interestPatterns) {
            let match;
            while ((match = pattern.exec(text)) !== null) {
                const specific = match[1].trim();
                if (specific.length > 0 && specific.length < 20) {
                    entities.interests.push({
                        domain: this._categorizeDomain(specific),
                        specific,
                        sentiment: 'positive',
                        constraints: []
                    });
                }
            }
        }

        // 提取能力
        const abilityPatterns = [
            /擅长(.+?)[，。；,.]/g,
            /会(.+?)[，。；,.]/g,
            /(.+?)能力强/g
        ];
        
        for (const pattern of abilityPatterns) {
            let match;
            while ((match = pattern.exec(text)) !== null) {
                const skill = match[1].trim();
                if (skill.length > 0 && skill.length < 15) {
                    entities.abilities.push({
                        skill,
                        level: this._detectAbilityLevel(text, skill),
                        evidence: match[0]
                    });
                }
            }
        }

        // 提取价值观
        const valueIndicators = ['重要', '在乎', '追求', '价值', '意义'];
        for (const indicator of valueIndicators) {
            const pattern = new RegExp(`${indicator}(.+?)[，。；,.]`, 'g');
            let match;
            while ((match = pattern.exec(text)) !== null) {
                const value = match[1].trim();
                if (value.length > 0 && value.length < 10) {
                    entities.values.push(value);
                }
            }
        }

        // 提取约束
        const constraintPatterns = [
            { type: 'time', keywords: ['没时间', '忙', '时间不够'] },
            { type: 'resource', keywords: ['没钱', '经济', '条件'] },
            { type: 'skill', keywords: ['不会', '不懂', '基础差'] }
        ];
        
        for (const { type, keywords } of constraintPatterns) {
            for (const keyword of keywords) {
                if (text.includes(keyword)) {
                    entities.constraints.push({
                        type,
                        description: keyword
                    });
                }
            }
        }

        // 去重
        entities.interests = entities.interests.filter((v, i, a) => 
            a.findIndex(t => t.specific === v.specific) === i
        );
        entities.values = [...new Set(entities.values)];

        return entities;
    }

    /**
     * 分类领域
     */
    _categorizeDomain(text) {
        const domains = {
            art: ['音乐', '绘画', '设计', '艺术', '舞蹈', '摄影'],
            tech: ['编程', '计算机', '技术', '工程', '科学', '数学'],
            social: ['交流', '沟通', '社交', '团队', '合作'],
            business: ['商业', '管理', '经济', '金融', '市场'],
            literature: ['写作', '阅读', '文学', '历史', '语言']
        };
        
        for (const [domain, keywords] of Object.entries(domains)) {
            if (keywords.some(k => text.includes(k))) {
                return domain;
            }
        }
        return 'general';
    }

    /**
     * 检测能力水平
     */
    _detectAbilityLevel(text, skill) {
        const advanced = ['精通', '熟练', '擅长', '专家', '很强'];
        const beginner = ['初学', '刚学', '入门', '新手', '不太会'];
        
        if (advanced.some(k => text.includes(k))) return 'advanced';
        if (beginner.some(k => text.includes(k))) return 'beginner';
        return 'intermediate';
    }

    /**
     * 检测情感状态
     */
    _detectEmotion(text) {
        for (const [emotion, keywords] of Object.entries(this.emotionalPatterns)) {
            if (keywords.some(k => text.includes(k))) {
                return emotion;
            }
        }
        return 'neutral';
    }

    /**
     * 生成上下文摘要
     * 分析近3条用户消息，提取核心需求和意图演变
     */
    _generateContextSummary(text, history) {
        if (history.length === 0) {
            return '新对话，用户首次表达意图';
        }
        
        // 获取最近3条用户消息（从完整的对话历史中筛选）
        const recentUserMessages = history
            .filter(h => h.role === 'user')
            .slice(-3);
        
        if (recentUserMessages.length === 0) {
            return '新对话，用户首次表达意图';
        }
        
        // 分析每条用户消息的意图和核心关键词
        const userNeeds = recentUserMessages.map((msg, index) => {
            const msgText = msg.content || msg.message || '';
            
            // 检测该条消息的意图
            const intent = this._detectIntent(msgText);
            
            // 提取核心实体（兴趣、能力、价值观、约束等）
            const entities = this._extractEntities(msgText);
            
            // 提取关键词（基于意图类型的关键信息）
            const keywords = this._extractKeywordsByIntent(msgText, intent.type, entities);
            
            return {
                round: index + 1, // 对话轮次
                intent: intent.type,
                intentLabel: this._getIntentLabel(intent.type),
                keywords: keywords,
                hasEmotion: this._detectEmotion(msgText) !== 'neutral'
            };
        });
        
        // 统计意图分布
        const intentCounts = {};
        userNeeds.forEach(need => {
            intentCounts[need.intent] = (intentCounts[need.intent] || 0) + 1;
        });
        
        // 确定主导意图（出现次数最多的）
        const dominantIntent = Object.entries(intentCounts)
            .sort((a, b) => b[1] - a[1])[0]?.[0] || 'general_chat';
        
        // 收集所有关键词并去重
        const allKeywords = [...new Set(userNeeds.flatMap(n => n.keywords))];
        
        // 生成结构化的摘要
        const needDescriptions = userNeeds.map(need => {
            const keywordStr = need.keywords.length > 0 ? `(${need.keywords.slice(0, 2).join('、')})` : '';
            return `${need.intentLabel}${keywordStr}`;
        });
        
        // 构建最终摘要
        if (userNeeds.length === 1) {
            return `用户关注点：${needDescriptions[0]}`;
        } else {
            // 检测需求演变（是否有新意图出现）
            const latestNeed = userNeeds[userNeeds.length - 1];
            const previousIntents = userNeeds.slice(0, -1).map(n => n.intent);
            const isNewIntent = !previousIntents.includes(latestNeed.intent);
            
            let summary = `对话脉络：`;
            if (isNewIntent && userNeeds.length > 1) {
                summary += `从${needDescriptions[0]}转向${needDescriptions[needDescriptions.length - 1]}`;
            } else {
                summary += needDescriptions.join(' → ');
            }
            
            // 添加核心关注领域
            if (allKeywords.length > 0) {
                const topKeywords = allKeywords.slice(0, 3);
                summary += ` | 核心关注：${topKeywords.join('、')}`;
            }
            
            return summary;
        }
    }
    
    /**
     * 根据意图类型提取关键词
     */
    _extractKeywordsByIntent(text, intentType, entities) {
        const keywords = [];
        
        // 根据意图类型提取不同的关键词
        switch (intentType) {
            case 'interest_explore':
                // 提取兴趣领域相关词
                if (entities.interests && entities.interests.length > 0) {
                    keywords.push(...entities.interests.map(i => i.specific));
                }
                // 额外提取常见领域词
                const interestDomains = ['体育', '音乐', '艺术', '编程', '文学', '科学', '商业', '医学', '法律'];
                interestDomains.forEach(domain => {
                    if (text.includes(domain) && !keywords.includes(domain)) {
                        keywords.push(domain);
                    }
                });
                break;
                
            case 'ability_assess':
                // 提取能力相关词
                if (entities.abilities && entities.abilities.length > 0) {
                    keywords.push(...entities.abilities.map(a => a.skill));
                }
                const abilityKeywords = ['擅长', '优势', '能力', '技能', '水平', '专业'];
                abilityKeywords.forEach(kw => {
                    if (text.includes(kw)) {
                        const match = text.match(new RegExp(`([^，。；,]{0,5}${kw}[^，。；,]{0,5})`));
                        if (match && match[1] && !keywords.includes(match[1])) {
                            keywords.push(match[1].trim());
                        }
                    }
                });
                break;
                
            case 'career_advice':
            case 'path_planning':
                // 提取职业相关词
                const careerKeywords = ['职业', '工作', '行业', '发展', '就业', '前景', '薪资'];
                careerKeywords.forEach(kw => {
                    if (text.includes(kw)) {
                        const match = text.match(new RegExp(`([^，。；,]{0,5}${kw}[^，。；,]{0,5})`));
                        if (match && match[1] && !keywords.includes(match[1])) {
                            keywords.push(match[1].trim());
                        }
                    }
                });
                break;
                
            case 'emotional_support':
                // 提取情绪相关词
                const emotionKeywords = ['焦虑', '担心', '迷茫', '压力', '困惑', '害怕', '不确定'];
                emotionKeywords.forEach(kw => {
                    if (text.includes(kw) && !keywords.includes(kw)) {
                        keywords.push(kw);
                    }
                });
                break;
                
            case 'value_clarify':
                // 提取价值观相关词
                if (entities.values && entities.values.length > 0) {
                    keywords.push(...entities.values);
                }
                break;
                
            case 'casve_guidance':
                // 提取决策相关词
                const decisionKeywords = ['选择', '决定', '纠结', '犹豫', '选项'];
                decisionKeywords.forEach(kw => {
                    if (text.includes(kw) && !keywords.includes(kw)) {
                        keywords.push(kw);
                    }
                });
                break;
        }
        
        // 通用：提取特定领域名词
        const commonDomains = {
            '体育': '体育', '运动': '体育',
            '音乐': '音乐', '画画': '艺术', '设计': '艺术',
            '编程': '技术', '计算机': '技术', '代码': '技术',
            '数学': '理科', '物理': '理科', '化学': '理科',
            '金融': '商科', '经济': '商科', '管理': '商科',
            '医学': '医学', '医生': '医学', '护理': '医学'
        };
        
        Object.entries(commonDomains).forEach(([key, category]) => {
            if (text.includes(key) && !keywords.includes(category)) {
                keywords.push(category);
            }
        });
        
        // 去重并限制数量
        return [...new Set(keywords)].slice(0, 3);
    }
    
    /**
     * 获取意图类型的中文标签
     */
    _getIntentLabel(intentType) {
        const labels = {
            interest_explore: '兴趣探索',
            ability_assess: '能力评估',
            value_clarify: '价值观澄清',
            career_advice: '职业建议',
            path_planning: '路径规划',
            casve_guidance: '决策指导',
            emotional_support: '情感支持',
            general_chat: '一般咨询'
        };
        return labels[intentType] || '未知意图';
    }

    /**
     * 建议处理方式
     */
    _suggestApproach(intent, entities, emotion) {
        const approaches = {
            interest_explore: '通过追问深入了解兴趣细节和背景',
            ability_assess: '引导用户具体说明能力水平和经历',
            value_clarify: '探索价值观背后的深层动机',
            career_advice: '提供相关职业信息和匹配建议',
            path_planning: '帮助用户制定阶段性目标',
            casve_guidance: '运用CASVE模型辅助决策',
            emotional_support: '先给予情感支持，再引导理性分析',
            general_chat: '保持开放，引导用户明确需求'
        };
        
        return approaches[intent.type] || approaches.general_chat;
    }

    /**
     * 快速意图检测（轻量级）
     */
    quickIntentDetect(text) {
        const result = this._detectIntent(text);
        return result.type;
    }
}

// 创建全局处理器实例
const typeChatProcessor = new LightweightTypeChatProcessor();

/**
 * 轻量级意图检测（快速，无需API调用）
 * 使用 LightweightTypeChatProcessor
 */
function quickIntentDetection(message) {
    return typeChatProcessor.quickIntentDetect(message);
}

/**
 * TypeChat预处理（异步）
 * 使用轻量级浏览器端处理器
 */
async function preprocessWithTypeChat(message, history) {
    if (!TYPECHAT_CONFIG.enabled) {
        return null;
    }
    
    try {
        // 使用内联的轻量级处理器
        const result = await typeChatProcessor.preprocess(message, history);
        console.log('[TypeChat] Preprocessed:', result);
        return result;
    } catch (error) {
        console.error('[TypeChat] Preprocess failed:', error);
        return null;
    }
}

// 发送消息
async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message || state.isLoading) return;
    
    // 清空输入
    input.value = '';
    
    // 添加用户消息到UI
    addMessageToUI('user', message);
    
    // 显示加载状态
    state.isLoading = true;
    showLoadingIndicator();
    
    try {
        // 1. 快速意图检测（本地）
        const quickIntent = quickIntentDetection(message);
        console.log('[Chat] Quick intent:', quickIntent);
        
        // 2. 异步进行TypeChat预处理（如果启用）
        let preprocessed = null;
        if (TYPECHAT_CONFIG.enabled) {
            preprocessed = await preprocessWithTypeChat(message, state.chatHistory.slice(-5));
        }
        
        // 3. 构建请求体
        const requestBody = {
            message: message,
            context: {
                history: state.chatHistory.slice(-5),
                quick_intent: quickIntent  // 传递快速检测结果
            }
        };
        
        // 如果有TypeChat预处理结果，添加到请求
        if (preprocessed) {
            requestBody.preprocessed = preprocessed;
        }
        
        // 4. 调用API
        const response = await fetch(`${CONFIG.API_BASE_URL}/user-profiles/${CONFIG.USER_ID}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });
        
        if (response.ok) {
            const result = await response.json();
            
            // 添加AI回复（自然对话，不包含结构化信息）
            addMessageToUI('assistant', result.reply, result.suggested_questions);
            
            // 更新侧边栏画像显示（如果有profile_updates）
            if (result.profile_updates) {
                updateUIFromProfileData(result.profile_updates);
            }
            
            // 显示本次提取到的信息（如果有）
            if (result.extracted_info && result.extracted_info.length > 0) {
                showExtractedInfoNotification(result.extracted_info);
            }
            
            // 更新CASVE阶段
            if (result.current_casve_stage) {
                updateCasveStage(result.current_casve_stage);
            }
            
            // 保存到历史
            state.chatHistory.push({ role: 'user', content: message });
            state.chatHistory.push({ role: 'assistant', content: result.reply });
        } else {
            addMessageToUI('assistant', '抱歉，我遇到了一些问题，请稍后再试。');
        }
    } catch (error) {
        console.error('[Chat] Error:', error);
        addMessageToUI('assistant', '网络连接失败，请检查网络设置。');
    } finally {
        state.isLoading = false;
        hideLoadingIndicator();
    }
}

// 发送意图消息（底部快捷按钮使用）
function sendIntent(intentMessage) {
    document.getElementById('chat-input').value = intentMessage;
    sendMessage();
}

// 将问题填入输入框（辅助问题使用，允许用户修改和回答）
function fillInputWithQuestion(question) {
    const input = document.getElementById('chat-input');
    // 将问题填入输入框，后面留出空格让用户继续输入回答
    input.value = question + ' ';
    // 聚焦到输入框，并将光标移到最后
    input.focus();
    // 将光标移到末尾
    const length = input.value.length;
    input.setSelectionRange(length, length);
}

// 处理键盘事件
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// 添加消息到UI
function addMessageToUI(role, content, suggestedQuestions = []) {
    const chatHistory = document.getElementById('chat-history');
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role === 'user' ? 'user-message' : 'ai-message'} p-4`;
    
    if (role === 'user') {
        messageDiv.innerHTML = `<p class="text-white">${escapeHtml(content)}</p>`;
    } else {
        let html = `
            <div class="flex items-start">
                <div class="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-white mr-3 flex-shrink-0">
                    <i class="fas fa-robot text-sm"></i>
                </div>
                <div class="flex-1">
                    <p class="text-gray-800">${escapeHtml(content)}</p>
        `;
        
        // 添加建议问题
        if (suggestedQuestions && suggestedQuestions.length > 0) {
            html += `
                <div class="mt-3 flex flex-wrap gap-2">
                    ${suggestedQuestions.map((q, index) => `
                        <button onclick="fillInputWithQuestion('${escapeHtml(q)}')" 
                                class="text-xs bg-blue-50 text-blue-600 px-3 py-1 rounded-full hover:bg-blue-100 transition-colors flex items-center gap-1"
                                title="点击将问题填入输入框，你可以修改后回答">
                            <i class="fas fa-question-circle text-xs opacity-60"></i>
                            ${escapeHtml(q)}
                        </button>
                    `).join('')}
                </div>
                <div class="mt-1 text-xs text-gray-400 italic">
                    <i class="fas fa-info-circle mr-1"></i>点击问题可将其填入输入框，你可以修改或直接回答
                </div>
            `;
        }
        
        html += '</div></div>';
        messageDiv.innerHTML = html;
    }
    
    chatHistory.appendChild(messageDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// 显示加载指示器
function showLoadingIndicator() {
    const chatHistory = document.getElementById('chat-history');
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'loading-indicator';
    loadingDiv.className = 'chat-message ai-message p-4';
    loadingDiv.innerHTML = `
        <div class="flex items-center text-gray-500">
            <i class="fas fa-spinner fa-spin mr-2"></i>
            <span>思考中...</span>
        </div>
    `;
    chatHistory.appendChild(loadingDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// 隐藏加载指示器
function hideLoadingIndicator() {
    const indicator = document.getElementById('loading-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// 清除对话
async function clearChat() {
    if (!confirm('确定要清除当前对话吗？')) return;
    
    try {
        await fetch(`${CONFIG.API_BASE_URL}/user-profiles/${CONFIG.USER_ID}/chat/session`, {
            method: 'DELETE'
        });
        
        // 清空UI
        const chatHistory = document.getElementById('chat-history');
        chatHistory.innerHTML = '';
        state.chatHistory = [];
        
        // 重新添加欢迎消息
        addWelcomeMessage();
    } catch (error) {
        console.error('[Chat] Clear error:', error);
    }
}

// 添加欢迎消息
function addWelcomeMessage() {
    addMessageToUI('assistant', `你好！我是你的职业规划助手。我可以帮助你：

• 探索兴趣和性格特点
• 评估能力和优势
• 澄清职业价值观
• 规划职业发展路径

我们可以从任何你感兴趣的话题开始聊！`);
}

// ==================== 画像更新 ====================

// 从提取的信息更新画像
async function updateProfileFromExtractedInfo(extractedInfo) {
    const updates = {};
    
    for (const info of extractedInfo) {
        updates[info.field] = info.value;
    }
    
    if (Object.keys(updates).length === 0) return;
    
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/user-profiles/${CONFIG.USER_ID}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updates)
        });
        
        if (response.ok) {
            state.profile = await response.json();
            updateUIFromProfile();
            showToast('画像已自动更新', 'success');
        }
    } catch (error) {
        console.error('[Profile] Update error:', error);
    }
}

// 更新UI显示
function updateUIFromProfile() {
    if (!state.profile) return;
    
    const p = state.profile;
    
    // 用户问候
    document.getElementById('user-greeting').textContent = `你好，${p.nickname || '用户'}`;
    
    // 接口层
    if (p.holland_code) {
        document.getElementById('holland-code').textContent = p.holland_code;
    }
    if (p.mbti_type) {
        document.getElementById('mbti-type').textContent = p.mbti_type;
    }
    if (p.value_priorities && p.value_priorities.length > 0) {
        document.getElementById('value-tags').innerHTML = p.value_priorities.map(v => 
            `<span class="attribute-tag tag-interface">${v}</span>`
        ).join('');
    }
    if (p.ability_assessment) {
        renderAbilityBars(p.ability_assessment);
    }
    
    // 可变层
    if (p.career_path_preference) {
        const pathNames = {
            technical: '技术专家路径',
            management: '管理领导路径',
            professional: '专业方向路径',
            public_welfare: '公益方向路径'
        };
        document.getElementById('career-path').textContent = pathNames[p.career_path_preference] || p.career_path_preference;
    }
    if (p.preferred_majors && p.preferred_majors.length > 0) {
        document.getElementById('major-tags').innerHTML = p.preferred_majors.map(m => 
            `<span class="attribute-tag tag-variable">专业${m}</span>`
        ).join('');
    }
    if (p.practice_experiences && p.practice_experiences.length > 0) {
        document.getElementById('practice-list').innerHTML = p.practice_experiences.map(pe => 
            `<div class="text-sm text-gray-600 mb-1">• ${pe.type}: ${pe.desc || ''}</div>`
        ).join('');
    }
    
    // 核心层
    if (p.universal_skills) {
        renderSkillBars(p.universal_skills);
    }
    if (p.resilience_score) {
        document.getElementById('resilience-bar').style.width = `${p.resilience_score * 10}%`;
        document.getElementById('resilience-score').textContent = `${p.resilience_score}/10`;
    }
    
    // CASVE阶段
    if (p.current_casve_stage) {
        updateCasveStage(p.current_casve_stage);
    }
    
    // 完整度
    updateCompleteness(p.completeness_score || 0);
}

// 渲染能力条
function renderAbilityBars(abilities) {
    const container = document.getElementById('ability-bars');
    const abilityNames = {
        logic: '逻辑推理',
        creativity: '创造力',
        communication: '沟通能力',
        teamwork: '团队协作',
        leadership: '领导力',
        analysis: '分析能力'
    };
    
    container.innerHTML = Object.entries(abilities).map(([key, value]) => `
        <div class="flex items-center mb-2">
            <span class="text-xs text-gray-600 w-20">${abilityNames[key] || key}</span>
            <div class="flex-1 bg-gray-200 rounded-full h-2 mx-2">
                <div class="bg-blue-500 h-2 rounded-full" style="width: ${value * 10}%"></div>
            </div>
            <span class="text-xs text-gray-500 w-8">${value}</span>
        </div>
    `).join('');
}

// 渲染技能条
function renderSkillBars(skills) {
    const container = document.getElementById('skill-bars');
    const skillNames = {
        communication: '沟通表达',
        teamwork: '团队协作',
        critical_thinking: '批判思维',
        creativity: '创造力'
    };
    
    container.innerHTML = Object.entries(skills).map(([key, value]) => `
        <div class="flex items-center mb-2">
            <span class="text-xs text-gray-600 w-20">${skillNames[key] || key}</span>
            <div class="flex-1 bg-gray-200 rounded-full h-2 mx-2">
                <div class="bg-purple-500 h-2 rounded-full" style="width: ${value * 10}%"></div>
            </div>
            <span class="text-xs text-gray-500 w-8">${value}</span>
        </div>
    `).join('');
}

// 更新CASVE阶段显示
function updateCasveStage(stage) {
    state.currentCasveStage = stage;
    
    // 更新阶段样式
    const stages = ['C', 'A', 'S', 'V', 'E'];
    const stageNames = {
        communication: 'C-沟通',
        analysis: 'A-分析',
        synthesis: 'S-综合',
        evaluation: 'V-评估',
        execution: 'E-执行'
    };
    const stageDescriptions = {
        communication: '识别决策需求，感知理想与现实差距',
        analysis: '系统梳理自我认知与选项信息',
        synthesis: '生成可能的解决方案',
        evaluation: '权衡各选项的优劣后果',
        execution: '将选择转化为行动计划'
    };
    
    stages.forEach((s, index) => {
        const el = document.getElementById(`stage-${s}`);
        const stageKey = Object.keys(stageNames).find(k => stageNames[k].startsWith(s));
        
        if (stageKey === stage) {
            el.className = 'casve-stage casve-active';
        } else {
            el.className = 'casve-stage casve-inactive';
        }
    });
    
    // 更新描述
    document.getElementById('casve-description').textContent = 
        `当前阶段：${stageDescriptions[stage] || '识别决策需求'}`;
}

// 更新完整度显示
async function updateCompleteness(score) {
    // 获取详细完整度
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/user-profiles/${CONFIG.USER_ID}/completeness`);
        if (response.ok) {
            const detail = await response.json();
            
            document.getElementById('completeness-score').textContent = `${detail.score}%`;
            document.getElementById('completeness-bar').style.width = `${detail.score}%`;
            document.getElementById('interface-score').textContent = detail.interface_layer_score;
            document.getElementById('variable-score').textContent = detail.variable_layer_score;
            document.getElementById('core-score').textContent = detail.core_layer_score;
        }
    } catch (error) {
        console.error('[Completeness] Error:', error);
        document.getElementById('completeness-score').textContent = `${score}%`;
        document.getElementById('completeness-bar').style.width = `${score}%`;
    }
}

// 根据API返回的profile_updates更新侧边栏UI
function updateUIFromProfileData(profileData) {
    if (!profileData) return;
    
    console.log('[updateUIFromProfileData] Updating UI with:', profileData);
    
    // 更新接口层
    if (profileData.holland_code !== undefined) {
        const el = document.getElementById('holland-code');
        if (el) {
            if (profileData.holland_code) {
                el.innerHTML = `<span class="text-blue-600 font-semibold">${profileData.holland_code}</span>`;
            } else {
                el.textContent = '未设置';
            }
        }
    }
    if (profileData.mbti_type !== undefined) {
        const el = document.getElementById('mbti-type');
        if (el) {
            if (profileData.mbti_type) {
                el.innerHTML = `<span class="text-blue-600 font-semibold">${profileData.mbti_type}</span>`;
            } else {
                el.textContent = '未设置';
            }
        }
    }
    if (profileData.value_priorities !== undefined) {
        const el = document.getElementById('value-tags');
        if (el) {
            if (profileData.value_priorities && profileData.value_priorities.length > 0) {
                el.innerHTML = profileData.value_priorities.map(v => 
                    `<span class="attribute-tag tag-interface">${v}</span>`
                ).join('');
            } else {
                el.innerHTML = '<span class="text-sm text-gray-400">暂无数据</span>';
            }
        }
    }
    if (profileData.ability_assessment !== undefined) {
        const container = document.getElementById('ability-bars');
        if (container) {
            if (profileData.ability_assessment && Object.keys(profileData.ability_assessment).length > 0) {
                renderAbilityBars(profileData.ability_assessment);
            } else {
                container.innerHTML = '<span class="text-sm text-gray-400">暂无数据</span>';
            }
        }
    }
    
    // 更新可变层
    if (profileData.career_path_preference !== undefined) {
        const el = document.getElementById('career-path');
        if (el) {
            if (profileData.career_path_preference) {
                const pathNames = {
                    technical: '技术专家路径',
                    management: '管理领导路径',
                    professional: '专业方向路径',
                    public_welfare: '公益方向路径'
                };
                el.textContent = pathNames[profileData.career_path_preference] || profileData.career_path_preference;
            } else {
                el.textContent = '未设置';
            }
        }
    }
    
    // 更新偏好专业
    if (profileData.preferred_majors !== undefined) {
        const el = document.getElementById('major-tags');
        if (el) {
            if (profileData.preferred_majors && profileData.preferred_majors.length > 0) {
                el.innerHTML = profileData.preferred_majors.map(m => 
                    `<span class="attribute-tag tag-variable">专业${m}</span>`
                ).join('');
            } else {
                el.innerHTML = '<span class="text-sm text-gray-400">暂无数据</span>';
            }
        }
    }
    
    // 更新实践经历
    if (profileData.practice_experiences !== undefined) {
        const el = document.getElementById('practice-list');
        if (el) {
            if (profileData.practice_experiences && profileData.practice_experiences.length > 0) {
                el.innerHTML = profileData.practice_experiences.map(pe => 
                    `<div class="text-sm text-gray-600 mb-1">• ${pe.type}: ${pe.desc || ''}</div>`
                ).join('');
            } else {
                el.innerHTML = '<span class="text-sm text-gray-400">暂无数据</span>';
            }
        }
    }
    
    // 更新核心层
    if (profileData.universal_skills !== undefined) {
        const container = document.getElementById('skill-bars');
        if (container) {
            if (profileData.universal_skills && Object.keys(profileData.universal_skills).length > 0) {
                renderSkillBars(profileData.universal_skills);
            } else {
                container.innerHTML = '<span class="text-sm text-gray-400">暂无数据</span>';
            }
        }
    }
    
    if (profileData.resilience_score !== undefined) {
        const bar = document.getElementById('resilience-bar');
        const score = document.getElementById('resilience-score');
        if (bar) {
            if (profileData.resilience_score) {
                bar.style.width = `${profileData.resilience_score * 10}%`;
            } else {
                bar.style.width = '0%';
            }
        }
        if (score) {
            if (profileData.resilience_score) {
                score.textContent = `${profileData.resilience_score}/10`;
            } else {
                score.textContent = '0/10';
            }
        }
    }
    
    // 更新CASVE阶段
    if (profileData.current_casve_stage) {
        updateCasveStage(profileData.current_casve_stage);
    }
    
    // 更新完整度
    if (profileData.completeness_score !== undefined) {
        updateCompleteness(profileData.completeness_score);
    }
    
    // 同时更新全局状态
    if (typeof state !== 'undefined') {
        state.profile = { ...state.profile, ...profileData };
    }
}

// 显示本次提取到的信息通知（优雅提示）
function showExtractedInfoNotification(extractedInfo) {
    if (!extractedInfo || extractedInfo.length === 0) return;
    
    const fieldNames = {
        holland_code: '霍兰德代码',
        mbti_type: 'MBTI类型',
        value_priorities: '价值观',
        ability_assessment: '能力评估',
        career_path_preference: '职业路径偏好',
        current_casve_stage: 'CASVE阶段',
        nickname: '昵称',
        practice_experiences: '实践经历'
    };
    
    const fieldLabels = extractedInfo.map(info => fieldNames[info.field] || info.field);
    
    // 创建一个优雅的通知提示
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-gradient-to-r from-green-500 to-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in';
    notification.innerHTML = `
        <div class="flex items-center">
            <i class="fas fa-check-circle mr-2"></i>
            <span>已自动记录：${fieldLabels.join('、')}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // 3秒后自动消失
    setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        notification.style.transition = 'all 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ==================== 层展开/收起 ====================

function expandLayer(layerName) {
    const content = document.getElementById(`${layerName}-content`);
    const isVisible = content.style.display !== 'none';
    
    // 切换显示
    content.style.display = isVisible ? 'none' : 'block';
    
    // 添加动画
    if (!isVisible) {
        anime({
            targets: content,
            opacity: [0, 1],
            translateY: [-10, 0],
            duration: 300,
            easing: 'easeOutQuad'
        });
    }
}

// ==================== 辅助功能 ====================

// 加载聊天历史
async function loadChatHistory() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/user-profiles/${CONFIG.USER_ID}/chat/history?limit=20`);
        if (response.ok) {
            const history = await response.json();
            // 历史记录已在服务器保存，UI从当前会话开始
        }
    } catch (error) {
        console.error('[Chat] Load history error:', error);
    }
}

// 更新UI状态
function updateUIFromState() {
    // 可以在这里添加更多状态同步逻辑
}

// HTML转义
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 显示提示
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `fixed top-20 right-4 px-6 py-3 rounded-lg shadow-lg z-50 ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', init);

// 退出登录
function logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    localStorage.removeItem('user_id');
    window.location.href = 'index.html';
}

// 暴露全局函数
window.sendMessage = sendMessage;
window.sendIntent = sendIntent;
window.handleKeyPress = handleKeyPress;
window.clearChat = clearChat;
window.expandLayer = expandLayer;
window.logout = logout;
window.goToLogin = goToLogin;
