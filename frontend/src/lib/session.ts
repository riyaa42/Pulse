import { writable } from 'svelte/store';
import { apiGet, getSelectedActor, setSelectedActor } from '$lib/api';

export type ListenerProfile = {
	actor_type: 'listener';
	user_id: number;
	username: string;
	country: string;
	profile_image_url: string;
};

export type ArtistProfile = {
	actor_type: 'artist';
	artist_id: number;
	stage_name: string;
	country: string;
	profile_image_url: string;
};

export type SessionActor = {
	actor_type: 'listener' | 'artist';
	role: 'listener' | 'artist';
	user_id: number | null;
	artist_id: number | null;
	username: string;
	profile_image_url: string;
};

type SessionState = {
	loading: boolean;
	listeners: ListenerProfile[];
	artists: ArtistProfile[];
	current: SessionActor | null;
	playlists: { playlist_id: number; name: string; tracks_count: number }[];
};

const initialState: SessionState = {
	loading: false,
	listeners: [],
	artists: [],
	current: null,
	playlists: []
};

export const session = writable<SessionState>(initialState);

export async function hydrateSession(): Promise<void> {
	session.update((state) => ({ ...state, loading: true }));
	const [options, me] = await Promise.all([
		apiGet<{ listeners: ListenerProfile[]; artists: ArtistProfile[] }>('/api/session/options', fetch),
		apiGet<SessionActor>('/api/me', fetch)
	]);

	let playlists: { playlist_id: number; name: string; tracks_count: number }[] = [];
	if (me.actor_type === 'listener') {
		const library = await apiGet<{ playlists: { playlist_id: number; name: string; tracks_count: number }[] }>(
			'/api/me/library',
			fetch
		);
		playlists = library.playlists;
	}

	const selected = getSelectedActor();
	if (selected.actorType !== me.actor_type || selected.actorId !== (me.actor_type === 'listener' ? me.user_id : me.artist_id)) {
		setSelectedActor(me.actor_type, me.actor_type === 'listener' ? (me.user_id ?? 1) : (me.artist_id ?? 1));
	}

	session.set({
		loading: false,
		listeners: options.listeners,
		artists: options.artists,
		current: me,
		playlists
	});
}

export function switchSessionActor(actorType: 'listener' | 'artist', actorId: number): void {
	setSelectedActor(actorType, actorId);
	window.location.reload();
}
