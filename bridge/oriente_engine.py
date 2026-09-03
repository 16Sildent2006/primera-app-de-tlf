import ctypes
import os
import sys
import heapq
from dataclasses import dataclass
from typing import List, Optional, Union, Dict, Tuple

# Definición de estructuras C para ctypes
class CNodeInfo(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_int),
        ("name", ctypes.c_char * 64),
        ("state", ctypes.c_char * 64),
        ("latitude", ctypes.c_double),
        ("longitude", ctypes.c_double),
    ]

class CTripCalculationResult(ctypes.Structure):
    _fields_ = [
        ("status", ctypes.c_int),
        ("total_distance_km", ctypes.c_double),
        ("effective_distance_km", ctypes.c_double),
        ("total_price", ctypes.c_double),
        ("base_price", ctypes.c_double),
        ("load_surcharge", ctypes.c_double),
        ("return_cost", ctypes.c_double),
        ("estimated_liters_fuel", ctypes.c_double),
        ("estimated_hours", ctypes.c_double),
        ("path_length", ctypes.c_int),
        ("path_node_ids", ctypes.c_int * 100),
    ]

@dataclass
class Location:
    id: int
    name: str
    state: str
    latitude: float
    longitude: float

@dataclass
class TripQuote:
    found: bool
    origin: Location
    destination: Location
    distance_km: float
    effective_distance_km: float
    total_price: float
    base_price: float
    load_surcharge: float
    return_cost: float
    fuel_liters: float
    estimated_hours: float
    path_nodes: List[Location]

# Base de datos embebida para entornos móviles / Android APK
DEFAULT_ORIENTE_NODES = [
    Location(0, "Barcelona", "Anzoátegui", 10.1340, -64.6869),
    Location(1, "Puerto La Cruz", "Anzoátegui", 10.2138, -64.6328),
    Location(2, "Guanta", "Anzoátegui", 10.2372, -64.5939),
    Location(3, "Píritu", "Anzoátegui", 10.0571, -65.0336),
    Location(4, "Clarines", "Anzoátegui", 9.9415, -65.1742),
    Location(5, "Anaco", "Anzoátegui", 9.4347, -64.4646),
    Location(6, "Cantaura", "Anzoátegui", 9.3051, -64.3592),
    Location(7, "El Tigre", "Anzoátegui", 8.8875, -64.2454),
    Location(8, "Pariaguán", "Anzoátegui", 8.8550, -64.7100),
    Location(9, "Maturín", "Monagas", 9.7457, -63.1793),
    Location(10, "Punta de Mata", "Monagas", 9.6917, -63.6300),
    Location(11, "Temblador", "Monagas", 9.0142, -62.6186),
    Location(12, "Caripe", "Monagas", 10.1667, -63.4833),
    Location(13, "Cumaná", "Sucre", 10.4539, -64.1750),
    Location(14, "Carúpano", "Sucre", 10.6678, -63.2585),
    Location(15, "Cariaco", "Sucre", 10.4950, -63.5539),
    Location(16, "Güiria", "Sucre", 10.5794, -62.3006),
    Location(17, "Ciudad Bolívar", "Bolívar", 8.1292, -63.5408),
    Location(18, "Puerto Ordaz", "Bolívar", 8.2974, -62.7303),
    Location(19, "San Félix", "Bolívar", 8.3683, -62.6469),
]

DEFAULT_ORIENTE_EDGES = [
    (0, 1, 12.0, 1.0), (1, 2, 10.0, 1.0), (0, 3, 48.0, 1.0), (3, 4, 25.0, 1.05),
    (0, 5, 85.0, 1.0), (5, 6, 20.0, 1.0), (6, 7, 40.0, 1.0), (7, 8, 55.0, 1.1),
    (5, 10, 110.0, 1.15), (10, 9, 45.0, 1.0), (0, 9, 180.0, 1.05),
    (9, 11, 75.0, 1.05), (9, 12, 80.0, 1.2),
    (2, 13, 80.0, 1.1), (0, 13, 92.0, 1.1),
    (13, 15, 75.0, 1.05), (15, 14, 45.0, 1.05), (14, 16, 140.0, 1.2), (15, 12, 65.0, 1.25),
    (9, 14, 165.0, 1.15),
    (7, 17, 130.0, 1.05), (17, 18, 105.0, 1.0), (18, 19, 15.0, 1.0),
    (11, 18, 120.0, 1.05), (7, 18, 195.0, 1.05)
]

