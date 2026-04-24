<script lang="ts">
	import { playTrack } from '$lib/player';

	let { data } = $props();

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
</script>

<section class="panel" style="margin-bottom: 0.75rem;">
	<h1 style="margin: 0 0 0.45rem; font-size: 1.2rem;">Search + Mood Tags</h1>
	<form method="GET" style="display: grid; grid-template-columns: 2fr 1fr auto; gap: 0.5rem;">
		<input name="q" value={data.q} placeholder="Search tracks and albums" />
		<select name="tag_id">
			<option value="">All moods</option>
			{#each data.tags as tag}
				<option value={tag.id} selected={data.tagId === String(tag.id)}>{tag.name}</option>
			{/each}
		</select>
		<button class="btn" type="submit">Apply</button>
	</form>
</section>

<section class="panel" style="margin-bottom: 0.75rem;">
	<h2 style="margin-top: 0; font-size: 1rem;">Artists</h2>
	<div class="grid-cards" style="grid-template-columns: repeat(3, minmax(0, 1fr));">
		{#each data.artists as artist}
			<a class="panel-soft" href={`/artist/${artist.artist_id}`}>
				<img class="cover-row" src={artist.profile_image_url} alt={artist.stage_name} />
				<div style="margin-top: 0.4rem;">{artist.stage_name}</div>
				<div class="muted">{artist.country ?? 'Unknown'}</div>
				<div class="muted">{artist.followers} followers · {artist.total_streams} streams</div>
			</a>
		{/each}
	</div>
</section>

<section class="grid-cards" style="margin-bottom: 0.75rem; grid-template-columns: 1.2fr 1fr;">
	<div class="panel">
		<h2 style="margin-top: 0; font-size: 1rem;">Tracks</h2>
		<div style="display: flex; flex-direction: column; gap: 0.55rem;">
			{#if data.results.tracks.length === 0}
				<div class="muted">No tracks match this filter.</div>
			{:else}
				{#each data.results.tracks as track}
					<button
						type="button"
						class="panel-soft"
						onclick={() => play(track)}
						style="display: flex; gap: 0.55rem; width: 100%; text-align: left;"
					>
						<img class="cover-row" src={track.track_cover_url} alt={track.title} />
						<div style="flex: 1; min-width: 0;">
							<div style="display: flex; justify-content: space-between; gap: 0.5rem;">
								<div>{track.title}</div>
								<span class="pill">{track.total_streams} streams</span>
							</div>
							<div class="muted">{track.album_title ?? 'Single'} · {track.language ?? 'NA'}</div>
							{#if track.tags}
								<div class="muted">{track.tags}</div>
							{/if}
						</div>
					</button>
				{/each}
			{/if}
		</div>
	</div>

	<div class="panel">
		<h2 style="margin-top: 0; font-size: 1rem;">Albums</h2>
		<div style="display: flex; flex-direction: column; gap: 0.55rem;">
			{#if data.results.albums.length === 0}
				<div class="muted">No albums match this filter.</div>
			{:else}
				{#each data.results.albums as album}
					<a href={`/album/${album.album_id}`} class="panel-soft" style="display: flex; gap: 0.55rem; text-decoration: none;">
						<img class="cover-row" src={album.album_cover_url} alt={album.title} />
						<div>
							<div>{album.title}</div>
							<div class="muted">{album.album_type ?? 'Album'} · {album.tracks_count} tracks</div>
							{#if album.tags}
								<div class="muted">{album.tags}</div>
							{/if}
						</div>
					</a>
				{/each}
			{/if}
		</div>
	</div>
</section>

<section class="panel">
	<h2 style="margin: 0 0 0.55rem; font-size: 1rem;">Top Songs Snapshot</h2>
	<div class="grid-cards" style="grid-template-columns: repeat(3, minmax(0, 1fr));">
		{#each data.topSongs as song}
			<button type="button" class="panel-soft" onclick={() => play(song)} style="text-align: left; width: 100%;">
				<img class="cover" src={song.album_cover_url} alt={song.title} />
				<div style="margin-top: 0.45rem;">{song.title}</div>
				<div class="muted">{song.album_title ?? 'Single'} · {song.total_streams}</div>
			</button>
		{/each}
	</div>
</section>
