ORNAMENTAL_PERENNIALS_PROMPT = """
Act as a Zone-Aware Master Gardener providing comprehensive ornamental perennial growing guidance.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate a detailed JSON response following this EXACT schema:**

```json
{{
  "plantName": "[Corrected Common Name]",
  "description": "[Brief description of the ornamental plant and its features]",
  "type": "Perennial",
  "seasonality": null,
  "zoneSuitability": "[match OR close OR far]",
  "seedStartingMonth": null,
  "plantingMonth": "[Month(s) or range for planting/division; e.g., Apr–May or Sep–Oct]",
  "requirements": {{
    "sun": "[Full Sun OR Partial Shade OR Full Shade]",
    "water": "[Deep weekly OR Consistent moisture OR Drought tolerant]",
    "soil": "[Well-draining, fertile OR Sandy loam OR Rich, organic]",
    "ph": "[6.0-7.0 OR 6.5-7.5 OR Specific range]",
    "spacing": "[Plant spacing requirements - e.g., 18-24 inches apart]",
    "rowSpacing": "[Row spacing distance - e.g., 24-30 inches apart OR N/A for naturalized planting]",
    "bloomTime": "[Spring OR Summer OR Fall OR Multiple seasons]",
    "matureSize": "[Height x Width - e.g., 2-3 feet tall, 2 feet wide]"
  }},
  "seed_starting": [],
  "planting": [
    {{
      "step": "[Specific perennial planting action]",
      "tip": "[Helpful hint about soil preparation, depth, spacing, etc.]"
    }}
  ],
  "care_plan": {{
    "must_do": [
      {{ "text": "[Essential seasonal care tasks]", "when": "[Season-appropriate timing]" }}
    ],
    "good_to_do": [
      {{ "text": "[Beneficial maintenance for plant health]", "when": "[Optimal timing]" }}
    ],
    "optional": []
  }}
}}
```

**CRUCIAL ZONE-SPECIFIC INSTRUCTIONS:**
• Keep `requirements` values extremely concise (1–3 words or compact ranges like "18–24 in"). No sentences.
1. All "when" values must be tied to local climate patterns. Do not include the word "Zone" or phrases like "in Zone {user_zone}" anywhere (text, tips, when).
2. Organize tasks by priority rather than season. Keep 1–8 total tasks across all priority levels
3. Each care_plan item has only: text, when (month/range or relative phrase). Tasks are organized into must_do (essential), good_to_do (recommended), and optional arrays.
4. Cover bloom care, pruning, deadheading, and division timing
5. Address both establishment (first year) and ongoing maintenance
6. Include zone-specific challenges (heat, cold, humidity, pests)
7. Provide division and propagation timing appropriate for the region
"""