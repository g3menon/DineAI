"""
test_phase5_frontend.py — Phase 5 Frontend Test Suite

Tests the frontend files exist, checks HTML structure, CSS coverage,
JS modules, and verifies end-to-end API connectivity by calling the
Phase 4 backend through the frontend's expected endpoints.

Run with:
    python -m pytest tests/test_phase5_frontend.py -v

Requires the Phase 4 backend to be running on http://localhost:8004
for the API connectivity tests.
"""
import os
import re
from pathlib import Path

import pytest

# Resolve paths
PHASE5_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = PHASE5_DIR / "frontend"


# ============================================================
# 1. FILE STRUCTURE TESTS
# ============================================================

class TestFileStructure:
    """Verify that all required Phase 5 frontend files exist."""

    def test_index_html_exists(self):
        assert (FRONTEND_DIR / "index.html").is_file(), "index.html is missing"

    def test_styles_css_exists(self):
        assert (FRONTEND_DIR / "css" / "styles.css").is_file(), "css/styles.css is missing"

    def test_api_js_exists(self):
        assert (FRONTEND_DIR / "js" / "api.js").is_file(), "js/api.js is missing"

    def test_ui_js_exists(self):
        assert (FRONTEND_DIR / "js" / "ui.js").is_file(), "js/ui.js is missing"

    def test_app_js_exists(self):
        assert (FRONTEND_DIR / "js" / "app.js").is_file(), "js/app.js is missing"

    def test_no_unexpected_files_in_js(self):
        """Only expected JS files should be in the js/ directory."""
        js_dir = FRONTEND_DIR / "js"
        expected = {"api.js", "ui.js", "app.js"}
        actual = {f.name for f in js_dir.iterdir() if f.is_file()}
        assert actual == expected, f"Unexpected JS files: {actual - expected}"


# ============================================================
# 2. HTML STRUCTURE TESTS
# ============================================================

class TestHTMLStructure:
    """Validate that index.html has the required structural elements."""

    @pytest.fixture(autouse=True)
    def load_html(self):
        self.html = (FRONTEND_DIR / "index.html").read_text(encoding="utf-8")

    def test_doctype(self):
        assert self.html.strip().startswith("<!DOCTYPE html>"), "Missing DOCTYPE"

    def test_has_lang_attribute(self):
        assert 'lang="en"' in self.html, "Missing lang attribute on <html>"

    def test_has_viewport_meta(self):
        assert 'name="viewport"' in self.html, "Missing viewport meta tag"

    def test_has_meta_description(self):
        assert 'name="description"' in self.html, "Missing meta description for SEO"

    def test_has_title(self):
        assert "<title>" in self.html and "</title>" in self.html, "Missing <title> tag"

    def test_has_single_h1(self):
        h1_count = self.html.count("<h1")
        assert h1_count == 1, f"Expected exactly 1 <h1>, found {h1_count}"

    def test_has_header(self):
        assert '<header' in self.html, "Missing <header> element"

    def test_has_main(self):
        assert '<main' in self.html, "Missing <main> element"

    def test_has_footer(self):
        assert '<footer' in self.html, "Missing <footer> element"

    # --- Filter elements ---
    def test_has_location_input(self):
        assert 'id="locationInput"' in self.html, "Missing location input"

    def test_has_price_group(self):
        assert 'id="priceGroup"' in self.html, "Missing price range button group"
        for value in ["low", "mid", "high"]:
            assert f'data-value="{value}"' in self.html, f"Missing price option: {value}"

    def test_has_rating_slider(self):
        assert 'id="ratingSlider"' in self.html, "Missing rating slider"

    def test_has_cuisine_input(self):
        assert 'id="cuisineInput"' in self.html, "Missing cuisine input"

    def test_has_cuisine_chips(self):
        assert 'id="cuisineChips"' in self.html, "Missing cuisine chips"

    def test_has_user_id_input(self):
        assert 'id="userIdInput"' in self.html, "Missing user ID input"

    def test_has_submit_button(self):
        assert 'id="submitBtn"' in self.html, "Missing submit button"

    # --- Result states ---
    def test_has_empty_state(self):
        assert 'id="emptyState"' in self.html, "Missing empty state"

    def test_has_loading_state(self):
        assert 'id="loadingState"' in self.html, "Missing loading state"

    def test_has_error_state(self):
        assert 'id="errorState"' in self.html, "Missing error state"

    def test_has_llm_summary(self):
        assert 'id="llmSummary"' in self.html, "Missing LLM summary area"

    def test_has_cards_grid(self):
        assert 'id="cardsGrid"' in self.html, "Missing cards grid"

    def test_has_no_results(self):
        assert 'id="noResults"' in self.html, "Missing no-results state"

    def test_has_toast(self):
        assert 'id="toast"' in self.html, "Missing toast notification"

    # --- Script includes ---
    def test_scripts_loaded_in_order(self):
        api_pos = self.html.find('src="js/api.js"')
        ui_pos = self.html.find('src="js/ui.js"')
        app_pos = self.html.find('src="js/app.js"')
        assert api_pos < ui_pos < app_pos, "Scripts must load in order: api.js → ui.js → app.js"

    def test_google_fonts_loaded(self):
        assert "fonts.googleapis.com" in self.html, "Missing Google Fonts link"

    def test_stylesheet_linked(self):
        assert 'href="css/styles.css"' in self.html, "Missing stylesheet link"


