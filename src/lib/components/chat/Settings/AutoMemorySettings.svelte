<script lang="ts">
	import { onMount, createEventDispatcher } from 'svelte';
	import { getAutoMemorySettings, updateAutoMemorySettings } from '$lib/apis/auto-memory';
	import type { AutoMemorySettings } from '$lib/types/memory';
	import { t } from '$lib/i18n';
	import Card from '$lib/components/common/Card.svelte';
	import Switch from '$lib/components/common/Switch.svelte';
	import RangeSlider from '$lib/components/common/RangeSlider.svelte';
	
	// General.svelteからのバインディング用プロパティ
	export let enabled = false;
	export let minConfidence = 0.7;
	
	const dispatch = createEventDispatcher();

	$: settings = {
		enabled,
		min_confidence: 0.7
	};

	let isSaving = false;
	let isLoading = true;

	onMount(async () => {
		try {
			const fetchedSettings = await getAutoMemorySettings();
			// コンポーネント外部のバインディングを更新
			enabled = fetchedSettings.enabled;
			minConfidence = fetchedSettings.min_confidence;
		} catch (error) {
			console.error('Failed to load auto memory settings:', error);
		} finally {
			isLoading = false;
		}
	});
	
	// プロパティが変更されたら設定オブジェクトを更新
	$: {
		if (!isLoading) {
			settings = { enabled, min_confidence: minConfidence };
			dispatch('change', { enabled, minConfidence });
		}
	}
	
	async function saveSettings() {
		isSaving = true;
		try {
			const success = await updateAutoMemorySettings(settings);
			if (!success) {
				throw new Error('Failed to update settings');
			}
		} catch (error) {
			console.error('Error saving settings:', error);
			// 設定の保存に失敗した場合、設定を再取得
			try {
				const fetchedSettings = await getAutoMemorySettings();
				enabled = fetchedSettings.enabled;
				minConfidence = fetchedSettings.min_confidence;
			} catch (e) {
				console.error('Failed to reload settings:', e);
			}
		} finally {
			isSaving = false;
		}
	}
</script>

<Card title={$t('自動メモリ抽出')} description={$t('メッセージからユーザーに関する事実を自動的に抽出してメモリに保存します')}>
	<div class="flex flex-col gap-4">
		<div class="flex items-center justify-between w-full">
			<div class="flex flex-col">
				<span class="font-medium">{$t('自動メモリ抽出')}</span>
				<span class="text-sm opacity-60">{$t('有効にすると、チャットからユーザーに関する事実を自動的に抽出します')}</span>
			</div>
			<Switch 
				on:change={() => saveSettings()}
				checked={enabled}
				bind:checked={settings.enabled}
				disabled={isLoading || isSaving}
			/>
		</div>

		{#if settings.enabled}
			<div class="flex flex-col gap-2 mt-2">
				<div class="flex justify-between items-center">
					<span class="font-medium">{$t('最小信頼度スコア')}</span>
					<span class="text-sm opacity-80">{Math.round(minConfidence * 100)}%</span>
				</div>
				<RangeSlider
					on:change={() => saveSettings()}
					value={minConfidence}
					bind:value={settings.min_confidence}
					min={0}
					max={1}
					step={0.05}
					disabled={isLoading || isSaving}
				/>
				<span class="text-sm opacity-60">
					{$t('信頼度が低い事実は無視されます。高い値に設定すると、より確実な事実のみが保存されます。')}
				</span>
			</div>
		{/if}
	</div>
</Card>