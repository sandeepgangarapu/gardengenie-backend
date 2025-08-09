BULBS_PROMPT = """
Act as a Zone-Aware Master Gardener providing comprehensive bulb growing guidance.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate a detailed JSON response following this EXACT schema:**

```json
{{
  "plantName": "[Corrected Common Name]",
  "description": "[Brief description of the bulb and its blooms]",
  "type": "Perennial",
  "seasonality": "[Spring-blooming OR Summer-blooming OR Fall-blooming]",
  "zoneSuitability": "[match OR close OR far]",
  "typeSpecific": {{
    "bulbType": "[True bulb OR Corm OR Tuber OR Rhizome]"
  }},
  "requirements": {{
    "sun": "[Full Sun OR Partial Shade OR Full Shade]",
    "water": "[During growing season only OR Minimal after dormancy OR Consistent spring moisture]",
    "soil": "[Well-draining, fertile OR Sandy, well-draining OR Rich but draining]",
    "drainage": "[Excellent drainage required OR Good drainage OR Tolerates some moisture]",
    "chilling": "[Requires cold treatment OR Pre-chilled OR Natural winter chill]",
    "plantingDepth": "[3x bulb height OR Specific depth requirement]"
  }},
  "seed_starting": [],
  "planting": [
    {{
      "step": "[Specific bulb planting action]",
      "tip": "[Helpful hint about bulb orientation, depth, etc.]"
    }}
  ],
  "care_plan": {{
    "style": "lifecycle",
    "tabs": [
      {{
        "key": "grow",
        "label": "Grow",
        "items": [
          {{ "text": "[Support spring growth with water and light feeding]", "when": "[Mar–May]", "priority": "good to do" }}
        ]
      }},
      {{
        "key": "post_bloom",
        "label": "Post‑Bloom",
        "items": [
          {{ "text": "[Deadhead; allow foliage to die back naturally]", "when": "[6–8 weeks after bloom]", "priority": "must do" }}
        ]
      }}
    ]
  }}
}}
```

**CRUCIAL ZONE-SPECIFIC INSTRUCTIONS:**
1. Provide exact planting timing for Zone {user_zone} based on soil temperature and frost dates
2. Keep planting guidance in the planting section; care_plan should only cover Grow and Post‑Bloom (post‑plant tasks). Keep 1–3 items per tab
3. Each item is only: text, when (month/range or relative phrase), priority (must do|good to do|optional). If a step should be explicitly skipped, use priority "skip".
4. Include pre-chilling requirements if needed for this zone
5. Address zone-specific challenges (drainage in clay soil, heat tolerance, etc.)
6. Specify naturalization potential and suitable companions
"""