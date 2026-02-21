import os
import sys
import django
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

# Setup Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Ensure project root is on sys.path so Django can import the project
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleetflow.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Known test users and their passwords (created earlier)
creds = [
    ('ceo_rohit', 'Rohit Kumar', 'ADMIN', 'ceo_rohit@fleetflow.in', 'Rohit@2026'),
    ('admin_priya', 'Priya Desai', 'ADMIN', 'admin_priya@fleetflow.in', 'Priya@2026'),
    ('manager_arjun', 'Arjun Patel', 'MANAGER', 'manager_arjun@fleetflow.in', 'Arjun@2026'),
    ('dispatcher_sneha', 'Sneha Rao', 'DISPATCHER', 'dispatcher_sneha@fleetflow.in', 'Sneha@2026'),
    ('safety_kavita', 'Kavita Nair', 'SAFETY', 'safety_kavita@fleetflow.in', 'Kavita@2026'),
    ('finance_suresh', 'Suresh Gandhi', 'FINANCE', 'finance_suresh@fleetflow.in', 'Suresh@2026'),
]

out_path = os.path.join(BASE_DIR, 'credentials.pdf')

doc = SimpleDocTemplate(out_path, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
styles = getSampleStyleSheet()
flow = []

flow.append(Paragraph('FleetFlow - Test User Credentials', styles['Title']))
flow.append(Spacer(1, 12))

data = [['Username', 'Full Name', 'Role', 'Email', 'Password']]
for u, full, role, email, pwd in creds:
    # verify user exists in DB
    try:
        user = User.objects.get(username=u)
        data.append([u, full, role, email, pwd])
    except User.DoesNotExist:
        data.append([u + ' (missing)', full, role, email, pwd])

table = Table(data, colWidths=[90, 120, 80, 140, 90])
table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#0ea5a5')),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('ALIGN', (0,0), (-1,-1), 'LEFT'),
    ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
]))

flow.append(table)

try:
    doc.build(flow)
    print('PDF generated at:', out_path)
except Exception as e:
    print('Failed to create PDF:', e)
