<script lang="ts">
	import { apiDelete, apiPost } from '$lib/api';

	let { data } = $props();
	const user = $derived(data.profile.user);
	const initialPlanId = $derived(String(data.profile.settings?.subscription?.plan_id ?? ''));
	let selectedPlanId = $state('');
	let profileMessage = $state('');
	let deviceType = $state('Desktop');
	let deviceName = $state('');

	const notificationTypes = ['New Releases', 'Show Reminders', 'Playlist Updates', 'Marketing'];

	$effect(() => {
		if (!selectedPlanId) {
			selectedPlanId = initialPlanId;
		}
	});

	function hasNotificationType(type: string): boolean {
		return Boolean(data.profile.settings?.notification_preferences.some((item: any) => item.notification_type === type));
	}

	async function updateSubscription() {
		if (!selectedPlanId) {
			return;
		}
		profileMessage = '';
		try {
			const response = await apiPost<{ plan: { plan_name: string; features: string | null; price: number; currency: string } }>(
				'/api/me/subscription',
				{ plan_id: Number(selectedPlanId) }
			);
			profileMessage = 'Subscription updated.';
			window.alert(
				`Current plan: ${response.plan.plan_name}\nPrice: ${response.plan.price} ${response.plan.currency}\nFeatures: ${response.plan.features ?? 'N/A'}`
			);
			window.location.reload();
		} catch (error) {
			profileMessage = error instanceof Error ? error.message : 'Could not update subscription.';
		}
	}

	async function addDevice() {
		profileMessage = '';
		try {
			await apiPost('/api/me/devices', {
				device_type: deviceType,
				device_name: deviceName || null
			});
			window.location.reload();
		} catch (error) {
			profileMessage = error instanceof Error ? error.message : 'Could not link device.';
		}
	}

	async function removeDevice(deviceId: number) {
		profileMessage = '';
		try {
			await apiDelete(`/api/me/devices/${deviceId}`);
			window.location.reload();
		} catch (error) {
			profileMessage = error instanceof Error ? error.message : 'Could not remove device.';
		}
	}

	async function toggleNotification(type: string, enabled: boolean) {
		profileMessage = '';
		try {
			await apiPost('/api/me/notification-preferences', {
				notification_type: type,
				enabled
			});
			window.location.reload();
		} catch (error) {
			profileMessage = error instanceof Error ? error.message : 'Could not update notifications.';
		}
	}

	async function cancelTicket(ticketId: number) {
		profileMessage = '';
		try {
			await apiPost(`/api/tickets/${ticketId}/cancel`, {});
			window.location.reload();
		} catch (error) {
			profileMessage = error instanceof Error ? error.message : 'Could not cancel ticket.';
		}
	}
</script>

<section class="panel" style="margin-bottom: 0.9rem;">
	<div style="display: flex; gap: 0.65rem; align-items: center; margin-bottom: 0.35rem;">
		<img class="cover-row" src={user.profile_image_url} alt={user.username} />
		<div>
			<h1 style="margin: 0; font-size: 1.3rem;">@{user.username}</h1>
			<div class="muted" style="margin-top: 0.2rem;">{user.first_name} {user.last_name} · {user.country}</div>
		</div>
	</div>
	<div class="grid-cards" style="margin-top: 0.75rem;">
		<div class="panel-soft"><div class="muted">Followers</div><div class="kpi">{user.followers}</div></div>
		<div class="panel-soft"><div class="muted">Following</div><div class="kpi">{user.following}</div></div>
		<div class="panel-soft"><div class="muted">Total Streams</div><div class="kpi">{user.total_stream_events}</div></div>
		<div class="panel-soft"><div class="muted">Plan</div><div class="kpi" style="font-size: 1rem;">{user.plan_name ?? 'Free / None'}</div></div>
		<div class="panel-soft"><div class="muted">Tickets booked</div><div class="kpi">{user.tickets_booked}</div></div>
	</div>
</section>

