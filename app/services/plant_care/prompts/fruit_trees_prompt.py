FRUIT_TREES_PROMPT = """
Act as a Zone-Aware Master Gardener providing comprehensive fruit tree growing guidance.

**Input Information:**
*   **Plant Name:** {plant_name}
*   **User USDA Hardiness Zone:** {user_zone}
*   **Plant Group:** {plant_group}

**Generate a detailed JSON response following this EXACT schema:**

```json
{{
  "plantName": "[Corrected Common Name]",
  "description": "[Brief description of the fruit tree and its fruit]",
  "type": "Perennial",
  "seasonality": null,
  "zoneSuitability": "[match OR close OR far]",
  "requirements": {{
    "sun": "[Full Sun OR Partial Shade OR Full Shade]",
    "water": "[Deep weekly OR Consistent moisture OR Moderate]",
    "soil": "[Well-draining, fertile OR Sandy loam OR Rich, organic]",
    "pH": "[6.0-7.0 OR 6.5-7.5 OR Specific range]",
    "spacing": "[Tree spacing requirements - e.g., 15-20 feet apart]",
    "pollination": "[Self-fertile OR Needs pollinator OR Cross-pollination helpful]",
    "rootstock": "[Standard OR Semi-dwarf OR Dwarf OR Variety-specific]"
  }},
  "seed_starting": [],
  "planting": [
    {{
      "step": "[Specific tree planting action]",
      "tip": "[Helpful hint about hole preparation, root handling, etc.]"
    }}
  ],
  "care_plan": [
    {{
      "task": "[Establishment care]",
      "description": "[Care during first 1-3 years - root development, structural pruning, protection, consistent watering]",
      "priority": "critical",
      "timing": {{
        "type": "relative",
        "start": "planting",
        "duration": "first 3 years"
      }},
      "frequency": "Ongoing during establishment",
      "tips": "[Zone-specific establishment guidance]"
    }},
    {{
      "task": "[Growing season care]",
      "description": "[Active season care - watering, fertilizing, pest monitoring, summer pruning]",
      "priority": "important",
      "timing": {{
        "type": "seasonal",
        "season": "spring_summer",
        "months": ["March", "April", "May", "June", "July", "August"]
      }},
      "frequency": "Monthly monitoring",
      "tips": "[Zone-specific growing season advice]"
    }},
    {{
      "task": "[Fruit production and harvest]",
      "description": "[Fruit thinning, harvest timing, post-harvest care]",
      "priority": "critical",
      "timing": {{
        "type": "maturity",
        "indicators": ["Fruit color", "Fruit size", "Easy separation from branch"]
      }},
      "frequency": "During harvest season",
      "tips": "[Storage and handling techniques]"
    }},
    {{
      "task": "[Dormant season maintenance]",
      "description": "[Dormant pruning, winter protection, annual fertilizing, disease prevention]",
      "priority": "important",
      "timing": {{
        "type": "seasonal",
        "season": "winter",
        "months": ["December", "January", "February"]
      }},
      "frequency": "Annual",
      "tips": "[Zone-specific winter care and pruning timing]"
    }}
  ]
}}
```

**CRUCIAL ZONE-SPECIFIC INSTRUCTIONS:**
1. All timing must be specific to Zone {user_zone} - use local frost dates and growing season
2. Include pruning guidance specific to fruit trees at appropriate lifecycle stages
3. Address zone-specific challenges (cold hardiness, heat tolerance, disease pressure)
4. Provide exact planting timing for this zone (early spring or fall)
5. Include harvest timing and techniques specific to the fruit type
6. Address pollination requirements and compatible varieties for the region
7. Include integrated pest and disease management for fruit production
"""