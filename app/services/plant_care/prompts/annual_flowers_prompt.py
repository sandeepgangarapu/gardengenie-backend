ANNUAL_FLOWERS_PROMPT = """
Act as a Zone-Aware Master Gardener providing comprehensive annual flower growing guidance.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate a detailed JSON response following this EXACT schema:**

```json
{{
  "plantName": "[Corrected Common Name]",
  "description": "[Brief description of the annual flower and its characteristics]",
  "type": "Annual",
  "seasonality": "[Cool Season OR Warm Season]",
  "zoneSuitability": "[match OR close OR far]",
  "typeSpecific": {{
    "daysToBloom": "[e.g., 60-80 days OR 45 days to first flowers]"
  }},
  "requirements": {{
    "sun": "[Full Sun OR Partial Shade OR Full Shade]",
    "water": "[Deep weekly OR Consistent moisture OR Moderate]",
    "soil": "[Well-draining, fertile OR Sandy loam OR Rich, organic]",
    "pH": "[6.0-7.0 OR 6.5-7.5 OR Specific range]",
    "spacing": "[Plant spacing requirements - e.g., 8-12 inches apart]",
    "companions": ["[Beneficial companion plants]"],
    "bloom_period": "[Spring through frost OR Summer months OR Specific season]"
  }},
  "seed_starting": [
    {{
      "step": "[Specific seed starting action]",
      "tip": "[Helpful hint about germination, light requirements, etc.]"
    }}
  ],
  "planting": [
    {{
      "step": "[Specific planting action]",
      "tip": "[Helpful hint about transplanting, direct seeding, etc.]"
    }}
  ],
  "care_plan": {{
    "style": "lifecycle",
    "tabs": [
      {{
        "key": "grow_bloom",
        "label": "Grow/Bloom",
        "items": [
          {{ "text": "[Water consistently and feed during bloom; stake/tie as needed]", "when": "[May–September in Zone {user_zone}]", "priority": "must do" }},
          {{ "text": "[Deadhead spent flowers to extend blooming]", "when": "[Weekly during bloom]", "priority": "good to do" }}
        ]
      }},
      {{
        "key": "end",
        "label": "End",
        "items": [
          {{ "text": "[Collect seeds and remove plants after first frost]", "when": "[After first frost in Zone {user_zone}]", "priority": "good to do" }}
        ]
      }}
    ]
  }}
}}
```

**CRUCIAL ZONE-SPECIFIC INSTRUCTIONS:**
1. All timing must be specific to Zone {user_zone} - use local frost dates and growing season
2. Keep seed starting and planting in their dedicated sections; care_plan should only contain post-plant lifecycle tasks (Grow/Bloom, End)
3. Include succession planting advice in care_plan only if it affects in‑season management
4. Cover deadheading techniques for continued flower production
5. Address zone-specific challenges (heat, humidity, short seasons)
6. Include seed collection and saving tips if relevant to the variety
"""