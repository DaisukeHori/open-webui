<script>
	import { toast } from 'svelte-sonner';

	import { onMount, getContext } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';

	import { getBackendConfig } from '$lib/apis';
	import { getSessionUser } from '$lib/apis/auths';

	import { WEBUI_API_BASE_URL, WEBUI_BASE_URL } from '$lib/constants';
	import { WEBUI_NAME, config, user, socket } from '$lib/stores';

	import { generateInitialsImage, canvasPixelTest } from '$lib/utils';

	import Spinner from '$lib/components/common/Spinner.svelte';
	import OnBoarding from '$lib/components/OnBoarding.svelte';

	const i18n = getContext('i18n');

	let loaded = false;

	const querystringValue = (key) => {
		const querystring = window.location.search;
		const urlParams = new URLSearchParams(querystring);
		return urlParams.get(key);
	};

	const setSessionUser = async (sessionUser) => {
		if (sessionUser) {
			console.log(sessionUser);
			toast.success($i18n.t(`You're now logged in.`));
			if (sessionUser.token) {
				localStorage.token = sessionUser.token;
			}

			$socket.emit('user-join', { auth: { token: sessionUser.token } });
			await user.set(sessionUser);
			await config.set(await getBackendConfig());

			const redirectPath = querystringValue('redirect') || '/';
			goto(redirectPath);
		}
	};

	const checkOauthCallback = async () => {
		if (!$page.url.hash) {
			return;
		}
		const hash = $page.url.hash.substring(1);
		if (!hash) {
			return;
		}
		const params = new URLSearchParams(hash);
		const token = params.get('token');
		if (!token) {
			return;
		}
		const sessionUser = await getSessionUser(token).catch((error) => {
			toast.error(`${error}`);
			return null;
		});
		if (!sessionUser) {
			return;
		}
		localStorage.token = token;
		await setSessionUser(sessionUser);
	};


	onMount(async () => {
		if ($user !== undefined) {
			await goto('/');
		}
		await checkOauthCallback();

		loaded = true;
		if (($config?.features.auth_trusted_header ?? false) || $config?.features.auth === false) {
		}
	});
</script>

<svelte:head>
	<title>
		{`${$WEBUI_NAME}`}
	</title>
</svelte:head>

<div class="w-full h-screen max-h-[100dvh] text-white relative">
	<div class="w-full h-full absolute top-0 left-0 bg-white dark:bg-black"></div>

	<div class="w-full absolute top-0 left-0 right-0 h-8 drag-region" />

	{#if loaded}
		<div class="fixed m-10 z-50">
			<div class="flex space-x-2">
				<div class=" self-center">
					<img
						crossorigin="anonymous"
						src="{WEBUI_BASE_URL}/static/splash.png"
						class=" w-6 rounded-full dark:invert"
						alt="logo"
					/>
				</div>
			</div>
		</div>

		<div
			class="fixed bg-transparent min-h-screen w-full flex justify-center font-primary z-50 text-black dark:text-white"
		>
			<div class="w-full sm:max-w-md px-10 min-h-screen flex flex-col text-center">
				{#if ($config?.features.auth_trusted_header ?? false) || $config?.features.auth === false}
					<div class=" my-auto pb-10 w-full">
						<div
							class="flex items-center justify-center gap-3 text-xl sm:text-2xl text-center font-semibold dark:text-gray-200"
						>
							<div>
								{$i18n.t('Signing in to {{WEBUI_NAME}}', { WEBUI_NAME: $WEBUI_NAME })}
							</div>

							<div>
								<Spinner />
							</div>
						</div>
					</div>
				{:else}
					<div class="my-auto pb-10 w-full dark:text-gray-100">
						<div class="mb-1">
							<div class="text-2xl font-medium">
								{$i18n.t(`Sign in to {{WEBUI_NAME}}`, { WEBUI_NAME: $WEBUI_NAME })}<br/>
								<p class="text-base mt-2">Revol GPTへようこそ。従業員の皆さんはMicrosoft アカウントでログインできます。</p>
							</div>
						</div>
						
							<div class="flex flex-col space-y-2">
								<button
									class="flex justify-center items-center bg-gray-700/5 hover:bg-gray-700/10 dark:bg-gray-100/5 dark:hover:bg-gray-100/10 dark:text-gray-300 dark:hover:text-white transition w-full rounded-full font-medium text-sm py-2.5"
									on:click={() => {
										window.location.href = `${WEBUI_BASE_URL}/oauth/microsoft/login`;
									}}
								>
									<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 21 21" class="size-6 mr-3">
										<rect x="1" y="1" width="9" height="9" fill="#f25022" /><rect
											x="1"
											y="11"
											width="9"
											height="9"
											fill="#00a4ef"
										/><rect x="11" y="1" width="9" height="9" fill="#7fba00" /><rect
											x="11"
											y="11"
											width="9"
											height="9"
											fill="#ffb900"
										/>
									</svg>
									<span>{$i18n.t('Continue with {{provider}}', { provider: 'Microsoft' })}</span>
								</button>
							</div>
						
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>
