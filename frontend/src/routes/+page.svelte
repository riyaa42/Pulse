<script lang="ts">
	import { apiDelete, apiPost } from '$lib/api';
	import { playTrack } from '$lib/player';
	import { session } from '$lib/session';

	let { data } = $props();
	const dashboard = $derived(data.dashboard!);
	const catalog = $derived(data.catalog!);
	let addMessages = $state<Record<number, string>>({});
	let selectedPlaylistId = $state('');
	let newPlaylistName = $state('');
	let newPlaylistDescription = $state('');
	let playlistCreateMessage = $state('');

	let albumForm = $state({ title: '', release_date: '', language: '', album_type: 'Studio Album', cover_image: '' });
	let trackForm = $state({ title: '', duration: 180, language: 'English', release_date: '', bpm: 100, album_id: '', tag_names: '' });
	let showForm = $state({
		title: '',
		description: '',
		show_date: '',
		show_time: '',
		venue_name: '',
		venue_city: '',
		venue_country: '',
		status: 'Scheduled'
	});
	let artistActionMessage = $state('');
	let albumTagInputs = $state<Record<number, string>>({});
	let creditForm = $state({ track_id: '', person_name: '', role: '' });

	function parseTagNames(raw: string): string[] {
		return raw
			.split(',')
			.map((value) => value.trim())
			.filter((value, index, all) => value.length > 0 && all.findIndex((item) => item.toLowerCase() === value.toLowerCase()) === index);
	}

	function play(song: any) {
		playTrack({
			track_id: song.track_id,
			title: song.title,
			album_title: song.album_title,
			track_cover_url: song.track_cover_url,
			audio_url: song.audio_url
		});
	}

	async function addToPlaylist(trackId: number) {
		if (!selectedPlaylistId) {
			addMessages[trackId] = 'Pick a playlist first.';
			return;
		}
		const playlistId = Number(selectedPlaylistId);
		try {
			await apiPost(`/api/playlists/${playlistId}/tracks`, { track_id: trackId });
			addMessages[trackId] = 'Added to playlist.';
		} catch (error) {
			addMessages[trackId] = error instanceof Error ? error.message : 'Could not add track.';
		}
	}

	async function createPlaylist() {
		playlistCreateMessage = '';
		if (!newPlaylistName.trim()) {
			playlistCreateMessage = 'Playlist name is required.';
			return;
		}
		try {
			await apiPost('/api/playlists', {
				name: newPlaylistName,
				description: newPlaylistDescription || null,
				is_public: true,
				is_collaborative: false
			});
			window.location.reload();
		} catch (error) {
			playlistCreateMessage = error instanceof Error ? error.message : 'Could not create playlist.';
		}
	}

	async function createAlbum() {
		artistActionMessage = '';
		try {
			await apiPost('/api/artist/me/albums', {
				title: albumForm.title,
				release_date: albumForm.release_date || null,
				language: albumForm.language || null,
				album_type: albumForm.album_type || null,
				cover_image: albumForm.cover_image || null
			});
			artistActionMessage = 'Album created.';
			window.location.reload();
		} catch (error) {
			artistActionMessage = error instanceof Error ? error.message : 'Album create failed.';
		}
	}

	async function createTrack() {
		artistActionMessage = '';
		try {
			await apiPost('/api/artist/me/tracks', {
				title: trackForm.title,
				duration: Number(trackForm.duration) || null,
				language: trackForm.language || null,
				release_date: trackForm.release_date || null,
				bpm: Number(trackForm.bpm) || null,
				album_id: trackForm.album_id ? Number(trackForm.album_id) : null,
				tag_names: parseTagNames(trackForm.tag_names)
			});
			artistActionMessage = 'Track created.';
			window.location.reload();
		} catch (error) {
			artistActionMessage = error instanceof Error ? error.message : 'Track create failed.';
		}
	}

	async function createShow() {
		artistActionMessage = '';
		try {
			await apiPost('/api/artist/me/shows', showForm);
			artistActionMessage = 'Show created.';
			window.location.reload();
		} catch (error) {
			artistActionMessage = error instanceof Error ? error.message : 'Show create failed.';
		}
	}

	async function setAlbumTags(albumId: number) {
		artistActionMessage = '';
		try {
			const raw = albumTagInputs[albumId] ?? '';
			await apiPost(`/api/artist/me/albums/${albumId}/tags`, {
				tag_names: parseTagNames(raw)
			});
			artistActionMessage = 'Album tags updated.';
		} catch (error) {
			artistActionMessage = error instanceof Error ? error.message : 'Could not update album tags.';
		}
	}

	async function cancelShow(showId: number) {
		artistActionMessage = '';
		try {
			await apiDelete(`/api/artist/me/shows/${showId}`);
			artistActionMessage = 'Show cancelled.';
			window.location.reload();
		} catch (error) {
			artistActionMessage = error instanceof Error ? error.message : 'Could not cancel show.';
		}
	}

	async function addCredit() {
		artistActionMessage = '';
		if (!creditForm.track_id || !creditForm.person_name || !creditForm.role) {
			artistActionMessage = 'Track ID, person name and role are required for credits.';
			return;
		}
		try {
			await apiPost(`/api/artist/me/tracks/${Number(creditForm.track_id)}/credits`, {
				person_name: creditForm.person_name,
				role: creditForm.role,
				entity_type: 'Track'
			});
			artistActionMessage = 'Track credit added.';
			creditForm = { track_id: '', person_name: '', role: '' };
		} catch (error) {
			artistActionMessage = error instanceof Error ? error.message : 'Could not add credit.';
		}
	}
