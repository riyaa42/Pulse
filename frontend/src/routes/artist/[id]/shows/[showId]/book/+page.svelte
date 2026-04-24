<script lang="ts">
	import { apiPost } from '$lib/api';

	let { data } = $props();

	let seatSection = $state('A');
	let seatRow = $state('1');
	let seatNumber = $state('1');
	let seatCategory = $state('Standard');
	let message = $state('');
	const isCancelled = $derived((data.show.status ?? '').toLowerCase() === 'cancelled');
	const priceMap: Record<string, number> = {
		VIP: 1500,
		Standard: 300,
		Economy: 180
	};

	async function submitBooking() {
		message = '';
		if (isCancelled) {
			message = 'This show is cancelled. Ticket booking is closed.';
			return;
		}
		try {
			const response = await apiPost<{ message: string; ticket_id: number }>(
				`/api/shows/${data.show.show_id}/book`,
				{
					seat_section: seatSection,
					seat_row: seatRow,
					seat_number: seatNumber,
					seat_category: seatCategory
				}
			);
			message = `${response.message} (Ticket #${response.ticket_id})`;
		} catch (error) {
			message = error instanceof Error ? error.message : 'Booking failed.';
		}
	}
</script>

<section class="panel" style="margin-bottom: 0.9rem;">
	<div style="display: grid; grid-template-columns: 120px 1fr; gap: 0.7rem; align-items: center;">
		<img class="cover" style="aspect-ratio: 1;" src={data.show.poster_image_url} alt={data.show.title} />
		<div>
			<h1 style="margin: 0; font-size: 1.3rem;">Book Ticket</h1>
			<p class="muted" style="margin-top: 0.45rem;">
				{data.show.title} · {data.show.artist_name} · {data.show.show_date} {data.show.show_time}
			</p>
			<p class="muted" style="margin-top: 0.25rem;">
				{data.show.venue_name}, {data.show.venue_city}, {data.show.venue_country}
			</p>
		</div>
	</div>
	{#if isCancelled}
		<p class="muted" style="margin-top: 0.45rem;">Status: Cancelled</p>
	{/if}
</section>

<section class="panel">
	<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.6rem;">
		<div>
			<label for="seat-section" class="muted">Seat section</label>
			<input id="seat-section" bind:value={seatSection} />
		</div>
		<div>
			<label for="seat-row" class="muted">Seat row</label>
			<input id="seat-row" bind:value={seatRow} />
		</div>
		<div>
			<label for="seat-number" class="muted">Seat number</label>
			<input id="seat-number" bind:value={seatNumber} />
		</div>
		<div>
			<label for="seat-category" class="muted">Seat category</label>
			<select id="seat-category" bind:value={seatCategory}>
				<option value="VIP">VIP</option>
				<option value="Standard">Standard</option>
				<option value="Economy">Economy</option>
			</select>
		</div>
	</div>
	<p class="muted" style="margin-top: 0.5rem;">Ticket price is auto-derived: {seatCategory} = {priceMap[seatCategory]}.</p>
	<div style="margin-top: 0.7rem; display: flex; gap: 0.55rem; align-items: center;">
		<button class="btn" type="button" onclick={submitBooking} disabled={isCancelled}>Confirm booking</button>
		{#if message}
			<span class="muted">{message}</span>
		{/if}
	</div>
</section>
