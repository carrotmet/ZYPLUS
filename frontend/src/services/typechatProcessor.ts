/**
 * TypeChat 预处理器
 * 将用户自然语言输入转换为结构化意图和实体
 */

import { PreprocessedInput, ConversationHistoryItem, TypeChatConfig } from '../types/careerChat';

// TypeChat Schema 定义（字符串形式）
const CAREER_CHAT_SCHEMA = `
interface Intent {
    type: "interest_explore" | "ability_assess" | "value_clarify" | 
          "career_advice" | "path_planning" | "casve_guidance" | 
          "general_chat" | "emotional_support";
    confidence: number;
    subType?: string;
    contextSignals: string[];
    emotionalState: "anxious" | "confident" | "curious" | "frustrated" | "neutral";
}

interface InterestItem {
    domain: string;
    specific: string;
    sentiment: "positive" | "negative" | "neutral";
    constraints?: string[];
}

interface AbilityItem {
    skill: string;
    level: "beginner" | "intermediate" | "advanced";
    evidence: string;
}

interface Constraint {
    type: "time" | "resource" | "skill" | "other";
    description: string;
}

interface ExtractedEntities {
    interests: InterestItem[];
    abilities: AbilityItem[];
    values: string[];
    constraints: Constraint[];
}

interface PreprocessedInput {
    rawText: string;
    cleanedText: string;
    intent: Intent;
    entities: ExtractedEntities;
    contextSummary: string;
    suggestedApproach: string;
}
`;

class TypeChatProcessor {
    private config: TypeChatConfig;
    private apiEndpoint: string;

    constructor(config: TypeChatConfig) {
        this.config = {
            model: 'gpt-3.5-turbo',
            temperature: 0.2,
            maxTokens: 1500,
            ...config
        };
        // 使用OpenAI兼容API
        this.apiEndpoint = this._getApiEndpoint();
    }

    private _getApiEndpoint(): string {
        // 检查是否使用Kimi
        if (this.config.apiKey.startsWith('sk-') && this.config.apiKey.length > 40) {
            return 'https://api.moonshot.cn/v1/chat/completions';
        }
        return 'https://api.openai.com/v1/chat/completions';
    }

    /**
     * 预处理用户输入
     * 将自然语言转换为结构化数据
     */
    async preprocess(
        rawText: string,
        conversationHistory: ConversationHistoryItem[] = []
    ): Promise<PreprocessedInput> {
        try {
            // 构建prompt
            const prompt = this._buildPrompt(rawText, conversationHistory);
            
            // 调用LLM
            const response = await this._callLLM(prompt);
            
            // 解析响应
            const parsed = this._parseResponse(response);
            
            return {
                rawText,
                cleanedText: rawText.trim(),
                ...parsed
            };
        } catch (error) {
            console.error('[TypeChat] Preprocess error:', error);
            // 返回默认值
            return this._getDefaultResult(rawText);
        }
    }

    /**
     * 构建LLM prompt
     */
    private _buildPrompt(
        rawText: string,
        history: ConversationHistoryItem[]
    ): string {
        const historyStr = history.length > 0 
            ? history.slice(-3).map(h => `${h.role === 'user' ? '用户' : 'AI'}: ${h.content}`).join('\n')
            : '（新对话）';

        return `你是一个职业规划对话分析助手。请将用户的输入分析为结构化数据。

${CAREER_CHAT_SCHEMA}

请分析以下对话：

对话历史：
${historyStr}

当前用户输入："${rawText}"

请以JSON格式返回 PreprocessedInput 对象，包含：
1. intent: 意图类型、置信度、子类型、上下文信号、情感状态
2. entities: 兴趣、能力、价值观、约束条件
3. contextSummary: 对话上下文摘要
4. suggestedApproach: 建议的处理方式

注意：
- 置信度范围0-1
- 识别隐含意图（如"没时间练习"=兴趣+时间约束）
- 情感状态要准确判断
- 只返回JSON，不要其他文字`;
    }

