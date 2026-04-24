import { apiGet } from '$lib/api';
import type { PageLoad } from './$types';

type Me = {
	user_id: number | null;
	username: string;
	role: 'listener' | 'artist';
	actor_type: 'listener' | 'artist';
	artist_id: number | null;
};

export const load: PageLoad = async ({ fetch, url }) => {
	const view = url.searchParams.get('view') ?? 'all';
	const me = await apiGet<Me>('/api/me', fetch);

	if (me.actor_type === 'artist') {
		type ArtistDashboard = Record<string, any>;
		type ArtistCatalog = Record<string, any>;
		const [dashboard, catalog, tags] = await Promise.all([
			apiGet<ArtistDashboard>('/api/artist/me/dashboard', fetch),
			apiGet<ArtistCatalog>('/api/artist/me/catalog', fetch),
			apiGet<{ id: number; name: string }[]>('/api/tags', fetch)
		]);
		return { me, view: 'artist', dashboard, catalog, tags };
	}

	type TopSong = Record<string, any>;
	type EventRow = Record<string, any>;
	const [topSongs, events] = await Promise.all([
		apiGet<TopSong[]>('/api/top-songs?limit=30', fetch),
		apiGet<EventRow[]>('/api/events/upcoming', fetch)
	]);

	return { me, view, topSongs, events };
};
