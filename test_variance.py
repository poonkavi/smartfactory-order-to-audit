from app.services.costing_service import calculate_production_variance


standard_materials = {
    "Flour": 40,
    "Oil": 10,
    "Spice Mix": 1.2,
    "Pouches": 200,
    "Cartons": 10
}

actual_materials = {
    "Flour": 40,
    "Oil": 10.5,
    "Spice Mix": 1.2,
    "Pouches": 194,
    "Cartons": 9
}

result = calculate_production_variance(
    planned_output=200,
    actual_output=188,
    standard_materials=standard_materials,
    actual_materials=actual_materials
)

print("Production Yield:", result["yield_percentage"], "%")
print("Yield Variance:", result["yield_variance_percentage"], "%")

print("\nMaterial Variance Report\n")

for material, data in result["material_variances"].items():

    print(material)
    print("  Standard:", data["standard"])
    print("  Actual:", data["actual"])
    print("  Variance:", data["variance"])
    print("  Variance %:", data["variance_percentage"], "%")
    print()