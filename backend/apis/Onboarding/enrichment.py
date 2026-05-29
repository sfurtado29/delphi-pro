# backend/apis/Onboarding/enrichment.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import get_conn

from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup
import httpx
import json
import asyncio
import concurrent.futures

router = APIRouter(
    prefix="/onboarding",
    tags=["Onboarding"]
)

# ─────────────────────────────────────────
# CONFIG LIMITS (VERY IMPORTANT)
# ─────────────────────────────────────────

MAX_PAGES = 5
MAX_BRANDS = 20
MIN_BRANDS_THRESHOLD = 3


# ─────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────

class EnrichRequest(BaseModel):
    website_url: str
    user_id: int


class SaveProfileRequest(BaseModel):
    user_id: int
    company_name: str
    company_size: str
    headquarters: str
    type: str
    founded: str
    revenue_size: str
    specialties: str
    website: str
    brands: str


# ─────────────────────────────────────────
# URL Normalizer
# ─────────────────────────────────────────

def normalize_url(url: str) -> str:
    url = url.strip()

    if not url.startswith("http"):
        url = "https://" + url

    return url.rstrip("/")


# ─────────────────────────────────────────
# Brand Validation
# ─────────────────────────────────────────

def _is_valid_brand(text: str) -> bool:

    text = text.strip()

    if not text:
        return False

    # length filter
    if len(text) < 2 or len(text) > 40:
        return False

    # too many words → sentence → reject
    if len(text.split()) > 3:
        return False

    lower = text.lower()

    # strong noise list
    skip_words = {

        # navigation
        "home", "about", "contact",
        "shopping", "discover",
        "service", "services",
        "parts", "support",

        # CTA buttons
        "book", "register",
        "submit", "explore",
        "know more",
        "learn more",
        "read more",

        # generic
        "menu",
        "search",
        "login",
        "signup",
        "register now",

        # footer junk
        "privacy policy",
        "terms",
        "cookies",

        # UI phrases
        "skip to main content",
        "owner's information",
        "customer stories",
        "test drive",
        "book a test drive",

        # categories (not models)
        "suv",
        "sedan",
        "hatchback",
        "range"
    }

    if lower in skip_words:
        return False

    # reject sentences
    if any(word in lower for word in [
        "drive",
        "experience",
        "explore",
        "discover",
        "information"
    ]):
        return False

    # reject numbers-heavy text
    digits = sum(c.isdigit() for c in text)

    if digits > 4:
        return False

    return True


# ─────────────────────────────────────────
# Extract Brands
# ─────────────────────────────────────────

def extract_brands_from_soup(
        soup: BeautifulSoup
) -> list:

    found = []

    section_keywords = [
        "model",
        "models",
        "brand",
        "brands",
        "product",
        "products",
        "portfolio",
        "series",
        "range","cars",
        "lineup",
        "collection",
        "catalog",
        "subsidiaries",
        "divisions"
    ]

    # FOOTER FIRST

    footer = soup.find("footer")

    if footer:

        for tag in footer.find_all(
                ["section", "div", "ul", "nav"]
        ):

            tag_id = (tag.get("id") or "").lower()

            tag_class = " ".join(
                tag.get("class") or []
            ).lower()

            if any(
                kw in tag_id or kw in tag_class
                for kw in section_keywords
            ):

                for item in tag.find_all(
                        ["li", "a"]
                )[:40]:

                    text = item.get_text(
                        strip=True
                    )

                    if _is_valid_brand(text):
                        found.append(text)

                if found:
                    break

    # BODY SCAN

    if not found:

        for tag in soup.find_all(
                ["section", "div", "ul"]
        ):

            tag_text = tag.get_text(
                separator=" "
            ).lower()[:200]

            if any(
                kw in tag_text
                for kw in section_keywords
            ):

                for item in tag.find_all(
                        ["li", "h2", "h3", "a"]
                )[:40]:

                    text = item.get_text(
                        strip=True
                    )

                    if _is_valid_brand(text):
                        found.append(text)

                if len(found) >= 3:
                    break

    # JSON-LD

    if not found:

        for script in soup.find_all(
                "script",
                type="application/ld+json"
        ):

            try:

                data = json.loads(
                    script.string or ""
                )

                if not isinstance(
                        data, dict
                ):
                    continue

                for key in [
                    "brand",
                    "model",
                    "subOrganization",
                    "Product Overview",
                    "Product"
                ]:

                    val = data.get(key)

                    if not val:
                        continue

                    if isinstance(val, list):

                        for b in val:

                            if isinstance(
                                    b, dict
                            ) and b.get("name"):

                                found.append(
                                    b["name"]
                                )

                    elif isinstance(
                            val, dict
                    ):

                        if val.get("name"):
                            found.append(
                                val["name"]
                            )

            except Exception:
                pass

    # Deduplicate

    seen = set()
    unique = []

    for item in found:

        if item.lower() not in seen:

            seen.add(item.lower())
            unique.append(item)

    return unique[:MAX_BRANDS]


