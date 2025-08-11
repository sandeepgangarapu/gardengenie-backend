HOUSEPLANTS_PROMPT = """
Act as a Zone-Aware Master Gardener providing comprehensive indoor houseplant care guidance.

**Input Information:**
*   **Plant Name:** {plant_name}

**Generate a detailed JSON response following this EXACT schema:**

```json
{
  "plantName": "[Corrected Common Name]",
  "description": "[Brief description of the houseplant and its characteristics]",
  "type": "Houseplant",
  "seasonality": null,
  "zoneSuitability": null,
  "seedStartingMonth": null,
  "plantingMonth": null,
  "requirements": {
    "sun": "[Bright indirect OR Medium light OR Low light]",
    "water": "[Allow top inch to dry OR Keep evenly moist OR Dry between waterings]",
    "soil": "[Well-draining potting mix OR Aroid mix OR Cactus mix]",
    "humidity": "[Average home humidity OK OR Needs higher humidity]",
    "temperature": "[Typical indoor range OR Avoid below 55F]",
    "lightPreference": "[Bright indirect OR Low light tolerant OR Direct sun tolerant]"
  },
  "seed_starting": [],
  "planting": [
    {
      "step": "[Repotting or initial potting guidance]",
      "tip": "[Container size, drainage, acclimation tips]"
    }
  ],
  "care_plan": {
    "style": "indoor",
    "tabs": [
      {
        "key": "year_round",
        "label": "Year‑Round",
        "items": [
          { "text": "[Water based on medium dryness; adjust by season]", "when": "[Check weekly; less in winter]", "priority": "must do" },
          { "text": "[Fertilize during active growth]", "when": "[Monthly in spring/summer]", "priority": "good to do" }
        ]
      },
      {
        "key": "winter",
        "label": "Winter",
        "items": [
          { "text": "[Reduce watering; increase light exposure if possible]", "when": "[Nov–Feb]", "priority": "good to do" }
        ]
      }
    ]
  }
}
```

**CRUCIAL INSTRUCTIONS:**
• Keep `requirements` values extremely concise (1–3 words or compact ranges). No sentences.
1. Do not include the word "Zone" anywhere. Tailor advice to typical indoor conditions.
2. Use indoor tabs (Year‑Round, Winter). Keep 1–3 concise items per tab (max 8 total)
3. Each item is only: text, when (month/range or relative phrase), priority (must do|good to do|optional). If a step should be explicitly skipped, use priority "skip".
"""

HOUSEPLANTS_PROMPT = """
Act as a Zone-Aware Master Gardener providing comprehensive indoor plant care guidance.

**Plant Name:** {plant_name}
**Context:** Indoor houseplant care with seasonal awareness

**Generate a detailed JSON response following this EXACT schema:**

```json
{{
  "plantName": "[Corrected Common Name]",
  "description": "[Brief description of the houseplant and its characteristics]",
  "type": "[Annual OR Perennial]",
  "seasonality": null,
  "zoneSuitability": null,
  "requirements": {{
    "sun": "[Bright Light OR Medium Light OR Low Light]",
    "water": "[Deep weekly OR Light frequent OR Allow to dry between waterings]",
    "humidity": "[High (60%+) OR Medium (40-60%) OR Low (30-40%)]",
    "temperature": "[65-75°F OR 60-70°F OR 70-80°F]",
    "soil": "[Well-draining potting mix OR Succulent mix OR Specific requirements]",
    "fertilizer": "[Monthly liquid OR Slow-release OR Minimal]"
  }},
  "seed_starting": [],
  "planting": [],
  "care_plan": {{
    "style": "indoor",
    "tabs": [
      {{
        "key": "year_round",
        "label": "Year‑round",
        "items": [
          {{ "text": "[Water when top 1–2 inches are dry; ensure drainage]", "when": "[Anytime]", "priority": "must do" }},
          {{ "text": "[Monitor pests; clean leaves; rotate for even light]", "when": "[Monthly]", "priority": "good to do" }}
        ]
      }},
      {{
        "key": "summer",
        "label": "Summer",
        "items": [
          {{ "text": "[Increase watering/humidity if hot or dry]", "when": "[Jun–Aug]", "priority": "good to do" }}
        ]
      }},
      {{
        "key": "winter",
        "label": "Winter",
        "items": [
          {{ "text": "[Reduce watering; keep away from cold drafts]", "when": "[Dec–Feb]", "priority": "must do" }}
        ]
      }}
    ]
  }}
}}
```

**CRUCIAL INSTRUCTIONS:**
• Keep `requirements` values extremely concise (1–3 words or compact phrases). No sentences.
1. Provide care_plan with tabs (Year‑round, Summer, Winter). Keep 1–3 concise items per tab (max 8 total)
2. Each item has: text (what to do), when (month/range or "Anytime"), priority (must do|good to do|optional). If a step should be explicitly skipped, use priority "skip".
3. Include tasks for watering, fertilizing, repotting, pest monitoring, pruning, humidity
4. Fold any tips into the text; do not create nested timing objects
5. Include practical tips for apartment/home growing conditions
6. Address common indoor plant challenges specific to this species
"""