import { apiGet } from '$lib/api';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, fetch }) => {
	const artistId = Number(params.id);
	const data = await apiGet<{
		artist: {
			artist_id: number;
			stage_name: string;
			first_name: string | null;
			last_name: string | null;
			bio: string | null;
			country: string | null;
			profile_image: string | null;
			profile_image_url: string;
			header_image_url: string;
			verification_status: string;
			followers: number;
			total_streams: number;
			is_following: boolean;
		};
		social_links: { platform: string; url: string }[];
		labels: { label_name: string; contract_start_date: string | null; contract_end_date: string | null }[];
		albums: {
			album_id: number;
			title: string;
			release_date: string | null;
			album_type: string | null;
			cover_image: string | null;
			album_cover_url: string;
			tracks_count: number;
			tags: string | null;
		}[];
		tracks: {
			track_id: number;
			title: string;
			duration: number | null;
			album_title: string;
			cover_image: string | null;
			album_cover_url: string;
			track_cover_url: string;
			audio_url: string;
			total_streams: number;
			tags: string | null;
		}[];
		upcoming_shows: {
			show_id: number;
			title: string;
			show_date: string;
			show_time: string;
			venue_name: string | null;
			venue_city: string | null;
			venue_country: string | null;
			status: string | null;
			booked_tickets: number;
		}[];
	}>(`/api/artists/${artistId}`, fetch);

	return { data };
};
