import { writable } from 'svelte/store';

export type PlayerTrack = {
	track_id: number;
	title: string;
	artist?: string;
	album_title?: string | null;
	track_cover_url?: string;
	audio_url?: string;
};

export const currentTrack = writable<PlayerTrack | null>(null);
export const isPlaying = writable(false);
export const currentTime = writable(0);
export const duration = writable(0);

export function playTrack(track: PlayerTrack): void {
	currentTrack.set(track);
	isPlaying.set(true);
	currentTime.set(0);
}
