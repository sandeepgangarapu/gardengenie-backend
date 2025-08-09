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
  "typeSpecific": {{}},
  "requirements": {{
    "light": "[Bright Light OR Medium Light OR Low Light]",
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
1. Provide care_plan with tabs (Year‑round, Summer, Winter). Keep 1–3 concise items per tab (max 8 total)
2. Each item has: text (what to do), when (month/range or "Anytime"), priority (must do|good to do|optional). If a step should be explicitly skipped, use priority "skip".
3. Include tasks for watering, fertilizing, repotting, pest monitoring, pruning, humidity
4. Fold any tips into the text; do not create nested timing objects
5. Include practical tips for apartment/home growing conditions
6. Address common indoor plant challenges specific to this species
"""