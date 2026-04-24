<script lang="ts">
	import { apiDelete, apiPost } from '$lib/api';
	import { playTrack } from '$lib/player';

	let { data } = $props();
	const artistData = $derived(data.data);
	let expandedBio = $state(false);
	let followMessage = $state('');
	let isFollowing = $state(false);

	$effect(() => {
		isFollowing = artistData.artist.is_following;
	});

	async function followArtist() {
		followMessage = '';
		try {
			await apiPost('/api/follow/artist', {
				artist_id: artistData.artist.artist_id
			});
			followMessage = 'Artist followed successfully.';
			isFollowing = true;
		} catch (error) {
			followMessage = error instanceof Error ? error.message : 'Failed to follow artist.';
		}
	}

	async function unfollowArtist() {
		followMessage = '';
		try {
			await apiDelete(`/api/follow/artist/${artistData.artist.artist_id}`);
			followMessage = 'Artist unfollowed.';
			isFollowing = false;
		} catch (error) {
			followMessage = error instanceof Error ? error.message : 'Failed to unfollow artist.';
		}
	}

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
			album_title: track.album_title,
			track_cover_url: track.track_cover_url,
			audio_url: track.audio_url
		});
	}
</script>

<section class="panel" style="margin-bottom: 0.75rem;">
	<div style="display: grid; grid-template-columns: 140px 1fr 210px; gap: 0.75rem; align-items: start;">
		<img class="cover" style="aspect-ratio: 1 / 1;" src={artistData.artist.profile_image_url} alt={artistData.artist.stage_name} />
		<div>
			<h1 style="margin: 0; font-size: 1.45rem;">{artistData.artist.stage_name}</h1>
			<div class="muted">{artistData.artist.country ?? 'Unknown'} · {artistData.artist.verification_status}</div>
			<div class="panel-soft" style="margin-top: 0.55rem;">
				<div style="display: flex; justify-content: space-between; align-items: center;">
					<strong>Bio</strong>
					<button class="btn" type="button" onclick={() => (expandedBio = !expandedBio)}>
						{expandedBio ? 'Collapse' : 'Expand'}
					</button>
				</div>
				{#if expandedBio}
					<p class="muted" style="margin-bottom: 0;">{artistData.artist.bio ?? 'No bio available.'}</p>
				{/if}
			</div>
		</div>
		<div class="panel-soft">
			<div class="muted">Followers</div>
			<div class="kpi">{artistData.artist.followers}</div>
			<div class="muted">Total Streams: {artistData.artist.total_streams}</div>
		</div>
	</div>

	<div style="display: flex; gap: 0.45rem; margin-top: 0.65rem; align-items: end;">
		{#if isFollowing}
			<button class="btn" type="button" onclick={unfollowArtist}>Unfollow artist</button>
		{:else}
			<button class="btn" type="button" onclick={followArtist}>Follow artist</button>
		{/if}
		{#if followMessage}
			<span class="muted">{followMessage}</span>
		{/if}
	</div>
</section>

<section class="grid-cards" style="grid-template-columns: 1.15fr 0.85fr; margin-bottom: 0.75rem;">
	<div class="panel">
		<h2 style="margin-top: 0; font-size: 1rem;">Songs</h2>
		<div style="display: flex; flex-direction: column; gap: 0.55rem;">
			{#each artistData.tracks as track}
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
							<div class="pill">{track.total_streams} streams</div>
						</div>
						<div class="muted">{track.album_title} · {track.duration ?? 0}s</div>
						{#if track.tags}
							<div class="muted">{track.tags}</div>
						{/if}
					</div>
				</button>
			{/each}
		</div>
	</div>

	<div class="panel">
		<h2 style="margin-top: 0; font-size: 1rem;">Upcoming Shows</h2>
		<div style="display: flex; flex-direction: column; gap: 0.55rem;">
			{#each artistData.upcoming_shows as show}
				{#if show.status === 'Cancelled'}
					<div class="panel-soft">
						<div>{show.title}</div>
						<div class="muted">{show.show_date} {show.show_time}</div>
						<div class="muted">{show.venue_name} · {show.venue_city}</div>
						<div class="muted">Booked tickets: {show.booked_tickets}</div>
						<div class="muted">Status: Cancelled</div>
					</div>
				{:else}
					<a class="panel-soft" href={`/artist/${artistData.artist.artist_id}/shows/${show.show_id}/book`}>
						<div>{show.title}</div>
						<div class="muted">{show.show_date} {show.show_time}</div>
						<div class="muted">{show.venue_name} · {show.venue_city}</div>
						<div class="muted">Booked tickets: {show.booked_tickets}</div>
						<div class="muted">Status: {show.status ?? 'Scheduled'}</div>
					</a>
				{/if}
			{/each}
		</div>
	</div>
</section>

<section class="panel" style="margin-bottom: 0.75rem;">
	<h2 style="margin: 0 0 0.55rem; font-size: 1rem;">Albums</h2>
	<div class="grid-cards" style="grid-template-columns: repeat(4, minmax(0, 1fr));">
		{#each artistData.albums as album}
			<a href={`/album/${album.album_id}`} class="panel-soft">
				<img class="cover" src={album.album_cover_url} alt={album.title} />
				<div style="margin-top: 0.45rem;">{album.title}</div>
				<div class="muted">{album.release_date ?? 'unknown'} · {album.tracks_count} tracks</div>
				{#if album.tags}
					<div class="muted">{album.tags}</div>
				{/if}
			</a>
		{/each}
	</div>
</section>

<section class="panel">
	<h2 style="margin: 0 0 0.55rem; font-size: 1rem;">Social Links</h2>
	<div style="display: flex; gap: 0.55rem; flex-wrap: wrap;">
		{#each artistData.social_links as link}
			<a class="pill" href={link.url} target="_blank" rel="noreferrer">{link.platform}</a>
		{/each}
	</div>
</section>