# ─────────────────────────────────────────
# Discover Product Pages
# ─────────────────────────────────────────

def find_product_links(
        soup: BeautifulSoup,
        base_url: str
) -> list:

    keywords = [
        "product",
        "products",
        "brand",
        "brands",
        "model",
        "models",
        "portfolio",
        "cars",
        "solutions",
        "catalog",
        "collection",
        "range",
        "lineup",
        "All Models"
    ]

    links = set()

    nav_sections = soup.find_all(
        ["nav", "header"]
    )

    for section in nav_sections:

        for a in section.find_all(
                "a",
                href=True
        ):

            text = a.get_text(
                strip=True
            ).lower()

            href = a["href"].lower()

            if any(
                kw in text or kw in href
                for kw in keywords
            ):

                full_url = urljoin(
                    base_url,
                    a["href"]
                )

                links.add(full_url)

    return list(links)[:MAX_PAGES]


# ─────────────────────────────────────────
# HTTPX Fetch
# ─────────────────────────────────────────

async def fetch_with_httpx(
        url: str
) -> str:

    headers = {
        "User-Agent":
        "Mozilla/5.0"
    }

    try:

        async with httpx.AsyncClient(
                follow_redirects=True,
                timeout=15.0,
                headers=headers,
                verify=False
        ) as client:

            res = await client.get(url)

            if res.status_code == 200:

                if len(res.text) > 500:
                    return res.text

    except Exception:
        pass

    return ""


# ─────────────────────────────────────────
# Playwright Thread
# ─────────────────────────────────────────

def _playwright_thread(url: str):

    loop = asyncio.new_event_loop()

    try:
        return loop.run_until_complete(
            _playwright_fetch(url)
        )
    finally:
        loop.close()


async def _playwright_fetch(
        url: str
) -> str:

    try:

        from playwright.async_api import async_playwright

        async with async_playwright() as p:

            browser = await p.chromium.launch(
                headless=True
            )

            page = await browser.new_page()

            await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            await page.wait_for_timeout(3000)

            html = await page.content()

            await browser.close()

            return html

    except Exception:

        return ""


# ─────────────────────────────────────────
# Multi-Page Scraper
# ─────────────────────────────────────────

async def scrape_website(
        url: str
) -> dict:

    url = normalize_url(url)

    parsed = urlparse(url)

    root_url = f"{parsed.scheme}://{parsed.netloc}"

    visited = set()

    collected_brands = []

    queue = [url]

    while queue:

        current_url = queue.pop(0)

        if current_url in visited:
            continue

        if len(visited) >= MAX_PAGES:
            break

        visited.add(current_url)

        print(f"[Scraper] Visiting: {current_url}")

        html = await fetch_with_httpx(
            current_url
        )

        if not html:

            loop = asyncio.get_event_loop()

            with concurrent.futures.ThreadPoolExecutor() as pool:

                html = await loop.run_in_executor(
                    pool,
                    _playwright_thread,
                    current_url
                )

        if not html:
            continue

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        brands = extract_brands_from_soup(
            soup
        )

        collected_brands.extend(brands)

        if len(collected_brands) >= MIN_BRANDS_THRESHOLD:

            continue

        # Discover new pages

        new_links = find_product_links(
            soup,
            root_url
        )

        for link in new_links:

            if link not in visited:

                queue.append(link)

    # Final Dedup

    seen = set()

    final = []

    for b in collected_brands:

        if b.lower() not in seen:

            seen.add(b.lower())

            final.append(b)

    if not final:

        return {
            "scraped": False,
            "reason":
            "No brands/products detected"
        }

    return {
        "scraped": True,
        "website": url,
        "brands":
        ", ".join(final[:MAX_BRANDS])
    }


# ─────────────────────────────────────────
# API ROUTES
# ─────────────────────────────────────────

@router.post("/enrich")
async def enrich_company(
        payload: EnrichRequest
):

    if not payload.website_url.strip():

        raise HTTPException(
            status_code=400,
            detail="Website URL required"
        )

    result = await scrape_website(
        payload.website_url
    )

    return {
        "success": True,
        "scraped":
        result.get("scraped", False),

        "message":
        result.get("reason", ""),

        "data": {
            "website":
            result.get("website", ""),

            "brands":
            result.get("brands", "")
        }
    }

@router.post("/save-profile")
async def save_profile(payload: SaveProfileRequest):

    try:
        conn = get_conn()
        cursor = conn.cursor()

        query = """
        INSERT INTO delphi_company_profiles (
            user_id,
            company_name,
            company_size,
            headquarters,
            type,
            founded,
            revenue_size,
            specialties,
            website,
            brands
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        values = (
            payload.user_id,
            payload.company_name,
            payload.company_size,
            payload.headquarters,
            payload.type,
            payload.founded,
            payload.revenue_size,
            payload.specialties,
            payload.website,
            payload.brands
        )

        cursor.execute(query, values)

        conn.commit()

        return {
            "success": True,
            "message": "Profile saved successfully"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass