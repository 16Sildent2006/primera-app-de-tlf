#include "../include/pricing.hpp"
#include <algorithm>

QuoteResult PricingCalculator::calculate_truck350_quote(double one_way_distance_km, const Truck350Params& params) {
    QuoteResult res;

    double valid_cargo_pct = std::clamp(params.cargo_percent, 0.0, 100.0);
    double valid_price_km = std::max(0.0, params.price_per_km);
    double valid_base_rate = std::max(0.0, params.base_rate);

    // Multiplicador por nivel de carga (1.0 = vacío, hasta 1.35 = batea a tope)
    res.cargo_multiplier = 1.0 + (valid_cargo_pct / 100.0) * 0.35;

    // Distancia simple de ida
    double dist_cost = one_way_distance_km * valid_price_km;
    res.base_price = dist_cost + valid_base_rate;

    // Recargo derivado del peso y esfuerzo del camión
    res.load_surcharge = dist_cost * (res.cargo_multiplier - 1.0);

    // Si es viaje de retorno
    if (params.is_round_trip) {
        res.effective_distance_km = one_way_distance_km * 2.0;
        double return_discount = std::clamp(params.return_discount_pct, 0.0, 1.0);
        // Retorno usualmente con camión vacío (precio base por km con descuento de retorno)
        res.return_cost = dist_cost * (1.0 - return_discount);
    } else {
        res.effective_distance_km = one_way_distance_km;
        res.return_cost = 0.0;
    }

    // Precio total final
    res.total_price = res.base_price + res.load_surcharge + res.return_cost + std::max(0.0, params.extra_expenses);

    // Estimación de combustible:
    // Camión 350 vacío rinde ~18L por cada 100 km (~5.5 km/L)
    // Camión 350 lleno rinde ~25L por cada 100 km (~4.0 km/L)
    double liters_per_100km = 18.0 + (7.0 * (valid_cargo_pct / 100.0));
    res.estimated_liters_fuel = (res.effective_distance_km / 100.0) * liters_per_100km;

    // Tiempo estimado en horas
    res.estimated_hours = res.effective_distance_km / AVG_SPEED_KMH;

    return res;
}
