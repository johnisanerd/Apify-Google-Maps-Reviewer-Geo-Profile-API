# 🗺️ Google Maps Reviewer Geo Profile API: infer a reviewer's home region from their reviews

> The most efficient, reliable, and developer-friendly way to use the Google Maps Reviewer Geo Profile API.

**Actor page:** [apify.com/johnvc/google-maps-reviewer-geo-profile-api](https://apify.com/johnvc/google-maps-reviewer-geo-profile-api?fpr=9n7kx3)
**Input schema:** [apify.com/johnvc/google-maps-reviewer-geo-profile-api/input-schema](https://apify.com/johnvc/google-maps-reviewer-geo-profile-api/input-schema?fpr=9n7kx3)

Give this API a Google Maps contributor ID and it infers where that reviewer is based from their public review history. It reverse-geocodes the coordinates attached to every review and clusters them into one derived profile per reviewer: a standardized home-region guess (city, state, country, plus ISO 3166 codes), a confidence score, how many reviews sit in the home cluster versus travel outliers, a footprint of the regions they review in, and a centroid and bounding box. It is built for aggregate reviewer vetting, reputation research, and review-fraud detection. It works at region level and is not a tool for locating a specific individual.

## Video Walkthrough

[![Watch the walkthrough](https://img.youtube.com/vi/jREWahDGhJM/maxresdefault.jpg)](https://www.youtube.com/watch?v=jREWahDGhJM)

## Quick Start

### Prerequisites
- Python 3.11 or higher
- An Apify account and API key ([get a free key here](https://apify.com?fpr=9n7kx3))

1. **Clone the repository**
   ```bash
   git clone https://github.com/johnisanerd/Apify-Google-Maps-Reviewer-Geo-Profile-API.git
   cd Apify-Google-Maps-Reviewer-Geo-Profile-API
   ```

2. **Install dependencies with UV**
   ```bash
   # Install UV if you do not have it:
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Install project dependencies:
   uv sync
   ```

3. **Configure your API key**
   ```bash
   cp .env.example .env
   # Edit .env and add your Apify API key
   # Get your free API key at: https://apify.com?fpr=9n7kx3
   ```

4. **Run the example**
   ```bash
   uv run python google-maps-reviewer-geo-profile-api-example.py
   ```

### Alternative: set the API key directly
```bash
export APIFY_API_TOKEN="your_api_key_here"
uv run python google-maps-reviewer-geo-profile-api-example.py
```

## Why Use This Google Maps Reviewer Geo Profile API?

**One answer per reviewer.** Instead of paging through a reviewer's history yourself, you get a single derived row: where they are based, how confident that guess is, and how far they roam. Pass a `contributorIds` list to profile a whole batch of reviewers in one run.

**Standardized, joinable output.** Regions come back with ISO 3166-1 country codes and best-effort ISO 3166-2 subdivision codes, resolved offline, so you can group or filter reviewers by `home_country_code` or `home_admin_code` without parsing free-text addresses that vary by language.

**A real fraud and vetting signal.** A tight cluster with high `confidence` looks like a genuine local; reviews scattered across many distant regions (`distinct_regions`, `travel_outliers`) are a classic paid-review tell. The footprint makes that pattern obvious.

**Region level by design.** The output stops at city or coarser, which keeps it useful for aggregate vetting and reputation research while staying away from identifying or tracking any individual.

**MCP-ready.** Load it as a tool in Claude, Cursor, or ChatGPT and ask an agent to profile a reviewer's home region and tell you whether the footprint looks locally coherent.

## Features

### Core Capabilities
- Infer a reviewer's `home_region_guess` at city, state/province (`admin1`), or country granularity
- Standardized `home_city`, `home_admin`, `home_admin_code` (ISO 3166-2), `home_country`, `home_country_code` (ISO 3166-1)
- Confidence score plus `home_cluster_size` vs `travel_outliers` and `distinct_regions`
- A `footprint` of the top regions with counts and shares, plus a `centroid` and `bounding_box`
- Batch mode: profile many reviewers in one run with `contributorIds`

### Data Quality
- Region resolved offline from review coordinates, so it does not depend on how an address happens to be written
- Neighborhood snapping (`minCityPopulation`) groups big-metro neighborhoods under the principal city (for example, Chicago)
- Deeper history (`maxResultsPerContributor`, up to 200) sharpens the home cluster by diluting a travel-heavy recent window

## Usage Examples

### Basic Example
```json
{
  "contributorId": "107022004965696773221",
  "regionGranularity": "city"
}
```

### Advanced Example
```json
{
  "contributorIds": ["107022004965696773221", "112233445566778899001"],
  "regionGranularity": "admin1",
  "minCityPopulation": 100000,
  "maxResultsPerContributor": 200,
  "hl": "en"
}
```

## Input Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `contributorId` | `str` | one of | - | A single Google Maps contributor ID (the long numeric ID from a reviewer's profile). Provide this, `contributorIds`, or both. |
| `contributorIds` | `list[str]` | one of | - | A batch of contributor IDs to profile in one run. Merged with `contributorId` and de-duplicated. |
| `regionGranularity` | `str` | no | `city` | Level the home-region guess is computed at: `city`, `admin1` (state/province), or `country`. |
| `minCityPopulation` | `int` | no | `100000` | Snap each review to the nearest city of at least this size, so metro neighborhoods group under the principal city. Lower it to keep smaller towns distinct. |
| `maxResultsPerContributor` | `int` | no | `100` | Reviews to analyze per contributor, most recent first (maximum 200). Deeper history sharpens the home cluster. |
| `hl` | `str` | no | `en` | Two-letter language code for the source reviews. |

## Output Format

One row per reviewer:

```json
{
  "result_type": "reviewer_geo_profile",
  "contributor_id": "107022004965696773221",
  "contributor_name": "Matt Moeini",
  "contributor_level": 5,
  "contributor_local_guide": true,
  "home_region_guess": "Chicago, IL",
  "home_city": "Chicago",
  "home_admin": "Illinois",
  "home_admin_code": "US-IL",
  "home_country": "United States",
  "home_country_code": "US",
  "confidence": 0.5312,
  "home_cluster_size": 17,
  "travel_outliers": 15,
  "located_reviews": 32,
  "total_reviews": 32,
  "distinct_regions": 13,
  "region_granularity": "city",
  "min_city_population": 100000,
  "footprint": [
    { "region": "Chicago, IL", "count": 17, "share": 0.5312 },
    { "region": "Miami, FL", "count": 2, "share": 0.0625 },
    { "region": "Tehran, Tehran", "count": 2, "share": 0.0625 }
  ],
  "centroid": { "latitude": 41.923811, "longitude": -87.648254 },
  "bounding_box": { "min_latitude": 25.7617, "min_longitude": -87.6847, "max_latitude": 41.9784, "max_longitude": -80.1918 }
}
```

---

## Install in Claude Cowork Desktop

![Install in Claude Cowork Desktop](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_desktop.png)

Cowork is the desktop app's automation mode. To give it the Google Maps Reviewer Geo Profile API as a tool, add the Apify MCP server as a connector.

1. Open the Claude desktop app and go to **Settings → Connectors** (or **Settings → Developer → Edit Config** to edit `claude_desktop_config.json` directly).
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
2. Add the Apify MCP server, preloaded with only this Actor:

```json
{
  "mcpServers": {
    "apify": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.apify.com/?tools=actors,docs,johnvc/google-maps-reviewer-geo-profile-api"
      ]
    }
  }
}
```

3. Restart the app. When Cowork first calls the tool, complete the OAuth prompt in your browser, or add your Apify API token in the connector settings to skip OAuth.
4. In a Cowork chat, confirm the tool is available and ask it to run the Google Maps Reviewer Geo Profile API.

Download the desktop app and start a free trial: https://claude.ai/referral/uIlpa7nPLg
More help: https://docs.apify.com/platform/integrations/claude-desktop

## Install in Claude Code

![Install in Claude Code](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_code.png)

Claude Code is the command-line tool. Add the Actor's MCP server with one command:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/google-maps-reviewer-geo-profile-api"
```

To use a token instead of browser OAuth:

```bash
claude mcp add --transport http apify \
  "https://mcp.apify.com/?tools=actors,docs,johnvc/google-maps-reviewer-geo-profile-api" \
  --header "Authorization: Bearer YOUR_APIFY_TOKEN"
```

Then verify with `claude mcp list`, or run `/mcp` inside a session. Ask Claude Code to call the Google Maps Reviewer Geo Profile API.

Try Claude Code free: https://claude.ai/referral/uIlpa7nPLg
Claude Code MCP docs: https://code.claude.com/docs/en/mcp

## Install in Claude (website)

![Install in Claude (website)](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_claude_ai.png)

On claude.ai you add Apify as a connector, then enable just this Actor's tool.

1. Go to **Settings → Connectors → Browse connectors** and search for **Apify MCP server**. Install it (enable or update if prompted).
2. When connecting, authenticate with your Apify API token, and enable the tool `johnvc/google-maps-reviewer-geo-profile-api`.
3. In any chat, open **+ → Connectors** and turn on **Apify**.
4. Alternatively, choose **Add custom connector** and paste the full MCP URL `https://mcp.apify.com/?tools=actors,docs,johnvc/google-maps-reviewer-geo-profile-api`, using OAuth when prompted.
5. Ask Claude to run the Google Maps Reviewer Geo Profile API.

Open Claude on the web: https://claude.ai/referral/uIlpa7nPLg

## Install in Cursor

![Install in Cursor](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_cursor.png)

Cursor reads MCP servers from a project file at `.cursor/mcp.json`.

1. In your project, create `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/google-maps-reviewer-geo-profile-api"
    }
  }
}
```

2. If you prefer token auth over browser OAuth, add a header:

```json
{
  "mcpServers": {
    "apify": {
      "url": "https://mcp.apify.com/?tools=actors,docs,johnvc/google-maps-reviewer-geo-profile-api",
      "headers": { "Authorization": "Bearer YOUR_APIFY_TOKEN" }
    }
  }
}
```

3. Open **Cursor → Settings → MCP** and confirm the **apify** server is connected (green dot).
4. In Composer or Chat, ask Cursor to call the Google Maps Reviewer Geo Profile API.

New to Cursor? Get it here: https://cursor.com/referral?code=XQP4VBLI3NNX

## Install in ChatGPT

![Install in ChatGPT](https://raw.githubusercontent.com/johnisanerd/ApifyPublicData/main/assets/guides/install_mcp_into_ChatGPT.png)

ChatGPT connects to the Apify MCP server through Developer mode (available on ChatGPT Pro, Plus, Business, Enterprise, and Education plans).

1. Click your profile icon, then go to **Settings > Apps**. If you do not see a **Create app** button, open **Advanced settings** and enable **Developer mode**.
2. Click **Create app** and fill out the form:
   - **Name:** Apify
   - **MCP Server URL:** `https://mcp.apify.com/?tools=actors,docs,johnvc/google-maps-reviewer-geo-profile-api`
   - **Authentication:** OAuth
3. Click **Create** and authorize the connection with Apify.
4. To use the app in a conversation, click **+** in the chat, choose **Developer mode**, and select **Apify**.

More help: https://docs.apify.com/platform/integrations/mcp

## Use this from n8n

Available as an n8n community node, **[n8n-nodes-google-maps-reviewer-geo-profile-api](https://www.npmjs.com/package/n8n-nodes-google-maps-reviewer-geo-profile-api)**. In n8n: Settings, Community Nodes, install `n8n-nodes-google-maps-reviewer-geo-profile-api`, then use it in any workflow (it also works as an AI Agent tool).

---

[**Made with care**](https://apify.com/johnvc?fpr=9n7kx3)

*Use the Google Maps Reviewer Geo Profile API to power your reviewer vetting and reputation research with reliable, structured results.*

Last Updated: 2026.09.03
