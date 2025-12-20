// Detect environment
const IS_SERVER = typeof window === 'undefined';
const API_BASE = IS_SERVER ? 'http://localhost:8000' : '';

export async function fetchFromAPI(endpoint: string, options: RequestInit = {}) {
    // Ensure we have a valid absolute URL for server-side fetching
    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE}/api/v1${endpoint}`;

    try {
        const res = await fetch(url, { ...options, cache: 'no-store' }); // Disable cache for real-time data
        if (!res.ok) throw new Error(`API Error: ${res.statusText}`);
        return await res.json();
    } catch (error) {
        console.error(`Fetch Error: ${error} (${url})`);
        return null;
    }
}