    /**
     * 调用LLM API
     */
    private async _callLLM(prompt: string): Promise<string> {
        const response = await fetch(this.apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.config.apiKey}`
            },
            body: JSON.stringify({
                model: this.config.model,
                messages: [
                    { role: 'system', content: '你是一个专业的职业规划对话分析助手。' },
                    { role: 'user', content: prompt }
                ],
                temperature: this.config.temperature,
                max_tokens: this.config.maxTokens
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        const data = await response.json();
        return data.choices[0]?.message?.content || '';
    }

    /**
     * 解析LLM响应
     */
    private _parseResponse(response: string): Partial<PreprocessedInput> {
        try {
            // 提取JSON
            const jsonMatch = response.match(/\{[\s\S]*\}/);
            if (!jsonMatch) {
                throw new Error('No JSON found in response');
            }

            const parsed = JSON.parse(jsonMatch[0]);

            // 验证和填充默认值
            return {
                intent: {
                    type: parsed.intent?.type || 'general_chat',
                    confidence: parsed.intent?.confidence || 0.5,
                    subType: parsed.intent?.subType,
                    contextSignals: parsed.intent?.contextSignals || [],
                    emotionalState: parsed.intent?.emotionalState || 'neutral'
                },
                entities: {
                    interests: parsed.entities?.interests || [],
                    abilities: parsed.entities?.abilities || [],
                    values: parsed.entities?.values || [],
                    constraints: parsed.entities?.constraints || []
                },
                contextSummary: parsed.contextSummary || '',
                suggestedApproach: parsed.suggestedApproach || ''
            };
        } catch (error) {
            console.error('[TypeChat] Parse error:', error);
            return this._getDefaultResult('').intent ? { 
                intent: this._getDefaultResult('').intent,
                entities: this._getDefaultResult('').entities,
                contextSummary: '',
                suggestedApproach: ''
            } : {
                intent: { type: 'general_chat', confidence: 0.5, contextSignals: [], emotionalState: 'neutral' },
                entities: { interests: [], abilities: [], values: [], constraints: [] },
                contextSummary: '',
                suggestedApproach: ''
            };
        }
    }

    /**
     * 获取默认结果
     */
    private _getDefaultResult(rawText: string): PreprocessedInput {
        return {
            rawText,
            cleanedText: rawText.trim(),
            intent: {
                type: 'general_chat',
                confidence: 0.5,
                contextSignals: [],
                emotionalState: 'neutral'
            },
            entities: {
                interests: [],
                abilities: [],
                values: [],
                constraints: []
            },
            contextSummary: '',
            suggestedApproach: '继续对话'
        };
    }

    /**
     * 快速意图识别（轻量级，不需要完整预处理）
     */
    async quickIntentDetect(rawText: string): Promise<string> {
        // 使用简单的关键词匹配作为fallback
        const text = rawText.toLowerCase();
        
        if (/喜欢|爱好|兴趣|热爱/.test(text)) return 'interest_explore';
        if (/擅长|能力|技能|会什么/.test(text)) return 'ability_assess';
        if (/重要|在乎|追求|价值/.test(text)) return 'value_clarify';
        if (/职业|工作|行业|建议/.test(text)) return 'career_advice';
        if (/规划|方向|怎么选|未来/.test(text)) return 'path_planning';
        if (/纠结|犹豫|不知道|怎么办/.test(text)) return 'casve_guidance';
        
        return 'general_chat';
    }
}

// 单例实例
let processorInstance: TypeChatProcessor | null = null;

/**
 * 获取TypeChat处理器实例
 */
export function getTypeChatProcessor(config?: TypeChatConfig): TypeChatProcessor {
    if (!processorInstance && config) {
        processorInstance = new TypeChatProcessor(config);
    }
    if (!processorInstance) {
        throw new Error('TypeChatProcessor not initialized');
    }
    return processorInstance;
}

/**
 * 初始化TypeChat处理器
 */
export function initTypeChatProcessor(config: TypeChatConfig): void {
    processorInstance = new TypeChatProcessor(config);
}

/**
 * 预处理用户输入（便捷函数）
 */
export async function preprocessUserInput(
    rawText: string,
    history?: ConversationHistoryItem[]
): Promise<PreprocessedInput> {
    const processor = getTypeChatProcessor();
    return processor.preprocess(rawText, history);
}

export default TypeChatProcessor;
