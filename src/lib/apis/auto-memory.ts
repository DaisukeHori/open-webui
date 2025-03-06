import { request } from '$lib/apis/utils/request';
import type { Memory, AutoMemorySettings, FactExtractionResult } from '$lib/types/memory';

/**
 * 自動メモリ抽出設定を取得する
 */
export const getAutoMemorySettings = async (): Promise<AutoMemorySettings> => {
    try {
        const response = await request('/api/v1/auto-memory/settings');
        return response as AutoMemorySettings;
    } catch (error) {
        console.error('Failed to get auto memory settings:', error);
        return { enabled: false, min_confidence: 0.7 };
    }
};

/**
 * 自動メモリ抽出設定を更新する
 */
export const updateAutoMemorySettings = async (settings: AutoMemorySettings): Promise<boolean> => {
    try {
        await request('/api/v1/auto-memory/settings', {
            method: 'POST',
            body: JSON.stringify(settings)
        });
        return true;
    } catch (error) {
        console.error('Failed to update auto memory settings:', error);
        return false;
    }
};

/**
 * ユーザーのメモリ一覧を取得する
 */
export const getMemories = async (): Promise<Memory[]> => {
    try {
        const response = await request('/api/v1/auto-memory');
        return response.memories || [];
    } catch (error) {
        console.error('Failed to get memories:', error);
        return [];
    }
};

/**
 * メモリを削除する
 */
export const deleteMemory = async (memoryId: string): Promise<boolean> => {
    try {
        await request(`/api/v1/auto-memory/${memoryId}`, {
            method: 'DELETE'
        });
        return true;
    } catch (error) {
        console.error('Failed to delete memory:', error);
        return false;
    }
};

/**
 * テキストから手動で事実を抽出する
 */
export const extractFacts = async (content: string): Promise<FactExtractionResult> => {
    try {
        const response = await request('/api/v1/auto-memory/manual-extract', {
            method: 'POST',
            body: JSON.stringify({ content })
        });
        return response as FactExtractionResult;
    } catch (error) {
        console.error('Failed to extract facts:', error);
        return { facts: [] };
    }
};