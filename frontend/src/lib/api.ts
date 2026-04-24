import { browser } from '$app/environment';

const baseUrl = (import.meta.env.PUBLIC_API_BASE_URL as string | undefined) || 'http://localhost:8000';
export const SESSION_ACTOR_TYPE_KEY = 'pulse_actor_type';
export const SESSION_ACTOR_ID_KEY = 'pulse_actor_id';

function selectedActorType(): 'listener' | 'artist' {
	if (!browser) {
		return 'listener';
	}
	const raw = window.localStorage.getItem(SESSION_ACTOR_TYPE_KEY) ?? 'listener';
	return raw === 'artist' ? 'artist' : 'listener';
}

function selectedActorId(): string {
	if (!browser) {
		return '1';
	}
	const raw = window.localStorage.getItem(SESSION_ACTOR_ID_KEY) ?? '1';
	return /^\d+$/.test(raw) ? raw : '1';
}

function actorHeaders(): HeadersInit {
	return {
		'x-actor-type': selectedActorType(),
		'x-actor-id': selectedActorId()
	};
}

export function setSelectedActor(actorType: 'listener' | 'artist', actorId: number): void {
	if (!browser) {
		return;
	}
	window.localStorage.setItem(SESSION_ACTOR_TYPE_KEY, actorType);
	window.localStorage.setItem(SESSION_ACTOR_ID_KEY, String(actorId));
}

export function getSelectedActor(): { actorType: 'listener' | 'artist'; actorId: number } {
	return { actorType: selectedActorType(), actorId: Number(selectedActorId()) };
}

export async function apiGet<T>(path: string, fetchFn: typeof fetch): Promise<T> {
	const response = await fetchFn(`${baseUrl}${path}`, {
		headers: actorHeaders()
	});
	if (!response.ok) {
		throw new Error(`Request failed: ${response.status}`);
	}
	return (await response.json()) as T;
}

export async function apiPost<T>(path: string, payload: unknown): Promise<T> {
	const response = await fetch(`${baseUrl}${path}`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json', ...actorHeaders() },
		body: JSON.stringify(payload)
	});
	if (!response.ok) {
		const data = (await response.json().catch(() => null)) as { detail?: string } | null;
		throw new Error(data?.detail ?? `Request failed: ${response.status}`);
	}
	return (await response.json()) as T;
}

export async function apiPatch<T>(path: string, payload: unknown): Promise<T> {
	const response = await fetch(`${baseUrl}${path}`, {
		method: 'PATCH',
		headers: { 'Content-Type': 'application/json', ...actorHeaders() },
		body: JSON.stringify(payload)
	});
	if (!response.ok) {
		const data = (await response.json().catch(() => null)) as { detail?: string } | null;
		throw new Error(data?.detail ?? `Request failed: ${response.status}`);
	}
	return (await response.json()) as T;
}

export async function apiDelete<T>(path: string): Promise<T> {
	const response = await fetch(`${baseUrl}${path}`, {
		method: 'DELETE',
		headers: actorHeaders()
	});
	if (!response.ok) {
		const data = (await response.json().catch(() => null)) as { detail?: string } | null;
		throw new Error(data?.detail ?? `Request failed: ${response.status}`);
	}
	return (await response.json()) as T;
}
