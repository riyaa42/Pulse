<script lang="ts">
	import { onMount } from 'svelte';
	import { currentTime, currentTrack, duration, isPlaying, playTrack } from '$lib/player';
	import { apiGet, apiPost } from '$lib/api';
	import { hydrateSession, session, switchSessionActor } from '$lib/session';
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
	let audioEl = $state<HTMLAudioElement | null>(null);
	let simTimer: ReturnType<typeof setInterval> | null = null;
	let profileOpen = $state(false);
	let activeStreamId = $state<number | null>(null);
	let activeStreamTrackId = $state<number | null>(null);
	let nowContext = $state<{
		track: {
			track_id: number;
			title: string;
			artist_name: string | null;
			artist_bio: string | null;
			artist_profile_url?: string;
		};
		related_tracks: {
			track_id: number;
			title: string;
			artist_name: string | null;
			track_cover_url: string;
			audio_url: string;
			album_title: string | null;
		}[];
	} | null>(null);

	function clearSimTimer() {
		if (simTimer) {
			clearInterval(simTimer);
			simTimer = null;
		}
	}

	function formatTime(value: number): string {
		const safe = Number.isFinite(value) ? Math.max(0, Math.floor(value)) : 0;
		const minutes = Math.floor(safe / 60);
		const seconds = String(safe % 60).padStart(2, '0');
		return `${minutes}:${seconds}`;
	}

	function useSimulatedPlayback() {
		clearSimTimer();
		duration.set(180);
		simTimer = setInterval(() => {
			if (!$isPlaying) {
				return;
			}
			currentTime.update((value) => {
				const next = value + 1;
				if (next >= 180) {
					isPlaying.set(false);
					return 180;
				}
				return next;
			});
		}, 1000);
	}

	function syncPlayback() {
		if (!$currentTrack || !$isPlaying) {
			if (audioEl) {
				audioEl.pause();
			}
			clearSimTimer();
			return;
		}

		const source = $currentTrack.audio_url ?? '';
		const isAudioFile = /\.(mp3|wav|ogg|flac|m4a)$/i.test(source);

		if (!audioEl || !isAudioFile) {
			useSimulatedPlayback();
			return;
		}

		clearSimTimer();
		if (audioEl.src !== source) {
			audioEl.src = source;
		}
		audioEl.play().catch(() => {
			useSimulatedPlayback();
		});
	}

	function togglePlayback() {
		isPlaying.update((value) => !value);
	}

	async function startStreamEvent(trackId: number) {
		if ($session.current?.actor_type !== 'listener') {
			return;
		}
		if (activeStreamId && activeStreamTrackId === trackId) {
			return;
		}
		const response = await apiPost<{ stream_id: number }>('/api/streams/start', {
			track_id: trackId,
			device_type: 'Desktop',
			country: 'Unknown'
		});
		activeStreamId = response.stream_id;
		activeStreamTrackId = trackId;
	}

	async function endStreamEvent(completed: boolean) {
		if (!activeStreamId || $session.current?.actor_type !== 'listener') {
			return;
		}
		await apiPost('/api/streams/end', {
			stream_id: activeStreamId,
			completed,
			skipped_at: completed ? null : Math.floor($currentTime || 0)
		});
		activeStreamId = null;
		activeStreamTrackId = null;
	}

	async function refreshNowPlayingContext() {
		if (!$currentTrack?.track_id) {
			nowContext = null;
			return;
		}
		nowContext = await apiGet<{
			track: {
				track_id: number;
				title: string;
				artist_name: string | null;
				artist_bio: string | null;
				artist_profile_url?: string;
			};
			related_tracks: {
				track_id: number;
				title: string;
				artist_name: string | null;
				track_cover_url: string;
				audio_url: string;
				album_title: string | null;
			}[];
		}>(`/api/tracks/${$currentTrack.track_id}/context`, fetch);
	}

	onMount(async () => {
		await hydrateSession();
	});

	$effect(() => {
		syncPlayback();
	});

	$effect(() => {
		if ($isPlaying && $currentTrack?.track_id) {
			void startStreamEvent($currentTrack.track_id);
		} else if (!$isPlaying && activeStreamId) {
			void endStreamEvent(false);
		}
	});

	$effect(() => {
		const trackId = $currentTrack?.track_id ?? null;
		if (activeStreamId && activeStreamTrackId && trackId !== activeStreamTrackId) {
			void endStreamEvent(false);
		}
	});

	$effect(() => {
		void refreshNowPlayingContext();
	});
</script>

<svelte:head><link rel="icon" href={favicon} /></svelte:head>

