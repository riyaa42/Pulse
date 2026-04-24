import { apiGet } from '$lib/api';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, fetch }) => {
	const playlistId = Number(params.id);
	const data = await apiGet<{
		playlist: {
			playlist_id: number;
			name: string;
			description: string | null;
			owner_username: string;
			tracks_count: number;
			can_edit: boolean;
		};
		tracks: {
			track_id: number;
			title: string;
			album_title: string | null;
			artist_name: string | null;
			track_cover_url: string;
			audio_url: string;
			total_streams: number;
			added_at: string;
		}[];
	}>(`/api/playlists/${playlistId}`, fetch);
	return { data };
};