</script>

{#if data.me.actor_type === 'artist'}
	<section class="panel" style="margin-bottom: 0.75rem;">
		<h1 style="margin: 0; font-size: 1.4rem;">Artist Studio</h1>
		<div class="muted" style="margin-top: 0.2rem;">Your stats, royalties, catalog, and release controls.</div>
		<div class="grid-cards" style="margin-top: 0.75rem;">
			<div class="panel-soft"><div class="muted">Followers</div><div class="kpi">{dashboard.artist.followers}</div></div>
			<div class="panel-soft"><div class="muted">Total Streams</div><div class="kpi">{dashboard.artist.total_streams}</div></div>
			<div class="panel-soft"><div class="muted">Total Royalty</div><div class="kpi">{dashboard.artist.total_royalty_amount}</div></div>
		</div>
	</section>

	<section class="grid-cards" style="margin-bottom: 0.75rem; grid-template-columns: 1fr 1fr;">
		<div class="panel">
			<h2 style="margin-top: 0; font-size: 1rem;">My Albums</h2>
			{#each catalog.albums as album}
				<div class="panel-soft" style="margin-bottom: 0.45rem;">
					<div>{album.title}</div>
					<div class="muted">{album.release_date ?? 'unknown'} · {album.tracks_count} tracks</div>
					<div style="display: flex; gap: 0.35rem; margin-top: 0.35rem;">
						<input
							placeholder="Tags (e.g. Pop, Romantic)"
							list="tag-suggestions"
							value={albumTagInputs[album.album_id] ?? ''}
							oninput={(event) => {
								const target = event.currentTarget as HTMLInputElement;
								albumTagInputs = { ...albumTagInputs, [album.album_id]: target.value };
							}}
						/>
						<button class="btn" type="button" onclick={() => setAlbumTags(album.album_id)}>Update tags</button>
					</div>
					<div class="muted" style="margin-top: 0.25rem;">Use comma-separated tag words, not IDs.</div>
				</div>
			{/each}
		</div>
		<div class="panel">
			<h2 style="margin-top: 0; font-size: 1rem;">My Shows</h2>
			{#each catalog.shows as show}
				<div class="panel-soft" style="margin-bottom: 0.45rem;">
					<div>{show.title}</div>
					<div class="muted">{show.show_date} {show.show_time} · {show.venue_name}</div>
					<div class="muted">Booked tickets: {show.booked_tickets} · Status: {show.status ?? 'Scheduled'}</div>
					{#if show.status !== 'Cancelled'}
						<button class="btn" type="button" style="margin-top: 0.35rem;" onclick={() => cancelShow(show.show_id)}>
							Cancel show
						</button>
					{/if}
				</div>
			{/each}
		</div>
	</section>

	<section class="panel" style="margin-bottom: 0.75rem;">
		<h2 style="margin-top: 0; font-size: 1rem;">Label Contracts & Royalty Rates</h2>
		{#if dashboard.active_label}
			<div class="panel-soft" style="margin-bottom: 0.55rem;">
				<div><strong>Current label:</strong> {dashboard.active_label.label_name}</div>
				<div class="muted">
					Rate: {dashboard.active_label.avg_royalty_rate ?? dashboard.royalty_overview?.avg_royalty_rate ?? 0}
					· Contract: {dashboard.active_label.contract_start_date ?? 'N/A'} to {dashboard.active_label.contract_end_date ?? 'Present'}
				</div>
			</div>
		{:else}
			<div class="panel-soft" style="margin-bottom: 0.55rem;">
				<div><strong>Current label:</strong> Independent</div>
				<div class="muted">Average royalty rate: {dashboard.royalty_overview?.avg_royalty_rate ?? 0}</div>
			</div>
		{/if}

		<div style="display: flex; flex-direction: column; gap: 0.45rem;">
			{#if dashboard.labels.length === 0}
				<div class="muted">No label contracts found for this artist.</div>
			{:else}
				{#each dashboard.labels as label}
					<div class="panel-soft">
						<div style="display: flex; justify-content: space-between; gap: 0.5rem; align-items: center;">
							<div>{label.label_name}</div>
							<div class="pill">{label.is_active ? 'Active' : 'Past'}</div>
						</div>
						<div class="muted">
							Rate: {label.avg_royalty_rate ?? 0} · Royalty total: {label.total_royalty_amount ?? 0}
						</div>
						<div class="muted">
							Contract: {label.contract_start_date ?? 'N/A'} to {label.contract_end_date ?? 'Present'} · {label.country}
						</div>
						<div class="muted">Contact: {label.contact_email ?? 'N/A'}</div>
					</div>
				{/each}
			{/if}
		</div>
	</section>

	<section class="grid-cards" style="grid-template-columns: 1fr 1fr 1fr;">
		<div class="panel">
			<h2 style="margin-top: 0; font-size: 1rem;">Add Album</h2>
			<div class="muted" style="margin-bottom: 0.2rem;">Album title (required)</div>
			<input placeholder="e.g. Midnight Echoes" bind:value={albumForm.title} style="margin-bottom: 0.4rem;" />
			<div class="muted" style="margin-bottom: 0.2rem;">Release date</div>
			<input type="date" bind:value={albumForm.release_date} style="margin-bottom: 0.4rem;" />
			<div class="muted" style="margin-bottom: 0.2rem;">Primary language</div>
			<input placeholder="e.g. English" bind:value={albumForm.language} style="margin-bottom: 0.4rem;" />
			<div class="muted" style="margin-bottom: 0.2rem;">Album type</div>
			<input placeholder="e.g. Studio Album" bind:value={albumForm.album_type} style="margin-bottom: 0.4rem;" />
			<div class="muted" style="margin-bottom: 0.2rem;">Cover filename (optional)</div>
			<input placeholder="e.g. album_12.jpg" bind:value={albumForm.cover_image} style="margin-bottom: 0.4rem;" />
			<button class="btn" type="button" onclick={createAlbum}>Create album</button>
		</div>

		<div class="panel">
			<h2 style="margin-top: 0; font-size: 1rem;">Add Track</h2>
			<div class="muted" style="margin-bottom: 0.2rem;">Track title (required)</div>
			<input placeholder="e.g. Neon Nights" bind:value={trackForm.title} style="margin-bottom: 0.4rem;" />
			<div class="muted" style="margin-bottom: 0.2rem;">Duration in seconds</div>
			<input type="number" placeholder="e.g. 210" bind:value={trackForm.duration} style="margin-bottom: 0.4rem;" />
			<div class="muted" style="margin-bottom: 0.2rem;">Language</div>
			<input placeholder="e.g. English" bind:value={trackForm.language} style="margin-bottom: 0.4rem;" />
			<div class="muted" style="margin-bottom: 0.2rem;">Release date</div>
			<input type="date" bind:value={trackForm.release_date} style="margin-bottom: 0.4rem;" />
			<div class="muted" style="margin-bottom: 0.2rem;">BPM</div>
			<input type="number" placeholder="e.g. 120" bind:value={trackForm.bpm} style="margin-bottom: 0.4rem;" />
			<div class="muted" style="margin-bottom: 0.2rem;">Album ID (optional, from My Albums)</div>
			<input placeholder="e.g. 5 (leave blank for single)" bind:value={trackForm.album_id} style="margin-bottom: 0.4rem;" />
			<div class="muted" style="margin-bottom: 0.2rem;">Tags (comma-separated words)</div>
			<input list="tag-suggestions" placeholder="e.g. Pop, Party" bind:value={trackForm.tag_names} style="margin-bottom: 0.4rem;" />
			<button class="btn" type="button" onclick={createTrack}>Create track</button>
			<div class="muted" style="margin-top: 0.4rem;">After creation, add credits below (singer/composer/etc).</div>
			<div style="display: grid; gap: 0.35rem; margin-top: 0.35rem;">
				<input placeholder="Track ID to credit" bind:value={creditForm.track_id} />
				<input placeholder="Contributor name" bind:value={creditForm.person_name} />
				<input placeholder="Role (Singer/Composer/Lyricist/etc)" bind:value={creditForm.role} />
				<button class="btn" type="button" onclick={addCredit}>Add credit</button>
			</div>
		</div>

		<div class="panel">
			<h2 style="margin-top: 0; font-size: 1rem;">Add Show</h2>
			<div class="muted" style="margin-bottom: 0.2rem;">Show title</div>
			<input placeholder="e.g. Pulse Arena Night" bind:value={showForm.title} style="margin-bottom: 0.4rem;" />
			<div class="muted" style="margin-bottom: 0.2rem;">Description</div>
			<input placeholder="What is this show about?" bind:value={showForm.description} style="margin-bottom: 0.4rem;" />
			<div class="muted" style="margin-bottom: 0.2rem;">Show date</div>
			<input type="date" bind:value={showForm.show_date} style="margin-bottom: 0.4rem;" />
			<div class="muted" style="margin-bottom: 0.2rem;">Show time</div>
			<input type="time" bind:value={showForm.show_time} style="margin-bottom: 0.4rem;" />
			<div class="muted" style="margin-bottom: 0.2rem;">Venue name</div>
			<input placeholder="e.g. NSCI Dome" bind:value={showForm.venue_name} style="margin-bottom: 0.4rem;" />
			<div class="muted" style="margin-bottom: 0.2rem;">Venue city</div>
			<input placeholder="e.g. Mumbai" bind:value={showForm.venue_city} style="margin-bottom: 0.4rem;" />
			<div class="muted" style="margin-bottom: 0.2rem;">Venue country</div>
			<input placeholder="e.g. India" bind:value={showForm.venue_country} style="margin-bottom: 0.4rem;" />
			<button class="btn" type="button" onclick={createShow}>Create show</button>
		</div>
	</section>

	<datalist id="tag-suggestions">
		{#each data.tags ?? [] as tag}
			<option value={tag.name}></option>
		{/each}
	</datalist>

	{#if artistActionMessage}
		<p class="muted">{artistActionMessage}</p>
	{/if}
{:else}
	<section class="panel" style="margin-bottom: 0.75rem;">
		<div style="display: flex; gap: 0.45rem; margin-bottom: 0.75rem;">
			<a class="pill" href="/?view=all">All</a>
			<a class="pill" href="/?view=music">Music</a>
			<a class="pill" href="/?view=events">Events</a>
		</div>
		<h1 class="pulse-logo">pulse</h1>
		<div class="muted" style="margin-top: 0.3rem;">Stream tracks, manage playlists, and book shows.</div>
	</section>

	{#if $session.playlists.length > 0}
		<section class="panel" style="margin-bottom: 0.75rem;">
			<div class="muted" style="margin-bottom: 0.35rem;">Quick add destination</div>
			<select bind:value={selectedPlaylistId}>
				<option value="">Select playlist</option>
				{#each $session.playlists as playlist}
					<option value={playlist.playlist_id}>{playlist.name}</option>
				{/each}
			</select>
		</section>
	{/if}

	<section class="panel" style="margin-bottom: 0.75rem;">
		<h2 style="margin-top: 0; font-size: 1rem;">Create Playlist</h2>
		<input placeholder="Playlist name" bind:value={newPlaylistName} style="margin-bottom: 0.4rem;" />
		<input placeholder="Description" bind:value={newPlaylistDescription} style="margin-bottom: 0.4rem;" />
		<button class="btn" type="button" onclick={createPlaylist}>Create</button>
		{#if playlistCreateMessage}
			<div class="muted" style="margin-top: 0.35rem;">{playlistCreateMessage}</div>
		{/if}
	</section>

	{#if data.view !== 'events'}
		<section class="panel" style="margin-bottom: 0.75rem;">
			<h2 style="margin-top: 0; font-size: 1rem;">Songs</h2>
			<div class="grid-cards" style="grid-template-columns: repeat(2, minmax(0, 1fr));">
				{#each data.topSongs as song}
					<div class="panel-soft">
						<button type="button" onclick={() => play(song)} style="display: flex; width: 100%; gap: 0.6rem; text-align: left;">
							<img class="cover-row" src={song.track_cover_url} alt={song.title} />
							<div>
								<div>{song.title}</div>
								<div class="muted">
									<a href={song.artist_id ? `/artist/${song.artist_id}` : '#'}>{song.artist_name ?? 'Unknown'}</a> · {song.total_streams} streams
								</div>
							</div>
						</button>
						{#if selectedPlaylistId}
							<button class="btn" type="button" style="margin-top: 0.45rem;" onclick={() => addToPlaylist(song.track_id)}>
								Add to playlist
							</button>
							{#if addMessages[song.track_id]}
								<div class="muted" style="margin-top: 0.2rem;">{addMessages[song.track_id]}</div>
							{/if}
						{/if}
					</div>
				{/each}
			</div>
		</section>
	{/if}

	{#if data.view !== 'music'}
		<section class="panel">
			<div style="display: flex; justify-content: space-between; align-items: center;">
				<h2 style="margin: 0; font-size: 1rem;">Upcoming Events</h2>
				<a href="/search" class="muted">show all</a>
			</div>
			<div style="display: flex; flex-direction: column; gap: 0.55rem; margin-top: 0.6rem;">
				{#each data.events as show}
					{#if show.status === 'Cancelled'}
						<div class="panel-soft">
							<div>{show.title}</div>
							<div class="muted">{show.artist_name} · {show.show_date} {show.show_time}</div>
							<div class="muted">{show.venue_name}, {show.venue_city} · booked {show.booked_tickets}</div>
							<div class="muted">Status: Cancelled</div>
						</div>
					{:else}
						<a class="panel-soft" href={`/artist/${show.artist_id}/shows/${show.show_id}/book`}>
							<div>{show.title}</div>
							<div class="muted">{show.artist_name} · {show.show_date} {show.show_time}</div>
							<div class="muted">{show.venue_name}, {show.venue_city} · booked {show.booked_tickets}</div>
							<div class="muted">Status: {show.status ?? 'Scheduled'}</div>
						</a>
					{/if}
				{/each}
			</div>
		</section>
	{/if}
{/if}
