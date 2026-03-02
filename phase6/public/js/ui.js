/**
 * ui.js — DOM manipulation and rendering module for Dine AI frontend.
 *
 * Handles all visual updates: showing/hiding states, rendering restaurant
 * cards, displaying toasts, etc.
 */

/* ===== Element references ===== */
const UI_ELEMENTS = {
    emptyState: () => document.getElementById("emptyState"),
    loadingState: () => document.getElementById("loadingState"),
    errorState: () => document.getElementById("errorState"),
    errorMessage: () => document.getElementById("errorMessage"),
    llmSummary: () => document.getElementById("llmSummary"),
    llmSummaryText: () => document.getElementById("llmSummaryText"),
    resultsMeta: () => document.getElementById("resultsMeta"),
    resultsCount: () => document.getElementById("resultsCount"),
    cardsGrid: () => document.getElementById("cardsGrid"),
    noResults: () => document.getElementById("noResults"),
    toast: () => document.getElementById("toast"),
    toastIcon: () => document.getElementById("toastIcon"),
    toastMessage: () => document.getElementById("toastMessage"),
    submitBtn: () => document.getElementById("submitBtn"),
};

/**
 * Hide all result-area states.
 */
function hideAllStates() {
    const ids = ["emptyState", "loadingState", "errorState", "llmSummary", "resultsMeta", "noResults"];
    ids.forEach((id) => {
        const el = document.getElementById(id);
        if (el) el.classList.add("hidden");
    });
    const grid = UI_ELEMENTS.cardsGrid();
    if (grid) grid.innerHTML = "";
}

/**
 * Show the loading spinner state.
 */
function showLoading() {
    hideAllStates();
    UI_ELEMENTS.loadingState().classList.remove("hidden");
    const btn = UI_ELEMENTS.submitBtn();
    btn.disabled = true;
    btn.querySelector(".btn-primary__text").textContent = "Searching…";
}

/**
 * Reset the submit button to its normal state.
 */
function resetSubmitButton() {
    const btn = UI_ELEMENTS.submitBtn();
    btn.disabled = false;
    btn.querySelector(".btn-primary__text").textContent = "Get Recommendations";
}

/**
 * Show an error message in the results area.
 * @param {string} message
 */
function showError(message) {
    hideAllStates();
    resetSubmitButton();
    UI_ELEMENTS.errorMessage().textContent = message;
    UI_ELEMENTS.errorState().classList.remove("hidden");
}

/**
 * Show the empty "ready to discover" state.
 */
function showEmpty() {
    hideAllStates();
    resetSubmitButton();
    UI_ELEMENTS.emptyState().classList.remove("hidden");
}

/**
 * Show the "no results found" state.
 */
function showNoResults() {
    hideAllStates();
    resetSubmitButton();
    UI_ELEMENTS.noResults().classList.remove("hidden");
}

/**
 * Render restaurant cards and optional LLM summary.
 *
 * @param {Object} data — API response with results, llm_summary, llm_used
 * @param {string|null} userId — current user ID (used for feedback)
 */
function renderResults(data) {
    hideAllStates();
    resetSubmitButton();

    const { results, llm_summary, llm_used } = data;

    if (!results || results.length === 0) {
        showNoResults();
        return;
    }

    // LLM Summary
    if (llm_used && llm_summary) {
        UI_ELEMENTS.llmSummaryText().textContent = llm_summary;
        UI_ELEMENTS.llmSummary().classList.remove("hidden");
    }

    // Results count
    UI_ELEMENTS.resultsCount().textContent = `${results.length} restaurant${results.length !== 1 ? "s" : ""} found`;
    UI_ELEMENTS.resultsMeta().classList.remove("hidden");

    // Cards
    const grid = UI_ELEMENTS.cardsGrid();
    grid.innerHTML = "";

    results.forEach((restaurant, index) => {
        const card = createRestaurantCard(restaurant, index);
        grid.appendChild(card);
    });
}

/**
 * Create a single restaurant card element.
 *
 * @param {Object} restaurant — { name, location, rating, price, cuisine, reason }
 * @param {number} index — 0-based rank
 * @param {string|null} userId — used for feedback calls
 * @returns {HTMLElement}
 */
