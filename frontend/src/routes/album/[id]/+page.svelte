<script lang="ts">
	import { playTrack } from '$lib/player';

	let { data } = $props();
	const albumData = $derived(data.data);

	function play(track: {
		track_id: number;
		title: string;
		album_title: string;
		track_cover_url: string;
		audio_url: string;
	}) {
		playTrack({
			track_id: track.track_id,
			title: track.title,
			album_title: albumData.album.title,
			track_cover_url: track.track_cover_url,
			audio_url: track.audio_url
		});
	}
</script>

<section class="panel" style="margin-bottom: 0.75rem;">
	<div style="display: grid; grid-template-columns: 140px 1fr 210px; gap: 0.75rem; align-items: start;">
		<img class="cover" style="aspect-ratio: 1 / 1;" src={albumData.album.album_cover_url} alt={albumData.album.title} />
		<div>
			<h1 style="margin: 0; font-size: 1.45rem;">{albumData.album.title}</h1>
			<a href={`/artist/${albumData.album.artist_id}`} class="muted">{albumData.album.artist_name}</a>
			<div class="muted">{albumData.album.release_date ?? 'Unknown'} · {albumData.album.album_type ?? 'Album'} · {albumData.album.language ?? 'Unknown'}</div>
			{#if albumData.album.tags}
				<div class="muted">{albumData.album.tags}</div>
			{/if}
		</div>
		<div class="panel-soft">
			<div class="muted">Tracks</div>
			<div class="kpi">{albumData.album.tracks_count}</div>
			<div class="muted">Total: {albumData.album.total_duration ?? 0}s</div>
		</div>
	</div>
</section>

<section class="panel" style="margin-bottom: 0.75rem;">
	<h2 style="margin-top: 0; font-size: 1rem;">Songs</h2>
	<div style="display: flex; flex-direction: column; gap: 0.55rem;">
		{#if albumData.tracks.length === 0}
			<div class="muted">No tracks in this album.</div>
		{:else}
			{#each albumData.tracks as track, index}
				<button
					type="button"
					class="panel-soft"
					onclick={() => play(track)}
					style="display: flex; gap: 0.55rem; width: 100%; text-align: left;"
				>
					<div class="muted" style="width: 1.5rem; text-align: center;">{index + 1}</div>
					<img class="cover-row" src={track.track_cover_url} alt={track.title} />
					<div style="flex: 1; min-width: 0;">
						<div style="display: flex; justify-content: space-between; gap: 0.5rem;">
							<div>{track.title}</div>
							<div class="pill">{track.total_streams} streams</div>
						</div>
						<div class="muted">{track.duration ?? 0}s · {track.language ?? 'NA'}</div>
					</div>
				</button>
			{/each}
		{/if}
	</div>
</section>