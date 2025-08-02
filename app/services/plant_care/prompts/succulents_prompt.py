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
  "hardiness": "[Hardy to Zone X OR Tender, container only OR Cold-sensitive]",
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
  "care_plan": [
    {{
      "task": "[Growing season care]",
      "description": "[Active growing period watering and feeding]",
      "priority": "important",
      "timing": {{
        "type": "seasonal",
        "season": "spring_summer",
        "months": ["April", "May", "June", "July", "August", "September"]
      }},
      "frequency": "When soil completely dry",
      "tips": "[Zone-specific watering timing based on climate]"
    }},
    {{
      "task": "[Winter dormancy care]",
      "description": "[Reduced water and protection from cold]",
      "priority": "critical",
      "timing": {{
        "type": "seasonal",
        "season": "winter",
        "months": ["November", "December", "January", "February", "March"]
      }},
      "frequency": "Monthly or less",
      "tips": "[Zone-specific winter protection needs]"
    }},
    {{
      "task": "[Repotting and propagation]",
      "description": "[When and how to repot, propagation methods]",
      "priority": "beneficial",
      "timing": {{
        "type": "recurring",
        "interval": "2-3 years",
        "best_season": "spring"
      }},
      "frequency": "Every 2-3 years",
      "tips": "[Propagation techniques specific to this succulent]"
    }}
  ]
}}
```

**CRUCIAL ZONE-SPECIFIC INSTRUCTIONS:**
1. Address outdoor vs. container growing based on Zone {user_zone} hardiness
2. Provide specific winter protection needs for this climate
3. Include seasonal watering adjustments based on local climate patterns
4. Address humidity challenges specific to the region
5. Include propagation timing appropriate for the local growing season
"""