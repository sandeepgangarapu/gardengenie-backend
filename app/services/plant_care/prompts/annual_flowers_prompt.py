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
  "daysToBloom": "[e.g., 60-80 days OR 45 days to first flowers]",
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
  "care_plan": [
    {{
      "task": "[Establishment care]",
      "description": "[Care during first 2-4 weeks after planting]",
      "priority": "critical",
      "timing": {{
        "type": "relative",
        "start": "planting",
        "duration": "2-4 weeks"
      }},
      "frequency": "Daily monitoring",
      "tips": "[Zone-specific establishment guidance]"
    }},
    {{
      "task": "[Blooming season care]",
      "description": "[Care during main blooming period - watering, feeding, support]",
      "priority": "important",
      "timing": {{
        "type": "seasonal",
        "season": "growing_season",
        "months": ["May", "June", "July", "August", "September"]
      }},
      "frequency": "Weekly care",
      "tips": "[Heat and humidity management]"
    }},
    {{
      "task": "[Deadheading and maintenance]",
      "description": "[Deadheading techniques for continued blooms, pinching, support]",
      "priority": "important",
      "timing": {{
        "type": "recurring",
        "frequency": "weekly",
        "during": "bloom_period"
      }},
      "frequency": "Weekly during bloom",
      "tips": "[Specific deadheading techniques for this flower]"
    }},
    {{
      "task": "[End of season care]",
      "description": "[Seed collection, cleanup, composting]",
      "priority": "beneficial",
      "timing": {{
        "type": "seasonal",
        "season": "fall",
        "trigger": "after_first_frost"
      }},
      "frequency": "End of season",
      "tips": "[Seed saving techniques if applicable]"
    }}
  ]
}}
```

**CRUCIAL ZONE-SPECIFIC INSTRUCTIONS:**
1. All timing must be specific to Zone {user_zone} - use local frost dates and growing season
2. Focus on the complete growing cycle from seed to end of season
3. Provide specific timing for seed starting and planting for this zone
4. Include succession planting advice if applicable for extended blooms
5. Cover deadheading techniques for continued flower production
6. Address zone-specific challenges (heat, humidity, short seasons)
7. Include seed collection and saving tips if relevant to the variety
"""