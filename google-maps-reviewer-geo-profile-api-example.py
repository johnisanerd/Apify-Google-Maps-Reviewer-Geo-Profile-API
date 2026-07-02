"""
Google Maps Reviewer Geo Profile API: A Quick Start Example
See more at: https://apify.com/johnvc/google-maps-reviewer-geo-profile-api?fpr=9n7kx3
Input schema: https://apify.com/johnvc/google-maps-reviewer-geo-profile-api/input-schema?fpr=9n7kx3

This script shows how to call the Google Maps Reviewer Geo Profile API on Apify
from Python and read its structured JSON output. Give it a Google Maps contributor
ID and it infers that reviewer's home region from where their public reviews cluster:
a standardized home-region guess (city/state/country plus ISO codes), a confidence
score, and a local-vs-travel footprint. One row per reviewer.

Privacy note: this is aggregate, region-level reviewer vetting and reputation
research. It is not for locating a specific individual.

Get your free Apify API key at: https://apify.com?fpr=9n7kx3
"""

import os
from dotenv import load_dotenv
from apify_client import ApifyClient

load_dotenv()

# Initialize the Apify client with your API token (read from .env)
client = ApifyClient(os.getenv("APIFY_API_TOKEN"))

# Build the Actor input.
# One contributor keeps this first run inexpensive (you are charged per
# contributor analyzed, not per review, so depth is cheap). Raise the depth or
# pass a `contributorIds` list once you have your own API key and know your budget.
run_input = {
    "contributorId": "107022004965696773221",  # the demo reviewer clusters in Chicago, IL
    "regionGranularity": "city",                # "city" | "admin1" (state) | "country"
    "minCityPopulation": 100000,                # snap neighborhoods to the principal city
    "maxResultsPerContributor": 50,             # deeper history sharpens the home cluster
    "hl": "en",
}

# Run the Actor and wait for it to finish
run = client.actor("johnvc/google-maps-reviewer-geo-profile-api").call(run_input=run_input)
if run is None:
    raise SystemExit("The Actor run did not return a result.")

# Read structured results from the run's default dataset
# (apify-client 3.x returns a Run object; use .default_dataset_id, not run["..."])
items = list(client.dataset(run.default_dataset_id).iterate_items())
print(f"Analyzed {len(items)} reviewer(s).\n")

# Show the derived geo profile for each reviewer.
for item in items:
    if item.get("result_type") == "error":
        print("Error:", item.get("error_message"))
        continue
    print(f"Reviewer:      {item.get('contributor_name')} ({item.get('contributor_id')})")
    print(f"Home region:   {item.get('home_region_guess')}")
    print(f"Standardized:  {item.get('home_city')}, {item.get('home_admin')} "
          f"({item.get('home_admin_code')}) - {item.get('home_country')} ({item.get('home_country_code')})")
    print(f"Confidence:    {item.get('confidence')}  "
          f"(home cluster {item.get('home_cluster_size')} vs {item.get('travel_outliers')} travel outliers, "
          f"{item.get('located_reviews')} located reviews across {item.get('distinct_regions')} regions)")
    top = (item.get("footprint") or [])[:5]
    if top:
        print("Top regions:")
        for region in top:
            print(f"  {region.get('count'):>3}  {region.get('region')}  ({region.get('share')})")
    centroid = item.get("centroid") or {}
    if centroid:
        print(f"Centroid:      {centroid.get('latitude')}, {centroid.get('longitude')}")
    print()
