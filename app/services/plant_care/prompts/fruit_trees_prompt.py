FRUIT_TREES_PROMPT = """
Act as a Zone-Aware Master Gardener providing comprehensive fruit tree growing guidance.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate a detailed JSON response following this EXACT schema:**

```json
{{
  "plantName": "[Corrected Common Name]",
  "description": "[Brief description of the fruit tree and its fruit]",
  "type": "Perennial",
  "seasonality": null,
  "zoneSuitability": "[match OR close OR far]",
  "seedStartingMonth": null,
  "plantingMonth": "[Month(s) or range for planting; e.g., Mar–Apr for bare-root or Oct–Nov in mild climates]",
  "requirements": {{
    "sun": "[Full Sun OR Partial Shade OR Full Shade]",
    "water": "[Deep weekly OR Consistent moisture OR Moderate]",
    "soil": "[Well-draining, fertile OR Sandy loam OR Rich, organic]",
    "ph": "[6.0-7.0 OR 6.5-7.5 OR Specific range]",
    "spacing": "[Tree spacing requirements - e.g., 15-20 feet apart]",
    "pollination": "[Self-fertile OR Needs pollinator OR Cross-pollination helpful]",
    "rootstock": "[Standard OR Semi-dwarf OR Dwarf OR Variety-specific]"
  }},
  "seed_starting": [],
  "planting": [
    {{
      "step": "[Specific tree planting action]",
      "tip": "[Helpful hint about hole preparation, root handling, etc.]"
    }}
  ],
  "care_plan": {{
    "style": "seasons",
    "tabs": [
      {{
        "key": "spring",
        "label": "Spring",
        "items": [
          {{ "text": "[Fertilize and perform formative pruning; monitor pests]", "when": "[Mar–May]", "priority": "must do" }}
        ]
      }},
      {{
        "key": "summer",
        "label": "Summer",
        "items": [
          {{ "text": "[Water deeply, thin fruit if heavy set; manage pests/disease]", "when": "[Jun–Aug]", "priority": "must do" }}
        ]
      }},
      {{
        "key": "fall",
        "label": "Fall",
        "items": [
          {{ "text": "[Harvest at correct maturity; post-harvest sanitation]", "when": "[Based on variety window]", "priority": "must do" }}
        ]
      }},
      {{
        "key": "winter",
        "label": "Winter",
        "items": [
          {{ "text": "[Dormant pruning and winter protection where needed]", "when": "[Dec–Feb]", "priority": "good to do" }}
        ]
      }}
    ]
  }}
}}
```

**CRUCIAL ZONE-SPECIFIC INSTRUCTIONS:**
• Keep `requirements` values extremely concise (1–3 words or compact ranges like "15–20 ft"). No sentences.
1. All "when" values must reference local frost dates and growing season. Do not include the word "Zone" or phrases like "in Zone {user_zone}" anywhere (text, tips, when).
2. Use seasonal tabs (Spring, Summer, Fall, Winter). Keep 1–3 concise items per tab (max 8 total)
3. Each item is only: text, when (month/range or relative phrase), priority (must do|good to do|optional). If a step should be explicitly skipped, use priority "skip".
4. Include pruning guidance, harvest timing, and storage techniques for the fruit type
5. Address pollination requirements and compatible varieties for the region
6. Include integrated pest and disease management for fruit production
"""