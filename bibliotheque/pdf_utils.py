from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

def generate_rapport_pdf(data, title):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Préparation des données
    pdf_data = []
    if title == "Livres populaires":
        headers = ["Livre", "Nombre d'emprunts"]
        pdf_data.append(headers)
        for item in data:
            pdf_data.append([item['livre__title'], str(item['total'])])
    else:  # Retards
        headers = ["Utilisateur", "Nombre de retards"]
        pdf_data.append(headers)
        for item in data:
            pdf_data.append([item['lecteur__username'], str(item['retards'])])
    
    # Création du tableau
    table = Table(pdf_data)
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)
    
    # Construction du PDF
    elements = []
    elements.append(table)
    doc.build(elements)
    
    buffer.seek(0)
    return buffer