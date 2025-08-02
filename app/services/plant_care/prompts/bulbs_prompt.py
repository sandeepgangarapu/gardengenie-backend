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
  "bulbType": "[True bulb OR Corm OR Tuber OR Rhizome]",
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
  "care_plan": [
    {{
      "task": "[Planting preparation]",
      "description": "[Detailed bulb planting instructions]",
      "priority": "critical",
      "timing": {{
        "type": "seasonal",
        "season": "fall",
        "months": ["October", "November"],
        "zone_adjustment": "Plant 6-8 weeks before ground freezes in Zone {user_zone}"
      }},
      "frequency": "Annual",
      "tips": "[Zone-specific planting timing]"
    }},
    {{
      "task": "[Spring emergence care]",
      "description": "[Care during active growth period]",
      "priority": "important",
      "timing": {{
        "type": "seasonal",
        "season": "spring",
        "months": ["March", "April", "May"]
      }},
      "frequency": "Weekly monitoring",
      "tips": "[Fertilizing and watering guidance]"
    }},
    {{
      "task": "[Post-bloom care]",
      "description": "[Deadheading and foliage management]",
      "priority": "critical",
      "timing": {{
        "type": "relative",
        "start": "bloom_end",
        "duration": "6-8 weeks"
      }},
      "frequency": "Allow natural dormancy",
      "tips": "[Importance of leaving foliage to die back naturally]"
    }}
  ]
}}
```

**CRUCIAL ZONE-SPECIFIC INSTRUCTIONS:**
1. Provide exact planting timing for Zone {user_zone} based on soil temperature and frost dates
2. Include pre-chilling requirements if needed for this zone
3. Address any zone-specific challenges (drainage in clay soil, heat tolerance, etc.)
4. Specify naturalization potential in this climate
5. Include companion planting with other bulbs or perennials
"""