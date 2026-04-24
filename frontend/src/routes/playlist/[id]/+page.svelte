<script lang="ts">
	import { apiDelete } from '$lib/api';
	import { playTrack } from '$lib/player';

	let { data } = $props();
	const playlistData = $derived(data.data);
	let message = $state('');

	function play(track: {
		track_id: number;
		title: string;
		album_title: string | null;
		track_cover_url: string;
		audio_url: string;
	}) {
		playTrack({
			track_id: track.track_id,
			title: track.title,
			album_title: track.album_title,
			track_cover_url: track.track_cover_url,
			audio_url: track.audio_url
		});
	}

	async function removeTrack(trackId: number) {
		message = '';
		try {
			await apiDelete(`/api/playlists/${playlistData.playlist.playlist_id}/tracks/${trackId}`);
			message = 'Track removed.';
			window.location.reload();
		} catch (error) {
			message = error instanceof Error ? error.message : 'Could not remove track.';
		}
	}

	async function deletePlaylist() {
		message = '';
		try {
			await apiDelete(`/api/playlists/${playlistData.playlist.playlist_id}`);
			window.location.href = '/';
		} catch (error) {
			message = error instanceof Error ? error.message : 'Could not delete playlist.';
		}
	}
</script>

<section class="panel" style="margin-bottom: 0.75rem;">
	<h1 style="margin: 0; font-size: 1.4rem;">{playlistData.playlist.name}</h1>
	<div class="muted" style="margin-top: 0.2rem;">
		Owner: @{playlistData.playlist.owner_username} · {playlistData.playlist.tracks_count} tracks
	</div>
	{#if playlistData.playlist.description}
		<p class="muted">{playlistData.playlist.description}</p>
	{/if}
	{#if playlistData.playlist.can_edit}
		<button class="btn" type="button" onclick={deletePlaylist}>Delete Playlist</button>
	{/if}
	{#if message}
		<p class="muted">{message}</p>
	{/if}
</section>

<section class="panel">
	<h2 style="margin-top: 0; font-size: 1rem;">Tracks</h2>
	{#if playlistData.tracks.length === 0}
		<div class="muted">No tracks yet in this playlist.</div>
	{:else}
		<div style="display: flex; flex-direction: column; gap: 0.55rem;">
			{#each playlistData.tracks as track}
				<div class="panel-soft" style="display: flex; gap: 0.55rem; align-items: center;">
					<button type="button" onclick={() => play(track)} style="display: flex; gap: 0.55rem; text-align: left; flex: 1;">
						<img class="cover-row" src={track.track_cover_url} alt={track.title} />
						<div style="flex: 1; min-width: 0;">
							<div style="display: flex; justify-content: space-between; gap: 0.4rem;">
								<div>{track.title}</div>
								<div class="pill">{track.total_streams} streams</div>
							</div>
							<div class="muted">{track.artist_name ?? 'Unknown artist'} · {track.album_title ?? 'Single'}</div>
							<div class="muted">Added: {track.added_at}</div>
						</div>
					</button>
					{#if playlistData.playlist.can_edit}
						<button class="btn" type="button" onclick={() => removeTrack(track.track_id)}>Remove</button>
					{/if}
				</div>
			{/each}
		</div>
	{/if}
</section>