# ============================================================
# 3. CSS TESTS
# ============================================================

class TestCSS:
    """Validate CSS has required design tokens and responsive rules."""

    @pytest.fixture(autouse=True)
    def load_css(self):
        self.css = (FRONTEND_DIR / "css" / "styles.css").read_text(encoding="utf-8")

    def test_has_custom_properties(self):
        assert ":root" in self.css, "Missing :root CSS custom properties"

    def test_has_dark_mode_colors(self):
        assert "--bg-primary" in self.css, "Missing --bg-primary token"
        assert "--accent" in self.css, "Missing --accent token"

    def test_has_light_mode(self):
        assert '[data-theme="light"]' in self.css, "Missing light mode overrides"

    def test_has_responsive_breakpoints(self):
        assert "@media" in self.css, "Missing media queries"
        assert "900px" in self.css, "Missing tablet breakpoint (900px)"
        assert "600px" in self.css, "Missing mobile breakpoint (600px)"

    def test_has_animations(self):
        assert "@keyframes" in self.css, "Missing CSS animations"
        for anim in ["spin", "fadeInUp", "slideDown"]:
            assert anim in self.css, f"Missing animation: {anim}"

    def test_has_card_styles(self):
        assert ".card" in self.css, "Missing .card styles"
        assert ".card:hover" in self.css, "Missing card hover effects"

    def test_has_glassmorphism_header(self):
        assert "backdrop-filter" in self.css, "Missing glassmorphism backdrop-filter"

    def test_has_hidden_utility(self):
        assert ".hidden" in self.css, "Missing .hidden utility class"

    def test_has_grid_layout(self):
        assert "grid-template-columns" in self.css, "Missing grid layout"

    def test_has_inter_font(self):
        assert "'Inter'" in self.css or "Inter" in self.css, "Missing Inter font reference"


# ============================================================
# 4. JAVASCRIPT MODULE TESTS
# ============================================================

class TestAPIModule:
    """Validate api.js has required functions and structure."""

    @pytest.fixture(autouse=True)
    def load_js(self):
        self.js = (FRONTEND_DIR / "js" / "api.js").read_text(encoding="utf-8")

    def test_has_base_url(self):
        assert "localhost:8004" in self.js, "Missing API base URL"

    def test_has_fetch_recommendations(self):
        assert "fetchRecommendations" in self.js, "Missing fetchRecommendations function"

    def test_has_submit_feedback(self):
        assert "submitFeedback" in self.js, "Missing submitFeedback function"

    def test_has_check_health(self):
        assert "checkHealth" in self.js, "Missing checkHealth function"

    def test_posts_to_correct_endpoints(self):
        assert "/api/recommendations" in self.js, "Missing /api/recommendations endpoint"
        assert "/api/feedback" in self.js, "Missing /api/feedback endpoint"
        assert "/health" in self.js, "Missing /health endpoint"

    def test_exports_to_window(self):
        assert "window.DineAPI" in self.js, "Missing window.DineAPI export"

    def test_uses_json_content_type(self):
        assert '"Content-Type": "application/json"' in self.js, "Missing JSON content type header"


class TestUIModule:
    """Validate ui.js has required rendering functions."""

    @pytest.fixture(autouse=True)
    def load_js(self):
        self.js = (FRONTEND_DIR / "js" / "ui.js").read_text(encoding="utf-8")

    def test_has_show_loading(self):
        assert "showLoading" in self.js, "Missing showLoading function"

    def test_has_show_error(self):
        assert "showError" in self.js, "Missing showError function"

    def test_has_show_empty(self):
        assert "showEmpty" in self.js, "Missing showEmpty function"

    def test_has_render_results(self):
        assert "renderResults" in self.js, "Missing renderResults function"

    def test_has_show_toast(self):
        assert "showToast" in self.js, "Missing showToast function"

    def test_has_card_creation(self):
        assert "createRestaurantCard" in self.js, "Missing createRestaurantCard function"

    def test_has_feedback_handler(self):
        assert "handleFeedback" in self.js, "Missing handleFeedback function"

    def test_has_star_rendering(self):
        assert "renderStars" in self.js, "Missing renderStars function"

    def test_has_xss_protection(self):
        assert "escapeHtml" in self.js, "Missing escapeHtml XSS protection"

    def test_exports_to_window(self):
        assert "window.DineUI" in self.js, "Missing window.DineUI export"