<section class="grid-cards" style="margin-bottom: 0.9rem;">
	<div class="panel">
		<h2 style="margin-top: 0; font-size: 1.05rem;">Playlists</h2>
		<div style="display: flex; flex-direction: column; gap: 0.55rem;">
			{#if data.profile.playlists.length === 0}
				<div class="muted">No playlists yet.</div>
			{:else}
				{#each data.profile.playlists as playlist}
					<a class="panel-soft" href={`/playlist/${playlist.playlist_id}`}>
						<div>{playlist.name}</div>
						<div class="muted">{playlist.tracks_count} tracks · {playlist.is_public ? 'Public' : 'Private'}</div>
					</a>
				{/each}
			{/if}
		</div>
	</div>

	<div class="panel">
		<h2 style="margin-top: 0; font-size: 1.05rem;">Recent Streams</h2>
		<div style="display: flex; flex-direction: column; gap: 0.55rem;">
			{#each data.profile.recent_streams as stream}
				<div class="panel-soft" style="display: flex; gap: 0.55rem; align-items: center;">
					<img class="cover-row" src={stream.track_cover_url} alt={stream.track_title} />
					<div>
						<div>{stream.track_title}</div>
						<div class="muted">{stream.start_time} · {stream.duration ?? 0}s</div>
					</div>
				</div>
			{/each}
		</div>
	</div>
</section>

{#if data.profile.is_own_profile}
	<section class="grid-cards" style="margin-bottom: 0.9rem; grid-template-columns: 1fr 1fr;">
		<div class="panel">
			<h2 style="margin-top: 0; font-size: 1.05rem;">Subscription</h2>
			<select bind:value={selectedPlanId} style="margin-bottom: 0.45rem;">
				{#each data.profile.settings?.plans ?? [] as plan}
					<option value={plan.plan_id}>{plan.plan_name} · {plan.price} {plan.currency}</option>
				{/each}
			</select>
			<button class="btn" type="button" onclick={updateSubscription}>Change Plan</button>
			<div class="muted" style="margin-top: 0.35rem;">Features are pulled directly from `plan.Features`.</div>
		</div>

		<div class="panel">
			<h2 style="margin-top: 0; font-size: 1.05rem;">Notification Preferences</h2>
			<div style="display: flex; flex-direction: column; gap: 0.4rem;">
				{#each notificationTypes as type}
					<div class="panel-soft" style="display: flex; justify-content: space-between; align-items: center;">
						<span>{type}</span>
						<button class="btn" type="button" onclick={() => toggleNotification(type, !hasNotificationType(type))}>
							{hasNotificationType(type) ? 'Disable' : 'Enable'}
						</button>
					</div>
				{/each}
			</div>
		</div>
	</section>

	<section class="grid-cards" style="margin-bottom: 0.9rem; grid-template-columns: 1fr 1fr;">
		<div class="panel">
			<h2 style="margin-top: 0; font-size: 1.05rem;">Linked Devices</h2>
			<div style="display: grid; grid-template-columns: 1fr 1fr auto; gap: 0.4rem; margin-bottom: 0.5rem;">
				<input bind:value={deviceType} placeholder="Device type" />
				<input bind:value={deviceName} placeholder="Device name" />
				<button class="btn" type="button" onclick={addDevice}>Add</button>
			</div>
			<div style="display: flex; flex-direction: column; gap: 0.45rem;">
				{#each data.profile.settings?.devices ?? [] as device}
					<div class="panel-soft" style="display: flex; justify-content: space-between; align-items: center;">
						<div>
							<div>{device.device_type} · {device.device_name ?? 'Unnamed'}</div>
							<div class="muted">Last used: {device.last_used ?? 'N/A'}</div>
						</div>
						<button class="btn" type="button" onclick={() => removeDevice(device.device_id)}>Remove</button>
					</div>
				{/each}
			</div>
		</div>

		<div class="panel">
			<h2 style="margin-top: 0; font-size: 1.05rem;">My Tickets</h2>
			<div style="display: flex; flex-direction: column; gap: 0.45rem; max-height: 280px; overflow: auto;">
				{#each data.profile.tickets as ticket}
					<div class="panel-soft" style="display: flex; justify-content: space-between; gap: 0.5rem; align-items: center;">
						<div>
							<div>{ticket.show_title}</div>
							<div class="muted">{ticket.show_date} {ticket.show_time}</div>
							<div class="muted">Status: {ticket.status}</div>
							<div class="muted">Seat {ticket.seat_section}-{ticket.seat_row}-{ticket.seat_number}</div>
						</div>
						{#if ticket.status !== 'Cancelled'}
							<button class="btn" type="button" onclick={() => cancelTicket(ticket.ticket_id)}>Cancel</button>
						{/if}
					</div>
				{/each}
			</div>
		</div>
	</section>
{/if}

{#if profileMessage}
	<p class="muted">{profileMessage}</p>
{/if}
