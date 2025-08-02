PLANT_CLASSIFICATION_PROMPT = """
Classify the plant "{plant_name}" to determine the most appropriate care instruction format.

Respond with ONLY a JSON object in this exact format:

{{
  "plant_group": "Vegetables" OR "Herbs" OR "Fruit Trees" OR "Flowering Shrubs" OR "Perennial Flowers" OR "Annual Flowers" OR "Ornamental Trees" OR "Houseplants" OR "Succulents" OR "Bulbs" OR "Native Plants"
}}

Classification Guidelines:
- **Vegetables**: Annual edible plants grown for food (tomatoes, lettuce, peppers, carrots, etc.)
- **Herbs**: Annual and perennial plants grown for culinary or medicinal use (basil, rosemary, mint, etc.)
- **Fruit Trees**: Long-term fruit-producing trees and shrubs (apple, citrus, berry bushes, etc.)
- **Flowering Shrubs**: Perennial woody ornamental plants (roses, hydrangeas, azaleas, etc.)
- **Perennial Flowers**: Long-term flowering plants (hostas, daylilies, peonies, etc.)
- **Annual Flowers**: Single-season flowering plants (marigolds, petunias, impatiens, etc.)
- **Ornamental Trees**: Non-fruit bearing trees for landscaping (maples, oaks, dogwoods, etc.)
- **Houseplants**: Plants typically grown indoors (fiddle leaf fig, pothos, etc.)
- **Succulents**: Water-storing plants including cacti (echeveria, jade plants, aloe, etc.)
- **Bulbs**: Underground storage organs with seasonal cycles (tulips, daffodils, gladiolus, etc.)
- **Native Plants**: Plants indigenous to specific regions (varies by location)

Plant: {plant_name}
Response:"""