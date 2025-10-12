"""
Модуль для автоматической генерации протоколов заседаний
с использованием OpenAI API и fpdf2
"""
import os
from datetime import datetime
from fpdf import FPDF
import openai
from app.models.meeting import Meeting, Message, AgendaItem, MeetingVote, VoteType
from app.models.user import User


class ProtocolPDF(FPDF):
    """Кастомный класс для генерации PDF протокола"""
    
    def __init__(self, meeting):
        super().__init__()
        self.meeting = meeting
        
    def header(self):
        """Заголовок на каждой странице"""
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'BRAMA UA e.V.', 0, 1, 'C')
        self.set_font('Arial', '', 12)
        self.cell(0, 10, 'Protokoll der Versammlung', 0, 1, 'C')
        self.ln(5)
        
    def footer(self):
        """Футер на каждой странице"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Seite {self.page_no()}', 0, 0, 'C')


def generate_protocol_text(meeting_id):
    """
    Генерирует текст протокола с помощью OpenAI API
    
    Args:
        meeting_id: ID заседания
        
    Returns:
        str: Сгенерированный текст протокола на немецком языке
    """
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        raise ValueError(f"Meeting {meeting_id} not found")
    
    # Получаем OpenAI API ключ
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment")
    
    # Собираем участников
    attendees = meeting.attendees.all()
    attendees_list = []
    for att in attendees:
        user = User.query.get(att.user_id)
        name = f"{user.first_name} {user.last_name}" if user.first_name else user.email
        attendees_list.append(name)
    
    # Собираем сообщения из чата
    messages = Message.query.filter_by(meeting_id=meeting_id).order_by(Message.created_at.asc()).all()
    chat_transcript = []
    for msg in messages:
        user = User.query.get(msg.user_id)
        name = f"{user.first_name} {user.last_name}" if user.first_name else user.email
        time_str = msg.created_at.strftime('%H:%M')
        chat_transcript.append(f"[{time_str}] {name}: {msg.content}")
    
    # Собираем результаты голосований
    agenda_items = AgendaItem.query.filter_by(meeting_id=meeting_id).order_by(AgendaItem.order).all()
    voting_results = []
    for item in agenda_items:
        votes = MeetingVote.query.filter_by(agenda_item_id=item.id).all()
        yes_count = sum(1 for v in votes if v.vote == VoteType.yes)
        no_count = sum(1 for v in votes if v.vote == VoteType.no)
        abstain_count = sum(1 for v in votes if v.vote == VoteType.abstain)
        
        voting_results.append({
            'title': item.title,
            'description': item.description or '',
            'yes': yes_count,
            'no': no_count,
            'abstain': abstain_count,
            'result': item.result
        })
    
    # Формируем контекст для OpenAI
    context = f"""
Ich benötige ein formelles Protokoll für eine Versammlung des BRAMA UA e.V.

VERSAMMLUNGSINFORMATIONEN:
Titel: {meeting.title}
Beschreibung: {meeting.description or 'Keine Beschreibung'}
Datum: {meeting.date.strftime('%d.%m.%Y %H:%M')}
Anzahl der Teilnehmer: {len(attendees_list)}

TEILNEHMER:
{chr(10).join(f'- {name}' for name in attendees_list)}

TAGESORDNUNG UND ABSTIMMUNGSERGEBNISSE:
"""
    
    for i, item in enumerate(voting_results, 1):
        context += f"""
{i}. {item['title']}
   Beschreibung: {item['description']}
   """
        if item['yes'] > 0 or item['no'] > 0 or item['abstain'] > 0:
            context += f"""Abstimmung: Ja: {item['yes']}, Nein: {item['no']}, Enthaltungen: {item['abstain']}
   Ergebnis: {item['result']}
   """
    
    if chat_transcript:
        context += f"""

DISKUSSIONSVERLAUF (Chat-Transkript):
{chr(10).join(chat_transcript)}
"""
    
    context += """

Bitte erstellen Sie ein professionelles Protokoll im deutschen formellen Stil für einen eingetragenen Verein (e.V.). 
Das Protokoll sollte folgende Struktur haben:

1. Kopfzeile mit Vereinsname, Datum, Uhrzeit und Ort
2. Liste der anwesenden Mitglieder
3. Tagesordnung
4. Beschlüsse und Abstimmungsergebnisse zu jedem Tagesordnungspunkt
5. Wichtige Diskussionspunkte (basierend auf dem Chat-Transkript)
6. Datum und Unterschriftszeilen für Protokollführer und Versammlungsleiter

Das Protokoll sollte sachlich, präzise und formal sein.
"""
    
    # Отправляем запрос в OpenAI
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Sie sind ein professioneller Protokollführer für einen deutschen eingetragenen Verein (e.V.). Erstellen Sie formelle, gut strukturierte Protokolle."
                },
                {
                    "role": "user",
                    "content": context
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        protocol_text = response.choices[0].message.content
        return protocol_text
        
    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}")


def create_pdf_protocol(meeting_id, protocol_text):
    """
    Создает PDF файл протокола
    
    Args:
        meeting_id: ID заседания
        protocol_text: Текст протокола (сгенерированный OpenAI)
        
    Returns:
        bytes: PDF файл в виде байтов
    """
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        raise ValueError(f"Meeting {meeting_id} not found")
    
    # Создаем PDF
    pdf = ProtocolPDF(meeting)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Добавляем основную информацию
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f'Titel: {meeting.title}', 0, 1)
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, f'Datum: {meeting.date.strftime("%d.%m.%Y %H:%M")}', 0, 1)
    pdf.ln(5)
    
    # Добавляем текст протокола
    pdf.set_font('Arial', '', 10)
    
    # Разбиваем текст на строки и добавляем в PDF
    lines = protocol_text.split('\n')
    for line in lines:
        # Обрабатываем заголовки (жирным шрифтом)
        if line.strip().endswith(':') or line.strip().startswith('##'):
            pdf.set_font('Arial', 'B', 11)
            pdf.multi_cell(0, 6, line.strip())
            pdf.set_font('Arial', '', 10)
        else:
            pdf.multi_cell(0, 6, line)
    
    # Возвращаем PDF как байты
    return pdf.output(dest='S').encode('latin-1')


def generate_and_save_protocol(meeting_id):
    """
    Генерирует протокол и сохраняет его
    
    Args:
        meeting_id: ID заседания
        
    Returns:
        tuple: (pdf_bytes, filename)
    """
    meeting = Meeting.query.get(meeting_id)
    if not meeting:
        raise ValueError(f"Meeting {meeting_id} not found")
    
    # Генерируем текст протокола
    protocol_text = generate_protocol_text(meeting_id)
    
    # Создаем PDF
    pdf_bytes = create_pdf_protocol(meeting_id, protocol_text)
    
    # Формируем имя файла
    date_str = meeting.date.strftime('%Y%m%d')
    filename = f"protokoll_{meeting_id}_{date_str}.pdf"
    
    return pdf_bytes, filename