class OrienteTripEngine:
    """Motor de cálculo de rutas y tarifas de Oriente con soporte C++ nativo y fallback móvil."""

    def __init__(self, dll_path: Optional[str] = None):
        self._lib = None
        self._locations_cache: Optional[List[Location]] = None

        if dll_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            root_dir = os.path.dirname(current_dir)
            possible_paths = [
                os.path.join(root_dir, "oriente_engine.dll"),
                os.path.join(root_dir, "liboriente_engine.so"),
                os.path.join(current_dir, "oriente_engine.dll"),
                os.path.join(current_dir, "liboriente_engine.so"),
                "oriente_engine.dll"
            ]
            for p in possible_paths:
                if os.path.exists(p):
                    dll_path = p
                    break

        if dll_path and os.path.exists(dll_path):
            try:
                self._lib = ctypes.CDLL(os.path.abspath(dll_path))
                self._setup_signatures()
                self._lib.oriente_init_engine()
            except Exception:
                self._lib = None

    def _setup_signatures(self):
        self._lib.oriente_init_engine.argtypes = []
        self._lib.oriente_init_engine.restype = None

        self._lib.oriente_get_node_count.argtypes = []
        self._lib.oriente_get_node_count.restype = ctypes.c_int

        self._lib.oriente_get_node_by_id.argtypes = [ctypes.c_int, ctypes.POINTER(CNodeInfo)]
        self._lib.oriente_get_node_by_id.restype = ctypes.c_int

        self._lib.oriente_find_node_by_name.argtypes = [ctypes.c_char_p]
        self._lib.oriente_find_node_by_name.restype = ctypes.c_int

        self._lib.oriente_calculate_trip.argtypes = [
            ctypes.c_int, ctypes.c_int, ctypes.c_double, ctypes.c_double,
            ctypes.c_double, ctypes.c_int, ctypes.c_double, ctypes.c_double
        ]
        self._lib.oriente_calculate_trip.restype = CTripCalculationResult

    @staticmethod
    def _normalize_str(s: str) -> str:
        import unicodedata
        normalized = unicodedata.normalize('NFD', s.strip().lower())
        return ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')

    def get_locations(self) -> List[Location]:
        if self._locations_cache is not None:
            return self._locations_cache

        if self._lib:
            try:
                count = self._lib.oriente_get_node_count()
                locations = []
                for i in range(count):
                    c_node = CNodeInfo()
                    if self._lib.oriente_get_node_by_id(i, ctypes.byref(c_node)):
                        locations.append(Location(
                            id=c_node.id,
                            name=c_node.name.decode('utf-8', errors='ignore'),
                            state=c_node.state.decode('utf-8', errors='ignore'),
                            latitude=c_node.latitude,
                            longitude=c_node.longitude
                        ))
                self._locations_cache = locations
                return locations
            except Exception:
                pass

        self._locations_cache = DEFAULT_ORIENTE_NODES
        return self._locations_cache

    def find_location(self, name_or_id: Union[str, int]) -> Optional[Location]:
        locations = self.get_locations()
        if isinstance(name_or_id, int):
            if 0 <= name_or_id < len(locations):
                return locations[name_or_id]
            return None
        
        target = self._normalize_str(str(name_or_id))
        for loc in locations:
            if self._normalize_str(loc.name) == target:
                return loc
        for loc in locations:
            if target in self._normalize_str(loc.name):
                return loc
        return None

    def _dijkstra_fallback(self, start_id: int, end_id: int) -> Tuple[bool, float, List[int]]:
        """Algoritmo de Dijkstra embebido para respaldo en Android APK."""
        n = len(DEFAULT_ORIENTE_NODES)
        adj: Dict[int, List[Tuple[int, float, float]]] = {i: [] for i in range(n)}
        for u, v, d, c in DEFAULT_ORIENTE_EDGES:
            adj[u].append((v, d, c))
            adj[v].append((u, d, c))

        dist = {i: float('inf') for i in range(n)}
        prev = {i: -1 for i in range(n)}
        dist[start_id] = 0.0
        pq = [(0.0, start_id)]

        while pq:
            d_curr, u = heapq.heappop(pq)
            if d_curr > dist[u]:
                continue
            if u == end_id:
                break
            for v, d, c in adj[u]:
                weight = d * c
                if dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight
                    prev[v] = u
                    heapq.heappush(pq, (dist[v], v))

        if dist[end_id] == float('inf'):
            return False, 0.0, []

        path = []
        curr = end_id
        while curr != -1:
            path.append(curr)
            curr = prev[curr]
        path.reverse()

        real_km = 0.0
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            for dest, d, _ in adj[u]:
                if dest == v:
                    real_km += d
                    break
        return True, real_km, path

    def calculate_trip(
        self,
        origin: Union[str, int, Location],
        destination: Union[str, int, Location],
        cargo_percent: float = 100.0,
        price_per_km: float = 1.20,
        base_rate: float = 20.0,
        is_round_trip: bool = False,
        return_discount_pct: float = 0.30,
        extra_expenses: float = 0.0
    ) -> Optional[TripQuote]:
        loc_origin = origin if isinstance(origin, Location) else self.find_location(origin)
        loc_dest = destination if isinstance(destination, Location) else self.find_location(destination)

        if not loc_origin or not loc_dest:
            return None

        # Intentar ejecutar con C++ nativo si está disponible
        if self._lib:
            try:
                res = self._lib.oriente_calculate_trip(
                    loc_origin.id,
                    loc_dest.id,
                    cargo_percent,
                    price_per_km,
                    base_rate,
                    1 if is_round_trip else 0,
                    return_discount_pct,
                    extra_expenses
                )
                if res.status == 0:
                    all_locs = {loc.id: loc for loc in self.get_locations()}
                    path_locations = [all_locs[res.path_node_ids[i]] for i in range(res.path_length)]
                    return TripQuote(
                        found=True,
                        origin=loc_origin,
                        destination=loc_dest,
                        distance_km=res.total_distance_km,
                        effective_distance_km=res.effective_distance_km,
                        total_price=res.total_price,
                        base_price=res.base_price,
                        load_surcharge=res.load_surcharge,
                        return_cost=res.return_cost,
                        fuel_liters=res.estimated_liters_fuel,
                        estimated_hours=res.estimated_hours,
                        path_nodes=path_locations
                    )
            except Exception:
                pass

        # Fallback embebido
        found, km, path_ids = self._dijkstra_fallback(loc_origin.id, loc_dest.id)
        if not found:
            return None

        cargo_pct_clamped = max(0.0, min(100.0, cargo_percent))
        cargo_mult = 1.0 + (cargo_pct_clamped / 100.0) * 0.35
        base_cost = (km * price_per_km) + base_rate
        surcharge = (km * price_per_km) * (cargo_mult - 1.0)
        
        if is_round_trip:
            eff_km = km * 2.0
            ret_discount = max(0.0, min(1.0, return_discount_pct))
            ret_cost = (km * price_per_km) * (1.0 - ret_discount)
        else:
            eff_km = km
            ret_cost = 0.0

        total = base_cost + surcharge + ret_cost + max(0.0, extra_expenses)
        liters = (eff_km / 100.0) * (18.0 + (7.0 * (cargo_pct_clamped / 100.0)))
        hours = eff_km / 65.0

        all_locs = {loc.id: loc for loc in self.get_locations()}
        path_nodes = [all_locs[idx] for idx in path_ids]

        return TripQuote(
            found=True,
            origin=loc_origin,
            destination=loc_dest,
            distance_km=km,
            effective_distance_km=eff_km,
            total_price=total,
            base_price=base_cost,
            load_surcharge=surcharge,
            return_cost=ret_cost,
            fuel_liters=liters,
            estimated_hours=hours,
            path_nodes=path_nodes
        )
