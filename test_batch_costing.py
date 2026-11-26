from app.services.costing_service import calculate_batch_cost

result = calculate_batch_cost()

print("BATCH COSTING REPORT")
print("-" * 35)

print("Flour rate:", result["flour_rate"])
print("Flour cost: Rs.", result["flour_cost"])
print("Oil cost: Rs.", result["oil_cost"])
print("Spice cost: Rs.", result["spice_cost"])
print("Pouch cost: Rs.", result["pouch_cost"])
print("Carton cost: Rs.", result["carton_cost"])

print("\nTotal material cost: Rs.", result["material_cost"])
print("Labour cost: Rs.", result["labour_cost"])
print("Gas and power cost: Rs.", result["power_cost"])

print("\nTotal batch cost: Rs.", result["total_batch_cost"])
print("Good packets:", result["good_packets"])
print("Cost per good packet: Rs.", result["cost_per_packet"])