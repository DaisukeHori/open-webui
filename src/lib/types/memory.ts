export interface Memory {
    id: string;
    user_id: string;
    fact: string;
    created_at: string;
    updated_at: string;
}

export interface AutoMemorySettings {
    enabled: boolean;
    min_confidence: number;
}

export interface FactExtractionResult {
    facts: {
        fact: string;
        confidence: number;
    }[];
}