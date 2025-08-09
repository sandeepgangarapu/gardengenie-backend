EDIBLE_PLANTS_PROMPT = """
Act as a Zone-Aware Master Gardener providing comprehensive growing guidance for edible plants.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate a detailed JSON response following this EXACT schema:**

```json
{{
  "plantName": "[Corrected Common Name]",
  "description": "[Brief description of the edible plant, its uses, and expected yields]",
  "type": "Annual",
  "seasonality": "[Cool Season OR Warm Season]",
  "zoneSuitability": "[match OR close OR far]",
  "seedStartingMonth": "[Month(s) or range for starting seeds; use local frost dates, e.g., Feb–Mar indoors]",
  "plantingMonth": "[Month(s) or range for transplanting/direct sowing; e.g., Apr–May after last frost]",
  "typeSpecific": {{
    "daysToMaturity": "[e.g., 60-80 days OR 45 days to first harvest]"
  }},
  "requirements": {{
    "sun": "[Full Sun OR Partial Shade OR Full Shade]",
    "water": "[Deep weekly OR Consistent moisture OR Moderate]",
    "soil": "[Well-draining, fertile OR Sandy loam OR Rich, organic]",
    "pH": "[6.0-7.0 OR 6.5-7.5 OR Specific range]",
    "spacing": "[Plant spacing requirements - e.g., 12-18 inches apart]",
    "companions": ["[Beneficial companion plants]"],
    "avoid": ["[Plants to avoid nearby]"]
  }},
  "seed_starting": [
    {{
      "step": "[Specific seed starting action]",
      "tip": "[Helpful hint or technique]"
    }}
  ],
  "planting": [
    {{
      "step": "[Specific planting action]",
      "tip": "[Helpful hint or technique]"
    }}
  ],
  "care_plan": {{
    "style": "lifecycle",
    "tabs": [
      {{
        "key": "grow",
        "label": "Grow",
        "items": [
          {{ "text": "[Water consistently; mulch; side-dress or feed as appropriate]", "when": "[During active growth, e.g., May–August]", "priority": "must do" }},
          {{ "text": "[Succession sow every 2–3 weeks for continuous harvest]", "when": "[Every 2–3 weeks until ~8 weeks before first frost]", "priority": "good to do" }}
        ]
      }},
      {{
        "key": "harvest",
        "label": "Harvest",
        "items": [
          {{ "text": "[Harvest at maturity using crop-specific indicators]", "when": "[e.g., Jun–Sep]", "priority": "must do" }},
          {{ "text": "[Handle and store properly for best shelf life]", "when": "[Immediately after harvest]", "priority": "good to do" }}
        ]
      }},
      {{
        "key": "end",
        "label": "End",
        "items": [
          {{ "text": "[Remove spent plants; compost debris; prep beds for next crop]", "when": "[After final harvest or first frost]", "priority": "good to do" }}
        ]
      }}
    ]
  }}
}}
```

**CRUCIAL ZONE-SPECIFIC INSTRUCTIONS:**
1. All "when" values should use local frost dates and season length. Do not include the word "Zone" or phrases like "in Zone {user_zone}" anywhere (text, tips, when).
2. Provide concise summary fields: seedStartingMonth and plantingMonth (month names/ranges only, no "Zone" wording). Keep seed starting and planting details in their dedicated sections; care_plan should only cover Grow, Harvest, End (post‑plant tasks)
3. Each item is only: text, when (month/range or relative phrase), priority (must do|good to do|optional). If a step should be explicitly skipped, use priority "skip".
4. Include succession planting guidance in Grow; pest/disease monitoring where relevant
5. Include companion planting recommendations and plants to avoid
6. Add expected yields and days to maturity information
7. Address soil preparation needs specific to the region
"""