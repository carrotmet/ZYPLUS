/**
 * 职业规划对话类型定义
 * TypeChat Schema 类型
 */

// 意图类型
export type IntentType = 
    | 'interest_explore' 
    | 'ability_assess' 
    | 'value_clarify'
    | 'career_advice' 
    | 'path_planning' 
    | 'casve_guidance'
    | 'general_chat'
    | 'emotional_support';

// 情感状态
export type EmotionalState = 
    | 'anxious' 
    | 'confident' 
    | 'curious' 
    | 'frustrated' 
    | 'neutral';

// 意图详情
export interface Intent {
    type: IntentType;
    confidence: number;
    subType?: string;
    contextSignals: string[];
    emotionalState: EmotionalState;
}

// 兴趣项
export interface InterestItem {
    domain: string;
    specific: string;
    sentiment: 'positive' | 'negative' | 'neutral';
    constraints?: string[];
}

// 能力项
export interface AbilityItem {
    skill: string;
    level: 'beginner' | 'intermediate' | 'advanced';
    evidence: string;
}

// 约束条件
export interface Constraint {
    type: 'time' | 'resource' | 'skill' | 'other';
    description: string;
}

// 提取的实体
export interface ExtractedEntities {
    interests: InterestItem[];
    abilities: AbilityItem[];
    values: string[];
    constraints: Constraint[];
}

// 预处理结果
export interface PreprocessedInput {
    rawText: string;
    cleanedText: string;
    intent: Intent;
    entities: ExtractedEntities;
    contextSummary: string;
    suggestedApproach: string;
}

// 对话历史项
export interface ConversationHistoryItem {
    role: 'user' | 'assistant';
    content: string;
    timestamp?: string;
}

// TypeChat 转换器配置
export interface TypeChatConfig {
    apiKey: string;
    model?: string;
    temperature?: number;
    maxTokens?: number;
}
