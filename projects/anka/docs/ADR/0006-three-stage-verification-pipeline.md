# 6. Three-Stage Verification Pipeline for Data Enrichment

Date: 2026-01-26

## Status

Accepted

## Context

We need to provide verified business contact information (phone, website) to our users based on city and sector queries. 
Directly jumping to premium API calls (like Google Places Enterprise / Contact Data) for all search results is prohibitively expensive because:
1.  Many search results might be irrelevant, closed, or duplicates.
2.  Users would be paying for low-quality data.
3.  The cost of a "blind" Enterprise call is significantly higher than a basic validation call.

We need a strategy to filter candidates and verify their existence before enriching them with expensive contact data, ensuring detailed audit trails for billing.

## Decision

We will implement a **3-Stage Waterfall Pipeline** in the backend (`BatchProcessor`):

### Stage 1: Candidate Collection (Low Cost)
*   **Source:** Google Places API `Text Search (ID Only)`.
*   **Goal:** Create a broad pool of candidate Place IDs matching the query (e.g., "Architects in Ankara").
*   **Cost:** Free / Very Low (Text Search Essentials).
*   **Fields:** `places.id`, `places.name`.

### Stage 2: Verification (Medium Cost / Gatekeeper)
*   **Source:** Google Places API `Place Details (Pro)`.
*   **Goal:** Verify the place exists, get human-readable name and address.
*   **Cost:** Pro Tier (Moderate).
*   **Fields:** `displayName`, `formattedAddress`.
*   **Logic:** If the place returns 404 or fails validation rules (e.g., missing address), it is discarded here. We do not proceed to Stage 3 for these items.
*   **Circuit Breaker:** If >50% of items fail in this stage, the batch is aborted to prevent system-wide issues.

### Stage 3: Enrichment (High Cost / Value)
*   **Source:** Google Places API `Place Details (Enterprise / Contact Data)`.
*   **Goal:** Fetch high-value contact attributes.
*   **Cost:** Enterprise Tier (High).
*   **Fields:** `websiteUri`, `nationalPhoneNumber`.
*   **Logic:** Only called for items that successfully passed Stage 2.

## Consequences

### Positive
*   **Cost Efficiency:** We only pay the high price for "surviving" valid records.
*   **Data Quality:** Users receive lists where existence is verified.
*   **Transparency:** We can show users exactly how many candidates were found vs. how many were verified and enriched.
*   **Safety:** Guardrails (Hard limits, Circuit Breakers) prevent runaway costs.

### Negative
*   **Latency:** The pipeline is sequential, increasing total processing time per batch (mitigated by async Celery tasks).
*   **Complexity:** Requires state management (`COLLECTING_IDS` -> `FILTERING` -> `ENRICHING_CONTACTS`) and robust error handling for each stage.

## Technical Implementation

*   **Model:** `Batch` model tracks `ids_collected`, `ids_verified`, `contacts_enriched`.
*   **Status:** New statuses `PARTIAL` and `ABORTED` handle cases where the pipeline stops early.
*   **Billing:** Users are billed only for `contacts_enriched`.
