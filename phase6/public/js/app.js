/**
 * app.js — Main application logic for Dine AI frontend.
 *
 * Initializes event listeners, handles form submission,
 * manages theme toggling, and coordinates between api.js and ui.js.
 */

document.addEventListener("DOMContentLoaded", () => {
    // ===== Elements =====
    const filtersForm = document.getElementById("filtersForm");
    const locationInput = document.getElementById("locationInput");
    const priceGroup = document.getElementById("priceGroup");
    const ratingSlider = document.getElementById("ratingSlider");
    const ratingValue = document.getElementById("ratingValue");
    const cuisineInput = document.getElementById("cuisineInput");
    const cuisineDropdown = document.getElementById("cuisineDropdown");
    const retryBtn = document.getElementById("retryBtn");
    const collapseBtn = document.getElementById("filtersCollapseBtn");
    const filtersFormEl = document.querySelector(".filters__form");

    // ===== State =====
    let selectedPriceRange = "mid";
    let lastPayload = null;
    let googleUserId = null;

    // ===== GOOGLE SIGN IN =====
    const googleSignInContainer = document.getElementById("googleSignInContainer");
    const userProfile = document.getElementById("userProfile");
    const userAvatar = document.getElementById("userAvatar");
    const userAvatarInitials = document.getElementById("userAvatarInitials");
    const userNameDisplay = document.getElementById("userNameDisplay");
    const userEmailDisplay = document.getElementById("userEmailDisplay");
    const signOutBtn = document.getElementById("signOutBtn");

    function parseJwt(token) {
        var base64Url = token.split('.')[1];
        var base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        var jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function (c) {
            return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        return JSON.parse(jsonPayload);
    }

    function handleCredentialResponse(response) {
        const responsePayload = parseJwt(response.credential);

        // Save the unique database ID mapping
        googleUserId = responsePayload.sub;

        // Update UI
        const rawName = responsePayload.given_name || responsePayload.name || "U";
        userNameDisplay.textContent = rawName;
        userEmailDisplay.textContent = responsePayload.email;

        // Initials fallback logic
        const initials = rawName.split(" ").map(n => n[0]).join("").substring(0, 2).toUpperCase();
        userAvatarInitials.textContent = initials;

        if (responsePayload.picture) {
            userAvatar.src = responsePayload.picture;
            userAvatar.classList.remove("hidden");
            userAvatarInitials.classList.add("hidden");

            // Fallback just in case the URL is broken
            userAvatar.onerror = () => {
                userAvatar.classList.add("hidden");
                userAvatarInitials.classList.remove("hidden");
            };
        } else {
            userAvatar.classList.add("hidden");
            userAvatarInitials.classList.remove("hidden");
        }

        googleSignInContainer.classList.add("hidden");
        userProfile.classList.remove("hidden");
    }

    window.onload = async function () {
        // Fetch config from backend to retrieve Google Client ID
        try {
            const config = await window.DineAPI.fetchConfig();

            if (window.google && config.google_client_id) {
                google.accounts.id.initialize({
                    client_id: config.google_client_id,
                    callback: handleCredentialResponse
                });
                google.accounts.id.renderButton(
                    document.getElementById("googleSignInContainer"),
                    { theme: "outline", size: "large", shape: "pill" }
                );
            } else if (!config.google_client_id) {
                console.warn("Google Client ID not found in backend configuration.");
            }
        } catch (error) {
            console.error("Could not fetch configuration from backend", error);
        }
    };

    signOutBtn.addEventListener("click", () => {
        googleUserId = null;
        googleSignInContainer.classList.remove("hidden");
        userProfile.classList.add("hidden");
        window.DineUI.showToast("ℹ️", "Signed out successfully");
    });

    // ===== LOCATION AUTOCOMPLETE =====
    const availableLocations = [
        "Banashankari",
        "Basavanagudi",
        "Jayanagar",
        "Kumaraswamy Layout",
        "Mysore Road",
        "Rajarajeshwari Nagar",
        "Vijay Nagar"
    ];
    const locationDropdown = document.getElementById("locationDropdown");

    function renderLocationDropdown(query) {
        const q = query.toLowerCase();
        const matches = availableLocations.filter(loc => loc.toLowerCase().includes(q));

        locationDropdown.innerHTML = "";
        if (matches.length > 0) {
            matches.forEach(loc => {
                const li = document.createElement("li");
                li.className = "autocomplete-item";
                li.textContent = loc;
                li.addEventListener("click", () => {
                    // If multiple allowed, we'd append. But instructions say "Typing the location must provide the list of narrowed down recommendations. Typing fully or partially."
                    // The backend accepts comma separated, but for the UI dropdown, selecting ONE replaces the text.
                    locationInput.value = loc;
                    locationDropdown.classList.add("hidden");
                });
                locationDropdown.appendChild(li);
            });
            locationDropdown.classList.remove("hidden");
        } else {
            locationDropdown.classList.add("hidden");
        }
    }

    locationInput.addEventListener("input", (e) => {
        const val = e.target.value.trim();
        if (val.length > 0) {
            renderLocationDropdown(val);
        } else {
            locationDropdown.classList.add("hidden");
        }
    });

    locationInput.addEventListener("focus", () => {
        renderLocationDropdown(locationInput.value.trim());
    });

    // Hide dropdown when clicking outside
    document.addEventListener("click", (e) => {
        if (!locationInput.contains(e.target) && !locationDropdown.contains(e.target)) {
            locationDropdown.classList.add("hidden");
        }
    });

    // ===== PRICE RANGE BUTTONS =====
    priceGroup.addEventListener("click", (e) => {
        const btn = e.target.closest(".btn-group__btn");
        if (!btn) return;

        priceGroup.querySelectorAll(".btn-group__btn").forEach((b) =>
            b.classList.remove("btn-group__btn--active")
        );
        btn.classList.add("btn-group__btn--active");
        selectedPriceRange = btn.dataset.value;
    });

    // ===== RATING SLIDER =====
    ratingSlider.addEventListener("input", () => {
        ratingValue.textContent = parseFloat(ratingSlider.value).toFixed(1);
    });

    // ===== CUISINE AUTOCOMPLETE =====
    const availableCuisines = [
        "North Indian", "South Indian", "Chinese", "Italian",
        "Continental", "Cafe", "Desserts", "Beverages",
        "Street Food", "Bakery", "Fast Food", "Pizza",
        "Burger", "Mughlai", "Biryani"
    ];

    function renderCuisineDropdown(query) {
        const q = query.toLowerCase();
        const matches = availableCuisines.filter(c => c.toLowerCase().includes(q));

        cuisineDropdown.innerHTML = "";
        if (matches.length > 0) {
            matches.forEach(c => {
                const li = document.createElement("li");
                li.className = "autocomplete-item";
                li.textContent = c;
                li.addEventListener("click", () => {
                    cuisineInput.value = c;
                    cuisineDropdown.classList.add("hidden");
                });
                cuisineDropdown.appendChild(li);
            });
            cuisineDropdown.classList.remove("hidden");
        } else {
            cuisineDropdown.classList.add("hidden");
        }
    }

    cuisineInput.addEventListener("input", (e) => {
        const val = e.target.value.trim();
        if (val.length > 0) {
            renderCuisineDropdown(val);
        } else {
            cuisineDropdown.classList.add("hidden");
        }
    });

    cuisineInput.addEventListener("focus", () => {
        renderCuisineDropdown(cuisineInput.value.trim());
    });

    document.addEventListener("click", (e) => {
        if (!cuisineInput.contains(e.target) && !cuisineDropdown.contains(e.target)) {
            cuisineDropdown.classList.add("hidden");
        }
    });

    // ===== FILTERS COLLAPSE (mobile/tablet) =====
    collapseBtn.addEventListener("click", () => {
        collapseBtn.classList.toggle("collapsed");
        filtersFormEl.classList.toggle("collapsed");
    });

    // ===== RETRY BUTTON =====
    retryBtn.addEventListener("click", () => {
        if (lastPayload) {
            performSearch(lastPayload);
        }
    });

    // ===== FORM SUBMISSION =====
    filtersForm.addEventListener("submit", (e) => {
        e.preventDefault();

        const location = locationInput.value.trim();
        const payload = {
            location,
            price_range: selectedPriceRange,
            min_rating: parseFloat(ratingSlider.value),
            cuisine: cuisineInput.value.trim() || null,
            user_id: googleUserId,
        };

        lastPayload = payload;
        performSearch(payload);
    });

    // ===== SEARCH LOGIC =====
    async function performSearch(payload) {
        window.DineUI.showLoading();

        try {
            const data = await window.DineAPI.fetchRecommendations(payload);
            window.DineUI.renderResults(data, payload.user_id);
        } catch (err) {
            console.error("Recommendation fetch failed:", err);
            window.DineUI.showError(err.message || "Could not reach the server. Please check your connection.");
        }
    }

    // ===== INIT =====

    // Quick health check to warm up and give early feedback
    window.DineAPI.checkHealth().then((ok) => {
        if (!ok) {
            window.DineUI.showToast("⚠️", "Backend APIs are currently unreachable.");
        }
    });
});
