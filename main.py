import os
import json
import asyncio
import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI(title="What NOT to Learn Engine")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

BRIGHTDATA_API_KEY = os.getenv("BRIGHTDATA_API_KEY", "Enter your Bright data API key here.")
FEATHERLESS_API_KEY = os.getenv("FEATHERLESS_API_KEY", "Enter your Featherless ai API key here.")

BRIGHTDATA_BASE_URL = "https://api.brightdata.com/serp/google"
FEATHERLESS_BASE_URL = "https://api.featherless.ai/v1"


async def scrape_trends_brightdata(query: str) -> str:
    """Use Bright Data SERP API to get real-time job/skill trend data."""
    search_queries = [
        f"{query} skills in demand 2025",
        f"outdated {query} skills to avoid",
        f"best {query} technologies 2025 job market",
    ]

    collected_snippets = []

    async with httpx.AsyncClient(timeout=30.0) as client:
        for search_query in search_queries:
            try:
                payload = {
                    "query": search_query,
                    "country": "us",
                    "num_results": 5,
                }
                headers = {
                    "Authorization": f"Bearer {BRIGHTDATA_API_KEY}",
                    "Content-Type": "application/json",
                }
                response = await client.post(
                    BRIGHTDATA_BASE_URL,
                    json=payload,
                    headers=headers,
                )
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("organic", []) or data.get("results", [])
                    for r in results[:3]:
                        title = r.get("title", "")
                        snippet = r.get("snippet", r.get("description", ""))
                        if title or snippet:
                            collected_snippets.append(f"- {title}: {snippet}")
                else:
                    # fallback: try alternative endpoint structure
                    collected_snippets.append(
                        f"[Trend data for '{search_query}' unavailable, using AI knowledge]"
                    )
            except Exception as e:
                collected_snippets.append(
                    f"[Search error for '{search_query}': {str(e)[:80]}]"
                )

    if not collected_snippets:
        return f"No trend data fetched. Using AI knowledge for: {query}"

    return "\n".join(collected_snippets[:15])


async def analyze_with_featherless(query: str, trend_data: str) -> dict:
    """Send query + trend data to Featherless AI for structured analysis."""

    system_prompt = """You are a senior tech career advisor with deep knowledge of industry trends, job markets, and technology lifecycles. You analyze real-time data and provide brutally honest advice about which skills are declining vs rising.

Always respond with ONLY valid JSON — no markdown, no explanation outside the JSON. The JSON must follow this exact structure:
{
  "avoid": [
    {"skill": "...", "reason": "..."},
    {"skill": "...", "reason": "..."},
    {"skill": "...", "reason": "..."}
  ],
  "alternatives": [
    {"skill": "...", "reason": "..."},
    {"skill": "...", "reason": "..."},
    {"skill": "...", "reason": "..."}
  ],
  "summary": "One paragraph overall strategic advice for this career goal."
}

Provide 3-5 items in each list. Reasons must be specific, data-driven, and reference trends, job market demand, or technology lifecycle facts."""

    user_message = f"""Career goal / domain: "{query}"

Real-time trend data scraped from the web:
{trend_data}

Based on this data and your knowledge of the current tech job market (2024-2025):
1. List skills/technologies to AVOID learning (declining, outdated, or low ROI)
2. List better ALTERNATIVES to focus on instead (high demand, future-proof)
3. Provide a brief strategic summary

Return ONLY the JSON object."""

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{FEATHERLESS_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {FEATHERLESS_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "meta-llama/Meta-Llama-3.1-70B-Instruct",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "max_tokens": 1500,
                "temperature": 0.3,
            },
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Featherless API error: {response.status_code} - {response.text[:300]}",
            )

        data = response.json()
        raw_text = data["choices"][0]["message"]["content"].strip()

        # Strip markdown fences if present
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        raw_text = raw_text.strip()

        parsed = json.loads(raw_text)
        return parsed


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/analyze")
async def analyze(request: Request):
    body = await request.json()
    query = body.get("query", "").strip()

    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    if len(query) > 200:
        raise HTTPException(status_code=400, detail="Query too long (max 200 chars).")

    # Step 1: Scrape trends
    trend_data = await scrape_trends_brightdata(query)

    # Step 2: Analyze with Featherless AI
    result = await analyze_with_featherless(query, trend_data)

    return JSONResponse(content=result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)