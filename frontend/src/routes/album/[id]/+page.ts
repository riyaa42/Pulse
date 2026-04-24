import { apiGet } from '$lib/api';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, fetch }) => {
	const data = await apiGet<{
		album: {
			album_id: number;
			title: string;
			release_date: string | null;
			language: string | null;
			album_type: string | null;
			cover_image: string | null;
			album_cover_url: string;
			artist_id: number;
			artist_name: string;
			artist_profile_url: string;
			tracks_count: number;
			total_duration: number | null;
			tags: string | null;
		};
		tracks: {
			track_id: number;
			title: string;
			duration: number | null;
			language: string | null;
			release_date: string | null;
			total_streams: number;
			track_cover_url: string;
			audio_url: string;
		}[];
	}>(`/api/albums/${Number(params.id)}`, fetch);

	return { data };
};