<div class="desktop-shell">
	<header class="topbar shell-outline">
		<div class="top-left">
			<a href="/" class="brand">Pulse</a>
			<a href="/search" class="chip-link">Discover</a>
		</div>
		<div class="top-search">What do you want to play?</div>
		<div class="top-right">
			<button class="profile-btn" type="button" onclick={() => (profileOpen = !profileOpen)}>
				<img src={$session.current?.profile_image_url} alt={$session.current?.username ?? 'profile'} />
				<span>{$session.current?.username ?? 'profile'}</span>
			</button>
			{#if profileOpen}
				<div class="profile-menu panel-soft">
					{#if $session.current?.actor_type === 'artist'}
						<a class="profile-option" href={`/artist/${$session.current?.artist_id}`}>
							<div>View Profile</div>
							<div class="muted">Public artist page</div>
						</a>
					{:else}
						<a class="profile-option" href={`/user/${$session.current?.user_id}`}>
							<div>View Profile</div>
							<div class="muted">Listener profile</div>
						</a>
					{/if}
					<div class="muted" style="margin-bottom: 0.25rem;">Listeners</div>
					{#each $session.listeners as listener}
						<button class="profile-option" type="button" onclick={() => switchSessionActor('listener', listener.user_id)}>
							<div>{listener.username}</div>
							<div class="muted">Listener · user #{listener.user_id}</div>
						</button>
					{/each}
					<div class="muted" style="margin: 0.4rem 0 0.25rem;">Artists</div>
					{#each $session.artists as artist}
						<button class="profile-option" type="button" onclick={() => switchSessionActor('artist', artist.artist_id)}>
							<div>{artist.stage_name}</div>
							<div class="muted">Artist · id #{artist.artist_id}</div>
						</button>
					{/each}
				</div>
			{/if}
		</div>
	</header>

	<div class="workspace">
		<aside class="left-rail shell-outline">
			<div class="rail-section-title">Your Library</div>
			<div class="thumb-column">
				{#if $session.current?.actor_type === 'artist'}
					<a class="library-item" href={`/artist/${$session.current?.artist_id}`}>My Profile</a>
					<a class="library-item" href="/">Artist Studio</a>
					<a class="library-item" href="/search">Discover</a>
				{:else}
					<a class="library-item" href={`/user/${$session.current?.user_id}`}>My Profile</a>
					<a class="library-item" href="/search">Discover</a>
					{#each $session.playlists as playlist}
						<a class="library-item" href={`/playlist/${playlist.playlist_id}`}>
							<span>{playlist.name}</span>
							<span class="muted">{playlist.tracks_count}</span>
						</a>
					{/each}
				{/if}
			</div>
		</aside>

		<main class="content-area shell-outline">
			{@render children()}
		</main>

		<aside class="right-rail shell-outline">
			<div class="rail-section-title">Now Playing</div>
			{#if nowContext?.track}
				<div class="panel-soft">
					<img class="cover" src={nowContext.track.artist_profile_url} alt={nowContext.track.artist_name ?? nowContext.track.title} />
					<div style="margin-top: 0.5rem; font-weight: 600;">{nowContext.track.title}</div>
					<div class="muted">{nowContext.track.artist_name ?? 'Unknown artist'}</div>
					<div class="muted" style="margin-top: 0.35rem;">{nowContext.track.artist_bio ?? 'No bio available yet.'}</div>
				</div>
				<div class="rail-section-title">More from this artist</div>
				<div class="related-list">
					{#each nowContext.related_tracks as track}
						<button
							type="button"
							class="related-item"
							onclick={() =>
								playTrack({
									track_id: track.track_id,
									title: track.title,
									album_title: track.album_title,
									track_cover_url: track.track_cover_url,
									audio_url: track.audio_url
								})}
						>
							<img class="cover-row" src={track.track_cover_url} alt={track.title} />
							<div>
								<div>{track.title}</div>
								<div class="muted">{track.artist_name ?? 'Unknown artist'}</div>
							</div>
						</button>
					{/each}
				</div>
			{:else}
				<div class="panel-soft muted">Play any track to see artist context here.</div>
			{/if}
		</aside>
	</div>

	<footer class="player-strip shell-outline">
		<div class="player-main">
			<div class="player-meta">
				<img class="cover-row" src={$currentTrack?.track_cover_url} alt={$currentTrack?.title ?? 'track'} />
				<div>
					<div style="font-weight: 600;">{$currentTrack?.title ?? 'No track selected'}</div>
					<div class="muted">{$currentTrack?.album_title ?? 'Pick a song from home or discover'}</div>
				</div>
			</div>
			<div class="player-controls">
				<button class="play-btn" type="button" onclick={togglePlayback} aria-label="Play or pause">
					{#if $isPlaying}❚❚{:else}▶{/if}
				</button>
				<div class="muted">{formatTime($currentTime)} / {formatTime($duration)}</div>
			</div>
			<div></div>
		</div>
		<div class="progress-wrap">
			<div class="progress-line">
				<div class="progress-fill" style={`width: ${$duration > 0 ? Math.min(100, ($currentTime / $duration) * 100) : 0}%`}></div>
			</div>
		</div>
		<audio
			bind:this={audioEl}
			onloadedmetadata={() => duration.set(audioEl?.duration ?? 0)}
			onended={() => {
				isPlaying.set(false);
				void endStreamEvent(true);
			}}
			ontimeupdate={() => currentTime.set(audioEl?.currentTime ?? 0)}
		></audio>
	</footer>
</div>
