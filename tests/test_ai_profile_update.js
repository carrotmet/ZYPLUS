/**
 * AI隐式调用表单更新测试 - 前端代码
 * 
 * 在浏览器控制台执行以下代码测试AI隐式更新功能
 */

// ==================== 测试1: 基础AI更新 ====================

/**
 * 测试AI隐式更新画像
 * 
 * 使用场景：AI从用户对话中提取信息后，自动更新用户画像
 * 调用方式：ProfileForm.updateByAI(userId, updates, reason)
 */
async function testAIProfileUpdate() {
    console.log('=== 测试AI隐式更新画像 ===');
    
    // 获取当前用户ID
    const userId = localStorage.getItem('user_id');
    if (!userId) {
        console.error('错误：未找到用户ID，请先登录');
        return;
    }
    console.log('当前用户ID:', userId);
    
    // 模拟AI从对话中提取的结构化数据
    // 示例对话："我喜欢编程，想走技术路线，擅长逻辑思维，重视创新和成就感"
    const aiExtractedData = {
        career_path_preference: 'technical',  // 技术专家路径
        value_priorities: ['成就感', '创新', '成长'],
        ability_assessment: {
            logic: 8,
            creativity: 7,
            communication: 6
        },
        current_casve_stage: 'analysis',  // 推进到分析阶段
        resilience_score: 8
    };
    
    console.log('AI提取的数据:', aiExtractedData);
    
    // 检查ProfileForm模块是否可用
    if (typeof ProfileForm === 'undefined') {
        console.error('错误：ProfileForm模块未加载，请确保已引入profile-form.js');
        return;
    }
    
    try {
        // 调用AI更新接口（隐式更新，不打开表单）
        const result = await ProfileForm.updateByAI(
            userId,
            aiExtractedData,
            '从对话"我想成为技术专家"中提取'
        );
        
        console.log('AI更新结果:', result);
        
        if (result.success) {
            console.log('✓ AI隐式更新成功!');
            console.log('  更新字段:', result.data.updated_fields);
            console.log('  新完整度:', result.data.profile.completeness_score + '%');
            
            // 刷新UI显示
            if (typeof updateUIFromProfileData === 'function') {
                updateUIFromProfileData(result.data.profile);
                console.log('✓ UI已刷新');
            }
        } else {
            console.error('✗ AI更新失败:', result.error);
        }
    } catch (error) {
        console.error('✗ 测试出错:', error);
    }
}


// ==================== 测试2: 模拟RAG对话流程 ====================

/**
 * 模拟完整的RAG对话处理流程
 * 
 * 流程：用户输入 -> RAG处理 -> 提取信息 -> AI更新 -> 更新UI
 */
async function testRAGFlowWithAIUpdate() {
    console.log('=== 测试RAG对话流程（含AI更新）===');
    
    const userId = localStorage.getItem('user_id');
    if (!userId) {
        console.error('错误：未找到用户ID');
        return;
    }
    
    // 模拟用户消息
    const userMessage = "我擅长逻辑思维，喜欢解决复杂问题，希望走技术专家路线";
    console.log('用户输入:', userMessage);
    
    // 模拟RAG服务返回的结果
    const mockRAGResult = {
        reply: "逻辑思维和技术专家路线很匹配！你有很强的分析能力。",
        intent: "career_advice",
        extracted_info: [
            { field: "ability_assessment", value: { logic: 8, analysis: 9 }, confidence: 0.9 },
            { field: "career_path_preference", value: "technical", confidence: 0.95 }
        ],
        profile_updates: {
            career_path_preference: "technical",
            ability_assessment: { logic: 8, analysis: 9 }
        }
    };
    
    console.log('RAG处理结果:', mockRAGResult);
    
    // 调用AI更新
    if (mockRAGResult.profile_updates && Object.keys(mockRAGResult.profile_updates).length > 0) {
        const result = await ProfileForm.updateByAI(
            userId,
            mockRAGResult.profile_updates,
            'RAG从对话中提取'
        );
        
        if (result.success) {
            console.log('✓ RAG流程完成：对话 -> 提取 -> AI更新 -> UI刷新');
            
            // 显示通知
            if (typeof showExtractedInfoNotification === 'function') {
                showExtractedInfoNotification(mockRAGResult.extracted_info);
            }
        }
    }
}


// ==================== 测试3: 批量字段更新 ====================

/**
 * 测试同时更新多个字段
 */
async function testBatchAIUpdate() {
    console.log('=== 测试批量AI更新 ===');
    
    const userId = localStorage.getItem('user_id');
    
    // 模拟一次完整的画像信息收集
    const completeProfileData = {
        holland_code: 'RIA',
        mbti_type: 'INTJ',
        value_priorities: ['成就感', '创新', '成长', '自由'],
        ability_assessment: {
            logic: 9,
            creativity: 7,
            communication: 6,
            teamwork: 5,
            leadership: 7,
            analysis: 9
        },
        career_path_preference: 'technical',
        universal_skills: {
            communication: 7,
            teamwork: 6,
            critical_thinking: 9,
            creativity: 7,
            problem_solving: 9,
            adaptability: 8
        },
        resilience_score: 8,
        current_casve_stage: 'analysis'
    };
    
    console.log('批量更新数据:', completeProfileData);
    
    const result = await ProfileForm.updateByAI(
        userId,
        completeProfileData,
        '完整画像信息收集'
    );
    
    if (result.success) {
        console.log('✓ 批量更新成功!');
        console.log('  更新字段数:', result.data.updated_fields.length);
        console.log('  预计完整度:', result.data.profile.completeness_score + '%');
    }
}


// ==================== 测试4: 对比手动表单和AI隐式调用 ====================

/**
 * 对比两种更新方式
 */
async function compareUpdateMethods() {
    console.log('=== 对比更新方式 ===');
    
    const userId = localStorage.getItem('user_id');
    
    console.log('方式1: 手动表单（用户主动）');
    console.log('  - 调用: ProfileForm.open(userId, data, callback)');
    console.log('  - 特点: 弹出表单，用户可见，可编辑');
    console.log('  - 适用: 用户主动完善信息');
    
    console.log('\n方式2: AI隐式调用（AI自动）');
    console.log('  - 调用: ProfileForm.updateByAI(userId, updates, reason)');
    console.log('  - 特点: 静默更新，无弹窗，自动完成');
    console.log('  - 适用: AI从对话中提取信息');
    
    console.log('\n两种方式的API端点：');
    console.log('  - 手动表单: POST /api/user-profiles/{user_id}/form-update');
    console.log('  - AI隐式:   POST /api/user-profiles/{user_id}/ai-update');
}


// ==================== 快速测试入口 ====================

// 在控制台输入以下命令执行测试：
// testAIProfileUpdate()      - 测试基础AI更新
// testRAGFlowWithAIUpdate()  - 测试RAG完整流程
// testBatchAIUpdate()        - 测试批量更新
// compareUpdateMethods()     - 对比更新方式

console.log('AI隐式调用测试脚本已加载');
console.log('可用测试函数:');
console.log('  testAIProfileUpdate() - 基础AI更新测试');
console.log('  testRAGFlowWithAIUpdate() - RAG流程测试');
console.log('  testBatchAIUpdate() - 批量更新测试');
console.log('  compareUpdateMethods() - 对比更新方式');
