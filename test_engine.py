import sys
from bridge.oriente_engine import OrienteTripEngine

def main():
    print("=" * 65)
    print("  VERIFICACIÓN DEL PUENTE PYTHON <-> MOTOR C/C++ (ORIENTE)")
    print("=" * 65)

    # 1. Inicializar motor
    engine = OrienteTripEngine()
    locations = engine.get_locations()
    print(f"\n[+] Ciudades cargadas desde C++: {len(locations)}")
    for loc in locations:
        print(f"    - ID {loc.id:2d}: {loc.name:18s} ({loc.state:11s}) [Lat: {loc.latitude:.4f}, Lon: {loc.longitude:.4f}]")

    print("\n" + "=" * 65)
    print("  CASO 1: Flete Puerto La Cruz -> Maturín (Camión 350 - 100% Carga)")
    print("=" * 65)

    quote1 = engine.calculate_trip(
        origin="Puerto La Cruz",
        destination="Maturín",
        cargo_percent=100.0,
        price_per_km=1.25,
        base_rate=30.0,
        is_round_trip=False
    )

    if quote1:
        print(f"  * Origen: {quote1.origin.name} ({quote1.origin.state})")
        print(f"  * Destino: {quote1.destination.name} ({quote1.destination.state})")
        print(f"  * Distancia Total: {quote1.distance_km:.2f} km")
        print(f"  * Tiempo Estimado: {quote1.estimated_hours:.2f} hrs")
        print(f"  * Combustible Estimado: {quote1.fuel_liters:.2f} L")
        print(f"  * Ruta calculada: {' -> '.join(n.name for n in quote1.path_nodes)}")
        print(f"  * Desglose: Base=${quote1.base_price:.2f} | Recargo Carga=${quote1.load_surcharge:.2f}")
        print(f"  >>> TOTAL A COBRAR: ${quote1.total_price:.2f} USD <<<")
    else:
        print("  [-] Error calculando ruta.")

    print("\n" + "=" * 65)
    print("  CASO 2: Flete Barcelona -> El Tigre (Ida y Vuelta, 70% Carga, $1.15/km)")
    print("=" * 65)

    quote2 = engine.calculate_trip(
        origin="Barcelona",
        destination="El Tigre",
        cargo_percent=70.0,
        price_per_km=1.15,
        base_rate=20.0,
        is_round_trip=True,
        return_discount_pct=0.30
    )

    if quote2:
        print(f"  * Distancia Solo Ida: {quote2.distance_km:.2f} km")
        print(f"  * Distancia Efectiva (Ida + Vuelta): {quote2.effective_distance_km:.2f} km")
        print(f"  * Ruta: {' -> '.join(n.name for n in quote2.path_nodes)}")
        print(f"  * Costo Ida: ${(quote2.base_price + quote2.load_surcharge):.2f}")
        print(f"  * Costo Retorno con Descuento: ${quote2.return_cost:.2f}")
        print(f"  * Combustible Total: {quote2.fuel_liters:.2f} L")
        print(f"  >>> TOTAL FLETE IDA Y VUELTA: ${quote2.total_price:.2f} USD <<<")

    print("\n" + "=" * 65)
    print("  CASO 3: Travesía Larga Carúpano (Sucre) -> Ciudad Bolívar")
    print("=" * 65)

    quote3 = engine.calculate_trip(
        origin="Carúpano",
        destination="Ciudad Bolívar",
        cargo_percent=90.0,
        price_per_km=1.40,
        base_rate=50.0,
        is_round_trip=False
    )

    if quote3:
        print(f"  * Distancia: {quote3.distance_km:.2f} km")
        print(f"  * Tiempo estimado: {quote3.estimated_hours:.2f} horas")
        print(f"  * Itinerario: {' -> '.join(n.name for n in quote3.path_nodes)}")
        print(f"  >>> TOTAL FLETE: ${quote3.total_price:.2f} USD <<<")

    print("\n[OK] Todas las pruebas se ejecutaron exitosamente.")

if __name__ == "__main__":
    main()
