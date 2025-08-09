SUCCULENTS_PROMPT = """
Act as a Zone-Aware Master Gardener providing comprehensive succulent growing guidance.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate a detailed JSON response following this EXACT schema:**

```json
{{
  "plantName": "[Corrected Common Name]",
  "description": "[Brief description of the succulent and its characteristics]",
  "type": "Perennial",
  "seasonality": null,
  "zoneSuitability": "[match OR close OR far]",
  "typeSpecific": {{
    "hardiness": "[Hardy to Zone X OR Tender, container only OR Cold-sensitive]"
  }},
  "requirements": {{
    "sun": "[Full Sun OR Bright Light OR Partial Shade]",
    "water": "[Soak and dry method OR Minimal winter water OR Deep, infrequent]",
    "soil": "[Cactus/succulent mix OR Sandy, well-draining OR Fast-draining]",
    "drainage": "[Excellent drainage critical OR Good drainage OR Tolerates brief moisture]",
    "temperature": "[Cold hardy to XF OR Minimum 50F OR Heat tolerant]",
    "humidity": "[Low humidity preferred OR Tolerates humidity OR Avoid high humidity]"
  }},
  "seed_starting": [],
  "planting": [
    {{
      "step": "[Specific succulent planting action]",
      "tip": "[Helpful hint about soil mix, container choice, etc.]"
    }}
  ],
  "care_plan": {{
    "style": "lifecycle",
    "tabs": [
      {{
        "key": "grow",
        "label": "Grow",
        "items": [
          {{ "text": "[Water thoroughly then allow to dry; light feeding]", "when": "[Apr–Sep in Zone {user_zone}]", "priority": "must do" }}
        ]
      }},
      {{
        "key": "dormancy",
        "label": "Dormancy",
        "items": [
          {{ "text": "[Reduce water to monthly or less; protect from cold]", "when": "[Nov–Mar]", "priority": "must do" }}
        ]
      }},
      {{
        "key": "repot",
        "label": "Repot/Propagate",
        "items": [
          {{ "text": "[Repot every 2–3 years; propagate via cuttings or offsets]", "when": "[Best in spring]", "priority": "good to do" }}
        ]
      }}
    ]
  }}
}}
```

**CRUCIAL ZONE-SPECIFIC INSTRUCTIONS:**
1. Address outdoor vs. container growing based on Zone {user_zone} hardiness
2. Provide specific winter protection needs for this climate
3. Use lifecycle tabs (Grow, Dormancy, Repot/Propagate). Keep 1–3 concise items per tab (max 8 total)
4. Each item is only: text, when (month/range or relative phrase), priority (must do|good to do|optional). If a step should be explicitly skipped, use priority "skip".
5. Address humidity challenges specific to the region and propagation timing
"""