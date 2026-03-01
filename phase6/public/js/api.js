/**
 * api.js — API communication module for Dine AI frontend.
 *
 * All fetch calls to the Phase 4 backend are encapsulated here. Other modules
 * import functions from this file so that URL and error handling logic stays
 * in one place.
 */

const API_BASE_URL = window.location.hostname === "localhost" && window.location.port !== "8004" ? "http://localhost:8004" : "";

/**
 * Fetch application configuration (like Google Client ID) from the backend.
 *
 * @returns {Promise<Object>} JSON response containing configuration variables.
 */
async function fetchConfig() {
    const response = await fetch(`${API_BASE_URL}/api/config`, {
        method: "GET",
    });

    if (!response.ok) {
        throw new Error(`Failed to fetch config (${response.status})`);
    }

    return response.json();
}

/**
 * Fetch restaurant recommendations from the backend.
 *
 * @param {Object} params
 * @param {string} params.location      – City or area (required)
 * @param {string} params.price_range   – "low" | "mid" | "high"
 * @param {number} params.min_rating    – 0–5
 * @param {string|null} params.cuisine  – Cuisine filter or null
 * @param {string|null} params.user_id  – Optional user identifier
 *
 * @returns {Promise<Object>} Parsed JSON response containing results, llm_summary, llm_used
 * @throws {Error} On network or HTTP errors
 */
async function fetchRecommendations({ location, price_range, min_rating, cuisine, user_id }) {
    const body = {
        location,
        price_range,
        min_rating,
    };

    if (cuisine) body.cuisine = cuisine;
    if (user_id) body.user_id = user_id;

    const response = await fetch(`${API_BASE_URL}/api/recommendations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        const detail = errorData?.detail || `Server error (${response.status})`;
        throw new Error(detail);
    }

    return response.json();
}

/**
 * Submit user feedback (like/dislike) for a restaurant.
 *
 * @param {Object} params
 * @param {string} params.user_id           – User identifier
 * @param {string} params.restaurant_name   – Name of the restaurant
 * @param {boolean} params.liked            – true for like, false for dislike
 *
 * @returns {Promise<Object>} Parsed JSON response
 * @throws {Error} On network or HTTP errors
 */
async function submitFeedback({ user_id, restaurant_name, liked }) {
    const response = await fetch(`${API_BASE_URL}/api/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id, restaurant_name, liked }),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        const detail = errorData?.detail || `Feedback error (${response.status})`;
        throw new Error(detail);
    }

    return response.json();
}

/**
 * Check if the backend is reachable.
 *
 * @returns {Promise<boolean>} true if /health returns ok
 */
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (!response.ok) return false;
        const data = await response.json();
        return data.status === "ok";
    } catch {
        return false;
    }
}

// Make functions available globally (they'll be used by app.js)
window.DineAPI = {
    fetchRecommendations,
    submitFeedback,
    checkHealth,
    fetchConfig,
    API_BASE_URL,
};
