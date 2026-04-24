<script lang="ts">
	let { data } = $props();
	const dashboard = $derived(data.dashboard);
</script>

<section class="panel" style="margin-bottom: 0.9rem;">
	<div style="display: flex; gap: 0.6rem; align-items: center; margin-bottom: 0.25rem;">
		<img class="cover-row" src={dashboard.artist.profile_image_url} alt={dashboard.artist.stage_name} />
		<h1 style="margin: 0; font-size: 1.3rem;">Artist Dashboard · {dashboard.artist.stage_name}</h1>
	</div>
	<div class="grid-cards" style="margin-top: 0.75rem;">
		<div class="panel-soft">
			<div class="muted">Followers</div>
			<div class="kpi">{dashboard.artist.followers}</div>
		</div>
		<div class="panel-soft">
			<div class="muted">Total Streams</div>
			<div class="kpi">{dashboard.artist.total_streams}</div>
		</div>
		<div class="panel-soft">
			<div class="muted">Total Royalty</div>
			<div class="kpi">{dashboard.artist.total_royalty_amount}</div>
		</div>
	</div>
</section>

<section class="grid-cards" style="margin-bottom: 0.9rem;">
	<div class="panel">
		<h2 style="margin-top: 0; font-size: 1.05rem;">Top Tracks</h2>
		<table>
			<thead>
				<tr>
					<th>Art</th>
					<th>Track</th>
					<th>Streams</th>
					<th>Royalty</th>
				</tr>
			</thead>
			<tbody>
				{#each dashboard.top_tracks as track}
					<tr>
						<td><img class="cover-row" src={track.track_cover_url} alt={track.title} /></td>
						<td>{track.title}</td>
						<td>{track.total_streams}</td>
						<td>{track.royalty_total}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	<div class="panel">
		<h2 style="margin-top: 0; font-size: 1.05rem;">Label Contracts</h2>
		<div style="display: flex; flex-direction: column; gap: 0.55rem;">
			{#if dashboard.labels.length === 0}
				<div class="muted">No label contracts found.</div>
			{:else}
				{#each dashboard.labels as label}
					<div class="panel-soft">
						<div>{label.label_name}</div>
						<div class="muted">{label.contract_start_date} to {label.contract_end_date ?? 'ongoing'}</div>
						<div class="muted">{label.contact_email ?? 'No contact email'}</div>
					</div>
				{/each}
			{/if}
		</div>
	</div>
</section>

<section class="grid-cards">
	<div class="panel">
		<h2 style="margin-top: 0; font-size: 1.05rem;">Royalty Periods</h2>
		<table>
			<thead>
				<tr>
					<th>Track</th>
					<th>Streams</th>
					<th>Amount</th>
					<th>Status</th>
				</tr>
			</thead>
			<tbody>
				{#each dashboard.royalties as royalty}
					<tr>
						<td>{royalty.track_title}</td>
						<td>{royalty.stream_count}</td>
						<td>{royalty.total_amount} {royalty.currency}</td>
						<td>{royalty.payment_status}</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>

	<div class="panel">
		<h2 style="margin-top: 0; font-size: 1.05rem;">Upcoming Shows</h2>
		<div style="display: flex; flex-direction: column; gap: 0.55rem;">
			{#each dashboard.shows as show}
				<div class="panel-soft">
					<div>{show.title}</div>
					<div class="muted">{show.show_date} {show.show_time} · {show.venue_name}</div>
					<div class="muted">Booked tickets: {show.tickets_booked}</div>
				</div>
			{/each}
		</div>
	</div>
</section>