class TestAppModule:
    """Validate app.js has required initialization logic."""

    @pytest.fixture(autouse=True)
    def load_js(self):
        self.js = (FRONTEND_DIR / "js" / "app.js").read_text(encoding="utf-8")

    def test_has_dom_content_loaded(self):
        assert "DOMContentLoaded" in self.js, "Missing DOMContentLoaded listener"

    def test_has_theme_toggle(self):
        assert "themeToggle" in self.js, "Missing theme toggle logic"
        assert "localStorage" in self.js, "Missing localStorage for theme persistence"

    def test_has_form_submit_handler(self):
        assert "submit" in self.js, "Missing form submit handler"

    def test_has_price_group_handler(self):
        assert "priceGroup" in self.js, "Missing price group handler"

    def test_has_rating_slider_handler(self):
        assert "ratingSlider" in self.js, "Missing rating slider handler"

    def test_has_cuisine_chips_handler(self):
        assert "cuisineChips" in self.js, "Missing cuisine chips handler"

    def test_has_collapse_handler(self):
        assert "collapseBtn" in self.js or "collapsed" in self.js, "Missing collapse handler"

    def test_calls_dine_api(self):
        assert "DineAPI" in self.js, "Missing DineAPI calls"

    def test_calls_dine_ui(self):
        assert "DineUI" in self.js, "Missing DineUI calls"

    def test_has_search_logic(self):
        assert "performSearch" in self.js, "Missing performSearch function"


# ============================================================
# 5. API CONNECTIVITY TESTS (require running backend)
# ============================================================

class TestAPIConnectivity:
    """Test actual API calls to the Phase 4 backend.

    These tests require the backend to be running on http://localhost:8004.
    They are automatically skipped if the backend is unreachable.
    """

    BACKEND_URL = "http://localhost:8004"

    @pytest.fixture(autouse=True)
    def check_backend(self):
        """Skip all tests in this class if backend is not running."""
        import httpx
        try:
            r = httpx.get(f"{self.BACKEND_URL}/health", timeout=5.0)
            if r.status_code != 200:
                pytest.skip("Backend not returning 200 on /health")
        except Exception:
            pytest.skip("Backend not reachable at localhost:8004")

    def test_health_endpoint(self):
        import httpx
        r = httpx.get(f"{self.BACKEND_URL}/health", timeout=5.0)
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_recommendations_endpoint(self):
        import httpx
        payload = {
            "location": "Bangalore",
            "price_range": "mid",
            "min_rating": 3.5,
            "cuisine": "Italian",
        }
        r = httpx.post(f"{self.BACKEND_URL}/api/recommendations", json=payload, timeout=30.0)
        assert r.status_code == 200
        data = r.json()
        assert "results" in data
        assert "llm_used" in data
        assert "llm_summary" in data
        assert isinstance(data["results"], list)

    def test_recommendations_response_structure(self):
        import httpx
        payload = {
            "location": "Bangalore",
            "price_range": "mid",
            "min_rating": 3.0,
        }
        r = httpx.post(f"{self.BACKEND_URL}/api/recommendations", json=payload, timeout=30.0)
        assert r.status_code == 200
        data = r.json()
        if data["results"]:
            first = data["results"][0]
            assert "name" in first
            assert "location" in first
            assert "rating" in first
            assert "price" in first
            assert "cuisine" in first
            assert "reason" in first

    def test_recommendations_with_user_id(self):
        import httpx
        payload = {
            "location": "Bangalore",
            "price_range": "mid",
            "min_rating": 3.5,
            "user_id": "test-phase5-user",
        }
        r = httpx.post(f"{self.BACKEND_URL}/api/recommendations", json=payload, timeout=30.0)
        assert r.status_code == 200

    def test_feedback_endpoint(self):
        """Submit feedback — only works if there are restaurants in the DB."""
        import httpx
        # First get a recommendation to have a restaurant name
        rec_payload = {
            "location": "Bangalore",
            "price_range": "mid",
            "min_rating": 3.0,
        }
        r = httpx.post(f"{self.BACKEND_URL}/api/recommendations", json=rec_payload, timeout=30.0)
        data = r.json()
        if not data["results"]:
            pytest.skip("No results to test feedback against")

        restaurant_name = data["results"][0]["name"]

        feedback_payload = {
            "user_id": "test-phase5-user",
            "restaurant_name": restaurant_name,
            "liked": True,
        }
        r2 = httpx.post(f"{self.BACKEND_URL}/api/feedback", json=feedback_payload, timeout=10.0)
        assert r2.status_code == 200
        assert r2.json()["status"] == "ok"

    def test_invalid_request_returns_422(self):
        """Invalid payload should return 422 (validation error)."""
        import httpx
        payload = {
            "location": "",
            "price_range": "invalid",
            "min_rating": 10,
        }
        r = httpx.post(f"{self.BACKEND_URL}/api/recommendations", json=payload, timeout=10.0)
        assert r.status_code == 422