function createRestaurantCard(restaurant, index) {
    const card = document.createElement("div");
    card.className = "card";
    card.style.animationDelay = `${index * 0.07}s`;

    const stars = renderStars(restaurant.rating);
    const priceDisplay = formatPrice(restaurant.price);

    card.innerHTML = `
        <span class="card__rank">#${index + 1}</span>
        <h3 class="card__name">${escapeHtml(restaurant.name)}</h3>
        <p class="card__location">📍 ${escapeHtml(restaurant.location)}</p>
        <div class="card__meta">
            <span class="card__badge card__badge--rating">${stars} ${restaurant.rating.toFixed(1)}</span>
            <span class="card__badge card__badge--price">₹ ${priceDisplay}</span>
            <span class="card__badge card__badge--cuisine">${escapeHtml(restaurant.cuisine || "Various")}</span>
        </div>
        <p class="card__reason">${escapeHtml(restaurant.reason)}</p>
        <div class="card__actions">
            <button class="card__action-btn card__action-btn--like" data-name="${escapeAttr(restaurant.name)}" data-liked="true">
                👍 Like
            </button>
            <button class="card__action-btn card__action-btn--dislike" data-name="${escapeAttr(restaurant.name)}" data-liked="false">
                👎 Dislike
            </button>
        </div>
    `;

    // Attach feedback handlers
    const likeBtn = card.querySelector(".card__action-btn--like");
    const dislikeBtn = card.querySelector(".card__action-btn--dislike");

    likeBtn.addEventListener("click", () => handleFeedback(restaurant.name, true, likeBtn, dislikeBtn));
    dislikeBtn.addEventListener("click", () => handleFeedback(restaurant.name, false, dislikeBtn, likeBtn));

    return card;
}

/**
 * Handle feedback button click.
 */
async function handleFeedback(restaurantName, liked, activeBtn, otherBtn) {
    const userId = window.getGoogleUserId ? window.getGoogleUserId() : null;
    if (!userId) {
        showToast("⚠️", "Please sign in with Google to submit feedback");
        return;
    }

    try {
        await window.DineAPI.submitFeedback({
            user_id: userId,
            restaurant_name: restaurantName,
            liked,
        });

        activeBtn.classList.add("active");
        otherBtn.classList.remove("active");
        showToast("✅", `Feedback saved – ${liked ? "liked" : "disliked"} ${restaurantName}`);
    } catch (err) {
        showToast("⚠️", `Feedback failed: ${err.message}`);
    }
}

/**
 * Render star icons for a rating value.
 * @param {number} rating — 0–5
 * @returns {string} star emoji string
 */
function renderStars(rating) {
    const full = Math.floor(rating);
    const half = rating - full >= 0.5 ? 1 : 0;
    const empty = 5 - full - half;
    return "★".repeat(full) + (half ? "½" : "") + "☆".repeat(empty);
}

/**
 * Format a numeric price for display.
 * @param {number} price
 * @returns {string}
 */
function formatPrice(price) {
    if (!price || price === 0) return "N/A";
    return price.toLocaleString("en-IN");
}

/**
 * Show a toast notification.
 * @param {string} icon
 * @param {string} message
 */
let toastTimeout = null;
function showToast(icon, message) {
    const toast = UI_ELEMENTS.toast();
    UI_ELEMENTS.toastIcon().textContent = icon;
    UI_ELEMENTS.toastMessage().textContent = message;
    toast.classList.remove("hidden");

    if (toastTimeout) clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => {
        toast.classList.add("hidden");
    }, 3500);
}

/**
 * Escape HTML to prevent XSS.
 */
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text || "";
    return div.innerHTML;
}

/**
 * Escape for use in HTML attributes.
 */
function escapeAttr(text) {
    return (text || "").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
}

// Expose globally
window.DineUI = {
    showLoading,
    showError,
    showEmpty,
    showNoResults,
    renderResults,
    showToast,
    hideAllStates,
    resetSubmitButton,
};
