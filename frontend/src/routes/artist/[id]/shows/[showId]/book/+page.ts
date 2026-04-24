import { apiGet } from '$lib/api';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ params, fetch }) => {
	const showId = Number(params.showId);
	const show = await apiGet<{
		show_id: number;
		title: string;
		description: string | null;
		show_date: string;
		show_time: string;
		venue_name: string | null;
		venue_city: string | null;
		venue_country: string | null;
		status: string | null;
		artist_id: number;
		artist_name: string;
		booked_tickets: number;
		poster_image_url: string;
	}>(`/api/shows/${showId}`, fetch);

	return { show };
};
