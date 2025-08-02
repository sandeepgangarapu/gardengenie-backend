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
  "requirements": {{
    "sun": "[Full Sun OR Partial Shade OR Full Shade]",
    "water": "[Deep weekly OR Consistent moisture OR Drought tolerant]",
    "soil": "[Well-draining, fertile OR Sandy loam OR Rich, organic]",
    "pH": "[6.0-7.0 OR 6.5-7.5 OR Specific range]",
    "spacing": "[Plant spacing requirements - e.g., 18-24 inches apart]",
    "bloom_time": "[Spring OR Summer OR Fall OR Multiple seasons]",
    "mature_size": "[Height x Width - e.g., 2-3 feet tall, 2 feet wide]"
  }},
  "seed_starting": [],
  "planting": [
    {{
      "step": "[Specific perennial planting action]",
      "tip": "[Helpful hint about soil preparation, depth, spacing, etc.]"
    }}
  ],
  "care_plan": [
    {{
      "task": "[Spring care tasks]",
      "description": "[Spring pruning, fertilizing, emergence care, mulching]",
      "priority": "[critical OR important OR beneficial]",
      "timing": {{
        "type": "seasonal",
        "season": "spring",
        "months": ["March", "April", "May"]
      }},
      "frequency": "Annual spring tasks",
      "tips": "[Zone-specific spring care timing]"
    }},
    {{
      "task": "[Summer care tasks]",
      "description": "[Watering, deadheading, pest monitoring, summer pruning]",
      "priority": "[critical OR important OR beneficial]",
      "timing": {{
        "type": "seasonal",
        "season": "summer",
        "months": ["June", "July", "August"]
      }},
      "frequency": "Weekly to monthly",
      "tips": "[Heat and drought management for the zone]"
    }},
    {{
      "task": "[Fall care tasks]",
      "description": "[Cleanup, division, transplanting, winter preparation]",
      "priority": "[critical OR important OR beneficial]",
      "timing": {{
        "type": "seasonal",
        "season": "fall",
        "months": ["September", "October", "November"]
      }},
      "frequency": "Annual fall tasks",
      "tips": "[Zone-specific winter preparation]"
    }},
    {{
      "task": "[Winter care tasks]",
      "description": "[Protection, dormant care, planning for next season]",
      "priority": "[critical OR important OR beneficial]",
      "timing": {{
        "type": "seasonal",
        "season": "winter",
        "months": ["December", "January", "February"]
      }},
      "frequency": "Minimal winter care",
      "tips": "[Zone-specific winter protection needs]"
    }}
  ]
}}
```

**CRUCIAL ZONE-SPECIFIC INSTRUCTIONS:**
1. All timing must be specific to Zone {user_zone} - adjust for local climate patterns
2. Focus on long-term perennial care and maintenance through seasons
3. Include pruning guidance specific to the plant type and bloom timing
4. Cover seasonal bloom care, deadheading, and division timing
5. Address both establishment (first year) and ongoing maintenance
6. Include zone-specific challenges (heat, cold, humidity, pests)
7. Provide division and propagation timing appropriate for the region
"""