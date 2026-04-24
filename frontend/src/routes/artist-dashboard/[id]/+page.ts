import { apiGet } from '$lib/api';
import type { PageLoad } from './$types';

type DashboardResponse = {
	artist: {
		artist_id: number;
		stage_name: string;
		profile_image_url: string;
		followers: number;
		total_streams: number;
		total_royalty_amount: number;
	};
	top_tracks: {
		track_id: number;
		title: string;
		cover_image: string | null;
		album_cover_url: string;
		track_cover_url: string;
		audio_url: string;
		total_streams: number;
		royalty_total: number;
	}[];
	royalties: {
		royalty_id: number;
		track_title: string;
		stream_count: number;
		total_amount: number;
		currency: string;
		payment_status: string;
		period_start: string;
		period_end: string;
	}[];
	labels: {
		label_name: string;
		contract_start_date: string | null;
		contract_end_date: string | null;
		contact_email: string | null;
	}[];
	shows: {
		show_id: number;
		title: string;
		show_date: string;
		show_time: string;
		venue_name: string | null;
		tickets_booked: number;
	}[];
};

export const load: PageLoad = async ({ params, fetch }) => {
	void params.id;
	const dashboard = await apiGet<DashboardResponse>('/api/artist/me/dashboard', fetch);

	return { dashboard };
};
