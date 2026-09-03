import os
import datetime
from fpdf import FPDF
from bridge.oriente_engine import TripQuote

class FreightQuotePDF(FPDF):
    def header(self):
        # Banner superior
        self.set_fill_color(24, 32, 54) # Azul Marino Oscuro
        self.rect(0, 0, 210, 28, 'F')
        
        self.set_text_color(255, 255, 255)
        self.set_font('Helvetica', 'B', 16)
        self.set_xy(10, 6)
        self.cell(190, 8, 'FLETES ORIENTE - TRANSPORTE & CARGA', align='C')
        
        self.set_font('Helvetica', '', 10)
        self.set_xy(10, 15)
        self.cell(190, 6, 'Comprobante de Cotización y Plan de Ruta | Camión 350', align='C')
        self.ln(18)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f'Página {self.page_no()} | Generado automáticamente por el Motor C++ de Fletes Oriente', align='C')


def generate_quote_pdf(quote: TripQuote, params: dict, output_dir: str = "cotizaciones") -> str:
    """
    Genera un PDF profesional con todo el detalle de la cotización y la ruta del viaje.
    Retorna la ruta absoluta del archivo generado.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    date_display = datetime.datetime.now().strftime("%d/%m/%Y %I:%M %p")
    
    # Nombre de archivo limpio
    orig_clean = quote.origin.name.replace(" ", "_").replace("í", "i").replace("á", "a").replace("é", "e").replace("ó", "o").replace("ú", "u").replace("ü", "u")
    dest_clean = quote.destination.name.replace(" ", "_").replace("í", "i").replace("á", "a").replace("é", "e").replace("ó", "o").replace("ú", "u").replace("ü", "u")
    filename = f"Cotizacion_350_{orig_clean}_a_{dest_clean}_{timestamp_str}.pdf"
    file_path = os.path.abspath(os.path.join(output_dir, filename))

    pdf = FreightQuotePDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # --- ENCABEZADO DE METADATOS ---
    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(90, 90, 90)
    pdf.cell(100, 5, f'Fecha de Emisión: {date_display}', align='L')
    quote_id = f"COT-350-{timestamp_str[-6:]}"
    pdf.cell(90, 5, f'N° de Cotización: {quote_id}', align='R')
    pdf.ln(7)

    # --- SECCIÓN 1: DATOS GENERALES DEL VIAJE ---
    pdf.set_fill_color(240, 243, 248)
    pdf.set_draw_color(200, 210, 225)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(24, 32, 54)
    pdf.cell(190, 8, '  1. INFORMACIÓN DEL VIAJE', fill=True, border=1, ln=True)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(40, 40, 40)
    
    col_w = 95
    row_h = 7

    # Fila 1: Origen y Destino
    pdf.cell(col_w, row_h, f'  - Origen: {quote.origin.name} ({quote.origin.state})', border='L')
    pdf.cell(col_w, row_h, f'  - Destino: {quote.destination.name} ({quote.destination.state})', border='R', ln=True)

    # Fila 2: Modalidad y Distancia
    modalidad = "Ida y Vuelta (Retorno)" if params.get("is_round_trip", False) else "Solo Ida"
    pdf.cell(col_w, row_h, f'  - Modalidad: {modalidad}', border='L')
    pdf.cell(col_w, row_h, f'  - Distancia Total: {quote.effective_distance_km:.1f} km', border='R', ln=True)

    # Fila 3: Tiempo y Combustible
    total_mins = int(quote.estimated_hours * 60)
    hours = total_mins // 60
    mins = total_mins % 60
    time_fmt = f"{hours}h {mins}m aprox."
    pdf.cell(col_w, row_h, f'  - Tiempo Estimado: {time_fmt}', border='LB')
    pdf.cell(col_w, row_h, f'  - Combustible Estimado: {quote.fuel_liters:.1f} Litros', border='RB', ln=True)

    pdf.ln(5)

    # --- SECCIÓN 2: ESPECIFICACIONES DEL CAMIÓN 350 ---
    pdf.set_fill_color(240, 243, 248)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(24, 32, 54)
    pdf.cell(190, 8, '  2. ESPECIFICACIONES DEL VEHÍCULO Y CARGA', fill=True, border=1, ln=True)

    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(40, 40, 40)
    
    cargo_pct = params.get("cargo_percent", 100.0)
    kg_approx = int(3500 * (cargo_pct / 100.0))
    pdf.cell(col_w, row_h, '  - Tipo de Vehículo: Camión 350 (Batea / Plataforma)', border='L')
    pdf.cell(col_w, row_h, '  - Capacidad Máx.: ~3.500 kg', border='R', ln=True)
    pdf.cell(col_w, row_h, f'  - Nivel de Carga Declarado: {int(cargo_pct)}%', border='LB')
    pdf.cell(col_w, row_h, f'  - Peso Aprox. Carga: ~{kg_approx} kg', border='RB', ln=True)

    pdf.ln(5)

    # --- SECCIÓN 3: DESGLOSE ECONÓMICO Y COTIZACIÓN ---
    pdf.set_fill_color(240, 243, 248)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(24, 32, 54)
    pdf.cell(190, 8, '  3. DESGLOSE DE COSTOS Y TARIFAS', fill=True, border=1, ln=True)

    # Cabecera de la tabla
    pdf.set_fill_color(225, 232, 242)
    pdf.set_font('Helvetica', 'B', 9)
    pdf.cell(120, 7, '  Concepto', border=1, fill=True)
    pdf.cell(70, 7, 'Monto (USD)', border=1, align='R', fill=True, ln=True)

    pdf.set_font('Helvetica', '', 9)
    # Líneas de desglose
    pdf.cell(120, 6, f'  Tarifa Base de Movilización', border='LR')
    pdf.cell(70, 6, f'$ {params.get("base_fee", 25.0):.2f} USD  ', border='LR', align='R', ln=True)

    price_km = params.get("price_per_km", 1.25)
    pdf.cell(120, 6, f'  Costo por Distancia ({quote.distance_km:.1f} km a ${price_km:.2f}/km)', border='LR')
    pdf.cell(70, 6, f'$ {(quote.distance_km * price_km):.2f} USD  ', border='LR', align='R', ln=True)

    pdf.cell(120, 6, f'  Recargo por Nivel de Carga / Peso ({int(cargo_pct)}% batea)', border='LR')
    pdf.cell(70, 6, f'$ {quote.load_surcharge:.2f} USD  ', border='LR', align='R', ln=True)

    if params.get("is_round_trip", False):
        pdf.cell(120, 6, f'  Costo de Retorno (con 30% descuento de viaje vacío)', border='LR')
        pdf.cell(70, 6, f'$ {quote.return_cost:.2f} USD  ', border='LR', align='R', ln=True)

    extras = params.get("extra_expenses", 0.0)
    if extras > 0:
        pdf.cell(120, 6, f'  Gastos Adicionales (Peajes / Ayudantes / Imprevistos)', border='LR')
        pdf.cell(70, 6, f'$ {extras:.2f} USD  ', border='LR', align='R', ln=True)

    pdf.cell(190, 1, '', border='T', ln=True) # Línea divisoria

    # TOTAL DESTACADO
    pdf.set_fill_color(22, 101, 52) # Verde oscuro
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(120, 12, '  PRECIO TOTAL DEL FLETE:', fill=True, border=1)
    pdf.cell(70, 12, f'$ {quote.total_price:.2f} USD  ', fill=True, border=1, align='R', ln=True)

    pdf.ln(5)

    # --- SECCIÓN 4: ITINERARIO DE RUTA VIAL ---
    pdf.set_fill_color(240, 243, 248)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.set_text_color(24, 32, 54)
    pdf.cell(190, 8, '  4. ITINERARIO Y PARADAS DE RUTA EN ORIENTE', fill=True, border=1, ln=True)

    pdf.set_font('Helvetica', '', 9)
    pdf.set_text_color(50, 50, 50)
    
    itinerary_nodes = quote.path_nodes
    for i, node in enumerate(itinerary_nodes):
        is_first = (i == 0)
        is_last = (i == len(itinerary_nodes) - 1)
        
        prefix = "[ORIGEN] " if is_first else ("[DESTINO] " if is_last else f"[{i+1}] ")
        tag = f"  {prefix}{node.name} ({node.state}) - Lat: {node.latitude:.4f}, Lon: {node.longitude:.4f}"
        
        pdf.set_font('Helvetica', 'B' if (is_first or is_last) else '', 9)
        pdf.cell(190, 6, tag, border='LR', ln=True)
    
    pdf.cell(190, 1, '', border='T', ln=True)

    # Guardar archivo
    pdf.output(file_path)
    return file_path
