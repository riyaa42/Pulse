import { apiGet } from '$lib/api';
import type { PageLoad } from './$types';

type UserProfileResponse = {
	user: {
		user_id: number;
		first_name: string;
		last_name: string;
		username: string;
		email: string;
		country: string;
		profile_image: string | null;
		profile_image_url: string;
		created_at: string;
		plan_name: string | null;
		subscription_status: string | null;
		followers: number;
		following: number;
		playlists: number;
		total_stream_events: number;
		tickets_booked: number;
	};
	playlists: {
		playlist_id: number;
		name: string;
		description: string | null;
		is_public: number;
		tracks_count: number;
	}[];
	recent_streams: {
		stream_id: number;
		start_time: string;
		end_time: string | null;
		duration: number | null;
		was_completed: number | null;
		track_id: number;
		track_title: string;
		cover_image: string | null;
		album_cover_url: string;
		track_cover_url: string;
		audio_url: string;
	}[];
	is_own_profile: boolean;
	settings: {
		devices: {
			device_id: number;
			device_type: string;
			device_name: string | null;
			last_used: string | null;
		}[];
		notification_preferences: {
			notification_id: number;
			notification_type: string;
		}[];
		subscription: {
			subscription_id: number;
			status: string;
			plan_id: number;
			plan_name: string;
			features: string | null;
			price: number;
			currency: string;
			max_devices: number | null;
		} | null;
		plans: {
			plan_id: number;
			plan_name: string;
			price: number;
			currency: string;
			features: string | null;
			max_devices: number | null;
		}[];
	} | null;
	tickets: {
		ticket_id: number;
		price: number;
		purchase_date: string;
		status: string;
		seat_section: string | null;
		seat_row: string | null;
		seat_number: string | null;
		seat_category: string | null;
		show_id: number;
		show_title: string;
		show_date: string;
		show_time: string;
		artist_id: number;
		artist_name: string;
	}[];
};

export const load: PageLoad = async ({ params, fetch }) => {
	const userId = Number(params.id);
	const [profile, topSongs] = await Promise.all([
		apiGet<UserProfileResponse>(`/api/users/${userId}/profile`, fetch),
		apiGet<{
			track_id: number;
			title: string;
			album_title: string | null;
			total_streams: number;
			album_cover_url: string;
			track_cover_url: string;
			audio_url: string;
		}[]>(
			'/api/top-songs?limit=6',
			fetch
		)
	]);

	return { profile, topSongs };
};
