import { apiGet } from '$lib/api';
import type { PageLoad } from './$types';

type SearchResult = {
	tracks: {
		track_id: number;
		title: string;
		duration: number | null;
		language: string | null;
		album_title: string | null;
		cover_image: string | null;
		album_cover_url: string;
		track_cover_url: string;
		audio_url: string;
		tags: string | null;
		total_streams: number;
	}[];
	albums: {
		album_id: number;
		title: string;
		release_date: string | null;
		language: string | null;
		album_type: string | null;
		cover_image: string | null;
		album_cover_url: string;
		tags: string | null;
		tracks_count: number;
	}[];
};

export const load: PageLoad = async ({ fetch, url }) => {
	const q = url.searchParams.get('q') ?? '';
	const tagId = url.searchParams.get('tag_id') ?? '';
	const tagClause = tagId ? `&tag_id=${encodeURIComponent(tagId)}` : '';

	const [tags, topSongs, results, artists] = await Promise.all([
		apiGet<{ id: number; name: string }[]>('/api/tags', fetch),
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
		),
		apiGet<SearchResult>(`/api/search?q=${encodeURIComponent(q)}${tagClause}`, fetch),
		apiGet<
			{
				artist_id: number;
				stage_name: string;
				country: string | null;
				followers: number;
				total_streams: number;
				profile_image_url: string;
			}[]
		>('/api/artists', fetch)
	]);

	return { q, tagId, tags, topSongs, results, artists };
};
