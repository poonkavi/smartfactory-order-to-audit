from decimal import Decimal


def calculate_production_variance(
    planned_output,
    actual_output,
    standard_materials,
    actual_materials
):
    planned_output = Decimal(str(planned_output))
    actual_output = Decimal(str(actual_output))

    yield_percentage = (
        actual_output / planned_output
    ) * Decimal("100")

    yield_variance_percentage = (
        yield_percentage - Decimal("100")
    )

    material_variances = {}

    for material, standard_quantity in standard_materials.items():

        standard_quantity = Decimal(str(standard_quantity))

        actual_quantity = Decimal(
            str(actual_materials.get(material, 0))
        )

        variance_quantity = (
            actual_quantity - standard_quantity
        )

        if standard_quantity != 0:
            variance_percentage = (
                variance_quantity / standard_quantity
            ) * Decimal("100"
            )
        else:
            variance_percentage = Decimal("0")

        material_variances[material] = {
            "standard": standard_quantity,
            "actual": actual_quantity,
            "variance": variance_quantity,
            "variance_percentage": variance_percentage
        }

    return {
        "yield_percentage": yield_percentage,
        "yield_variance_percentage": yield_variance_percentage,
        "material_variances": material_variances
    }


def calculate_batch_cost():

    # Weighted-average flour rate
    opening_flour_qty = Decimal("100")
    opening_flour_rate = Decimal("42")

    purchased_flour_qty = Decimal("60")
    purchase_flour_rate = Decimal("45")

    flour_rate = (
        (opening_flour_qty * opening_flour_rate)
        + (purchased_flour_qty * purchase_flour_rate)
    ) / (opening_flour_qty + purchased_flour_qty)

    # Material costs
    flour_cost = Decimal("40") * flour_rate
    oil_cost = Decimal("10.5") * Decimal("140")
    spice_cost = Decimal("1.2") * Decimal("200")

    pouch_cost = Decimal("194") * Decimal("2.50")
    carton_cost = Decimal("9") * Decimal("15")

    # Labour and utilities
    labour_cost = Decimal("1200")
    power_cost = Decimal("600")

    total_material_cost = (
        flour_cost
        + oil_cost
        + spice_cost
        + pouch_cost
        + carton_cost
    )

    total_batch_cost = (
        total_material_cost
        + labour_cost
        + power_cost
    )

    good_packets = Decimal("188")

    cost_per_packet = total_batch_cost / good_packets

    return {
        "flour_rate": flour_rate,
        "flour_cost": flour_cost,
        "oil_cost": oil_cost,
        "spice_cost": spice_cost,
        "pouch_cost": pouch_cost,
        "carton_cost": carton_cost,
        "material_cost": total_material_cost,
        "labour_cost": labour_cost,
        "power_cost": power_cost,
        "total_batch_cost": total_batch_cost,
        "good_packets": good_packets,
        "cost_per_packet": cost_per_packet
    }