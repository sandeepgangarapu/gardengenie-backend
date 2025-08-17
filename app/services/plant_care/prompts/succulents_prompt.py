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
  "seedStartingMonth": null,
  "plantingMonth": "[Month(s) or range for outdoor/container planting; e.g., Apr–May after frost or anytime indoors]",
  "requirements": {{
    "sun": "[Full Sun OR Bright Light OR Partial Shade]",
    "water": "[Soak and dry method OR Minimal winter water OR Deep, infrequent]",
    "soil": "[Cactus/succulent mix OR Sandy, well-draining OR Fast-draining]",
    "drainage": "[Excellent drainage critical OR Good drainage OR Tolerates brief moisture]",
    "temperature": "[Cold tolerance or minimum temperature]",
    "humidity": "[Low humidity preferred OR Tolerates humidity OR Avoid high humidity]",
    "hardiness": "[Cold hardiness description]"
  }},
  "seed_starting": [],
  "planting": [
    {{
      "step": "[Specific succulent planting action]",
      "tip": "[Helpful hint about soil mix, container choice, etc.]"
    }}
  ],
  "care_plan": {{
    "must_do": [
      {{ "text": "[Essential watering and seasonal care]", "when": "[Season-appropriate timing]" }}
    ],
    "good_to_do": [
      {{ "text": "[Beneficial maintenance tasks]", "when": "[Optimal timing for task]" }}
    ],
    "optional": []
  }}
}}
```

**CRUCIAL ZONE-SPECIFIC INSTRUCTIONS:**
• Keep `requirements` values extremely concise (1–3 words or compact phrases). No sentences.
1. Address outdoor vs. container growing based on local hardiness conditions. Do not include the word "Zone" or phrases like "in Zone {user_zone}" anywhere (text, tips, when).
2. Provide specific winter protection needs for this climate
3. Organize tasks by priority rather than growth stage. Keep 1–8 total tasks across all priority levels
4. Each care_plan item has only: text, when (month/range or relative phrase). Tasks are organized into must_do (essential), good_to_do (recommended), and optional arrays.
5. Address humidity challenges specific to the region and propagation timing
"""