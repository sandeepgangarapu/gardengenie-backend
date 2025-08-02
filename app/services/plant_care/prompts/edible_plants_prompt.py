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
  "daysToMaturity": "[e.g., 60-80 days OR 45 days to first harvest]",
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
  "care_plan": [
    {{
      "task": "[Specific care task - e.g., 'Establish seedlings']",
      "description": "[Detailed explanation of the task and techniques]",
      "priority": "[critical OR important OR beneficial]",
      "timing": {{
        "type": "relative",
        "start": "planting",
        "duration": "2-4 weeks"
      }},
      "frequency": "Daily monitoring",
      "tips": "[Zone-specific advice or warnings]"
    }},
    {{
      "task": "[Another task - e.g., 'Succession planting']",
      "description": "[Detailed explanation]",
      "priority": "[critical OR important OR beneficial]",
      "timing": {{
        "type": "recurring",
        "interval": "2-3 weeks",
        "season_end": "8 weeks before first frost"
      }},
      "frequency": "Every 2-3 weeks",
      "tips": "[Zone-specific timing advice]"
    }},
    {{
      "task": "[Harvest task]",
      "description": "[Harvesting techniques and timing indicators]",
      "priority": "critical",
      "timing": {{
        "type": "maturity",
        "indicators": ["Size reached", "Color change", "Texture signs"]
      }},
      "frequency": "As ready",
      "tips": "[Storage and post-harvest handling]"
    }}
  ]
}}
```

**CRUCIAL ZONE-SPECIFIC INSTRUCTIONS:**
1. All timing must be specific to Zone {user_zone} - use local frost dates, growing season length
2. Create comprehensive, multi-step care_plan with distinct task objects
3. Include zone-specific challenges (heat, humidity, pests common to the region)
4. Provide exact timing for seed starting, planting, and succession planting for this zone
5. Include companion planting recommendations and plants to avoid
6. Add expected yields and days to maturity information
7. Address soil preparation needs specific to the region
8. Include integrated pest management appropriate for edible crops
"""