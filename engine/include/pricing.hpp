#ifndef PRICING_HPP
#define PRICING_HPP

struct Truck350Params {
    double cargo_percent;       // 0.0 a 100.0 (% de capacidad ocupada)
    double price_per_km;        // Tarifa por km fijada por el usuario (ej: $1.25 / km)
    double base_rate;           // Tarifa base fija de arranque/movilización (ej: $25.0)
    bool is_round_trip;         // True si es viaje de ida y vuelta
    double return_discount_pct; // Descuento en retorno si regresa vacío (ej: 30% -> 0.30)
    double extra_expenses;      // Gastos extras (caleteros, peajes, imprevistos)

    Truck350Params()
        : cargo_percent(100.0),
          price_per_km(1.20),
          base_rate(20.0),
          is_round_trip(false),
          return_discount_pct(0.30),
          extra_expenses(0.0) {}
};

struct QuoteResult {
    double effective_distance_km; // Distancia considerada (ida o ida+retorno)
    double base_price;            // Costo por distancia simple
    double cargo_multiplier;      // Factor de carga (1.0 a 1.35)
    double load_surcharge;        // Recargo por peso/carga
    double return_cost;           // Costo adicional por retorno
    double estimated_liters_fuel; // Litros estimados de gasolina/gasoil
    double estimated_hours;       // Tiempo estimado de viaje
    double total_price;           // Precio final cotizado
};

class PricingCalculator {
public:
    // Capacidad estándar del Camión 350 en kg
    static constexpr double MAX_CARGO_KG = 3500.0;
    static constexpr double AVG_SPEED_KMH = 65.0; // Velocidad promedio de carga

    static QuoteResult calculate_truck350_quote(double one_way_distance_km, const Truck350Params& params);
};

#endif // PRICING_HPP
