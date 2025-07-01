import streamlit as st
import pandas as pd
from groq import Groq
import plotly.express as px
from datetime import datetime
import json
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import base64
from reportlab.lib.units import inch
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
import plotly.io as pio
from reportlab.platypus.flowables import Image
import os

# Set page config first, before any other Streamlit commands
st.set_page_config(
    page_title="Yoga Progress Analysis",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def get_groq_client():
    """Initialize Groq client with API key from environment or secrets."""
    api_key = None
    
    # Try to get API key from environment variable first
    api_key = os.getenv('GROQ_API_KEY')
    
    # If not in environment, try to get from streamlit secrets
    if not api_key and 'GROQ_API_KEY' in st.secrets:
        api_key = st.secrets['GROQ_API_KEY']
    
    if not api_key:
        st.error("""
            Groq API key not found. Please set it up:
            1. Local development: Set GROQ_API_KEY environment variable
            2. Streamlit Cloud: Add GROQ_API_KEY to your app secrets
            """)
        st.stop()
    
    return Groq(api_key=api_key)

# Initialize Groq client
try:
    groq_client = get_groq_client()
except Exception as e:
    st.error(f"Failed to initialize Groq client: {str(e)}")
    st.stop()

def initialize_session_state():
    default_data = {
        'flexibility': 0,
        'strength': 0,
        'balance': 0,
        'pain': 0,
        'posture': 0,
        'breathing': 0,
        'spine': 0,
        'hips': 0,
        'shoulders': 0,
        'core': 0,
        'stress': 0,
        'energy': 0,
        'focus': 0,
        'sleep': 0,
        'anxiety': 0,
        'mood': 0,
        'mindfulness': 0,
        'notes': '',
        'limitations': '',
        'symptoms': ''
    }
    
    if 'before_data' not in st.session_state:
        st.session_state.before_data = default_data.copy()
    if 'after_data' not in st.session_state:
        st.session_state.after_data = default_data.copy()
    if 'client_info' not in st.session_state:
        st.session_state.client_info = {
            'name': '',
            'age': 0,
            'medical_history': '',
            'current_medications': '',
            'previous_yoga_experience': '',
            'primary_goals': [],
            'specific_concerns': '',
            'occupation': '',
            'work_activity_level': '',
            'stress_sources': [],
            'exercise_routine': '',
            'sleep_hours': 7,
            'diet_type': ''
        }

def create_comparison_charts(before_data, after_data):
    # Physical metrics comparison
    physical_metrics = {
        'Flexibility': [before_data['flexibility'], after_data['flexibility']],
        'Strength': [before_data['strength'], after_data['strength']],
        'Balance': [before_data['balance'], after_data['balance']],
        'Pain Level': [before_data['pain'], after_data['pain']],
        'Posture': [before_data['posture'], after_data['posture']],
        'Breathing': [before_data['breathing'], after_data['breathing']],
        'Spine': [before_data['spine'], after_data['spine']],
        'Hips': [before_data['hips'], after_data['hips']],
        'Shoulders': [before_data['shoulders'], after_data['shoulders']],
        'Core': [before_data['core'], after_data['core']]
    }
    
    # Mental metrics comparison
    mental_metrics = {
        'Stress': [before_data['stress'], after_data['stress']],
        'Energy': [before_data['energy'], after_data['energy']],
        'Focus': [before_data['focus'], after_data['focus']],
        'Sleep': [before_data['sleep'], after_data['sleep']],
        'Anxiety': [before_data['anxiety'], after_data['anxiety']],
        'Mood': [before_data['mood'], after_data['mood']],
        'Mindfulness': [before_data['mindfulness'], after_data['mindfulness']]
    }
    
    # Create dataframes and charts
    physical_df = pd.DataFrame(physical_metrics, index=['Before', 'After']).transpose()
    mental_df = pd.DataFrame(mental_metrics, index=['Before', 'After']).transpose()
    
    fig1 = px.bar(physical_df, barmode='group', title='Physical Metrics Comparison')
    fig2 = px.bar(mental_df, barmode='group', title='Mental & Emotional Metrics Comparison')
    
    return fig1, fig2

def generate_analysis(before_data, after_data, client_info):
    prompt = f"""
    As an expert yoga trainer and wellness analyst, provide a detailed progress analysis for:
    
    CLIENT PROFILE:
    Name: {client_info['name']}
    Age: {client_info['age']}
    Occupation: {client_info['occupation']}
    Previous Yoga Experience: {client_info['previous_yoga_experience']}
    Primary Goals: {', '.join(client_info['primary_goals'])}
    
    COMPREHENSIVE ASSESSMENT COMPARISON:
    
    1. PHYSICAL METRICS ANALYSIS:
    
    Basic Metrics:
    Flexibility: Before {before_data['flexibility']}/10 → After {after_data['flexibility']}/10
    Strength: Before {before_data['strength']}/10 → After {after_data['strength']}/10
    Balance: Before {before_data['balance']}/10 → After {after_data['balance']}/10
    Pain Levels: Before {before_data['pain']}/10 → After {after_data['pain']}/10
    
    Detailed Physical Assessment:
    Posture: Before {before_data['posture']}/10 → After {after_data['posture']}/10
    Breathing: Before {before_data['breathing']}/10 → After {after_data['breathing']}/10
    Spine Flexibility: Before {before_data['spine']}/10 → After {after_data['spine']}/10
    Hip Mobility: Before {before_data['hips']}/10 → After {after_data['hips']}/10
    Shoulder Mobility: Before {before_data['shoulders']}/10 → After {after_data['shoulders']}/10
    Core Strength: Before {before_data['core']}/10 → After {after_data['core']}/10
    
    2. MENTAL & EMOTIONAL METRICS:
    
    Stress Levels: Before {before_data['stress']}/10 → After {after_data['stress']}/10
    Energy Levels: Before {before_data['energy']}/10 → After {after_data['energy']}/10
    Focus & Clarity: Before {before_data['focus']}/10 → After {after_data['focus']}/10
    Sleep Quality: Before {before_data['sleep']}/10 → After {after_data['sleep']}/10
    Anxiety Levels: Before {before_data['anxiety']}/10 → After {after_data['anxiety']}/10
    Overall Mood: Before {before_data['mood']}/10 → After {after_data['mood']}/10
    Mindfulness: Before {before_data['mindfulness']}/10 → After {after_data['mindfulness']}/10
    
    Lifestyle Factors:
    - Work Activity Level: {client_info['work_activity_level']}
    - Exercise Routine: {client_info['exercise_routine']}
    - Sleep Hours: {client_info['sleep_hours']}
    - Diet Type: {client_info['diet_type']}
    - Stress Sources: {', '.join(client_info['stress_sources'])}
    
    Initial Limitations/Symptoms:
    {before_data['limitations']}
    {before_data['symptoms']}
    
    Current Notes:
    Before: {before_data['notes']}
    After: {after_data['notes']}
    
    Please provide a detailed analysis with the following sections:

    1. EXECUTIVE SUMMARY
    Provide a concise overview of the client's overall progress and key achievements.

    2. PHYSICAL PROGRESS ANALYSIS
    - Detailed analysis of improvements in all physical metrics
    - Specific areas of notable improvement
    - Areas requiring continued attention
    
    3. MENTAL & EMOTIONAL WELLNESS PROGRESS
    - Comprehensive analysis of mental and emotional improvements
    - Impact on daily life and wellbeing
    - Notable behavioral changes
    
    4. KEY ACHIEVEMENTS
    List the top 3-5 most significant improvements observed.
    
    5. AREAS FOR FOCUS
    Identify 2-3 specific areas that need continued attention and work.
    
    6. PERSONALIZED RECOMMENDATIONS
    Provide 4-5 specific, actionable recommendations for:
    - Poses or exercises to practice
    - Lifestyle adjustments
    - Mental wellness practices
    - Sleep hygiene improvements (if applicable)
    
    7. LONG-TERM OUTLOOK
    - Projected benefits if current progress continues
    - Potential milestones to work towards
    - Timeline expectations
    
    8. MOTIVATIONAL INSIGHTS
    End with a personalized motivational message that:
    - Acknowledges their progress
    - Encourages continued dedication
    - Highlights their potential for further growth

    Please format the response clearly with headers and bullet points where appropriate.
    Focus on being specific, actionable, and encouraging while maintaining a professional tone.
    """
    
    response = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="meta-llama/llama-4-maverick-17b-128e-instruct",
        temperature=0.7,
        max_tokens=3000,
        top_p=0.95,
        stream=False
    )
    
    return response.choices[0].message.content

def set_custom_style():
    st.markdown("""
        <style>
        /* Main container */
        .main {
            padding: 2rem;
        }
        
        /* Headers */
        h1 {
            color: #2E4057;
            padding-bottom: 1.5rem;
        }
        
        h2 {
            color: #2E4057;
            font-size: 1.8rem;
            padding: 1rem 0;
        }
        
        h3 {
            color: #2E4057;
            font-size: 1.4rem;
            padding: 0.8rem 0;
        }
        
        /* Slider styling */
        .stSlider {
            padding: 1rem 0;
        }
        
        .stSlider > div > div {
            background-color: #f0f2f6;
        }
        
        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding: 0 20px;
            background-color: #ffffff;
            border-radius: 5px 5px 0 0;
            color: #2E4057;
            font-weight: 600;
        }
        
        .stTabs [aria-selected="true"] {
            background-color: #2E4057;
            color: #ffffff;
        }
        
        /* Input fields */
        .stTextInput > div > div {
            background-color: #ffffff;
            border-radius: 5px;
        }
        
        /* Cards for metric groups */
        .metric-card {
            background-color: #ffffff;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

def create_metric_card(title, content):
    st.markdown(f"""
        <div class="metric-card">
            <h3>{title}</h3>
            {content}
        </div>
    """, unsafe_allow_html=True)

def generate_dietary_plan(client_info, before_data, after_data):
    prompt = f"""
    As a professional nutritionist, create a detailed 7-day meal plan for:

    CLIENT PROFILE:
    Name: {client_info['name']}
    Height: {client_info['height']} cm
    Weight: {client_info['weight']} kg
    Dietary Restrictions: {client_info['dietary_restrictions']}
    Health Goals: {', '.join(client_info['health_goals'])}
    Food Allergies: {client_info['food_allergies']}
    Exercise Level: {client_info['exercise_routine']}

    Please provide a COMPLETE 7-day meal plan following this EXACT format for each day:

    [DAY]
    Breakfast (7:00 AM)
    Main: [Provide specific meal with portions]
    Alternative: [Provide specific alternative meal]
    Calories: [Exact number]
    Protein: [X]g
    Carbs: [X]g
    Fat: [X]g
    Prep Time: [X] mins

    Morning Snack (10:00 AM)
    [Same format as breakfast]

    Lunch (12:30 PM)
    [Same format as breakfast]

    Afternoon Snack (3:30 PM)
    [Same format as breakfast]

    Dinner (7:00 PM)
    [Same format as breakfast]

    IMPORTANT REQUIREMENTS:
    1. Provide SPECIFIC meal descriptions with portions
    2. Include EXACT nutrient values
    3. Consider client's dietary restrictions and allergies
    4. Keep total daily calories appropriate for their goals
    5. Include realistic prep times
    6. Ensure meals are practical and easy to prepare
    7. Provide realistic alternatives for each meal

    Please maintain this exact format for all 7 days.
    """
    
    response = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="meta-llama/llama-4-maverick-17b-128e-instruct",
        temperature=0.7,
        max_tokens=3000,
        top_p=0.95,
        stream=False
    )
    
    return response.choices[0].message.content

def create_pdf(client_info, analysis, before_data, after_data, fig1, fig2):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles - check if they exist first
    try:
        custom_title = ParagraphStyle(
            name='CustomTitle',  # Changed from 'Title' to 'CustomTitle'
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1,  # Center alignment
            textColor=colors.HexColor('#2E4057')
        )
        styles.add(custom_title)
    except ValueError:
        pass  # Style already exists

    try:
        custom_heading = ParagraphStyle(
            name='CustomHeading2',  # Changed from 'Heading2' to 'CustomHeading2'
            parent=styles['Heading2'],
            fontSize=18,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.HexColor('#2E4057')
        )
        styles.add(custom_heading)
    except ValueError:
        pass

    try:
        custom_body = ParagraphStyle(
            name='CustomBody',  # Changed from 'BodyText' to 'CustomBody'
            parent=styles['Normal'],
            fontSize=12,
            leading=16,
            spaceBefore=6,
            spaceAfter=6
        )
        styles.add(custom_body)
    except ValueError:
        pass
    
    # Title Page - using new style names
    story.append(Paragraph(f"Yoga Progress Report", styles['CustomTitle']))
    story.append(Paragraph(f"for {client_info['name']}", styles['CustomTitle']))
    story.append(Spacer(1, 30))
    
    # Rest of the function remains the same, but use the new style names
    story.append(Paragraph(f"Assessment Date: {datetime.now().strftime('%B %d, %Y')}", styles['CustomBody']))
    story.append(Paragraph(f"Experience Level: {client_info['previous_yoga_experience']}", styles['CustomBody']))
    story.append(Spacer(1, 30))
    
    # Progress Visualization Section
    story.append(Paragraph("Progress Visualization", styles['CustomHeading2']))
    story.append(Spacer(1, 10))
    
    # Add charts with better formatting
    for fig, title in [
        (fig1, "Physical Metrics Comparison"),
        (fig2, "Mental & Emotional Metrics Comparison")
    ]:
        story.append(Paragraph(title, styles['CustomBody']))
        img_bytes = pio.to_image(fig, format="png", width=800, height=400, scale=2)
        img_stream = BytesIO(img_bytes)
        img = Image(img_stream)
        img.drawHeight = 4*inch
        img.drawWidth = 7*inch
        story.append(img)
        story.append(Spacer(1, 20))
    
    # Summary Tables
    story.append(Paragraph("Progress Summary", styles['CustomHeading2']))
    
    # Physical Metrics Summary Table
    physical_data = [
        ['Metric', 'Before', 'After', 'Change'],
        ['Flexibility', f"{before_data['flexibility']}/10", f"{after_data['flexibility']}/10", 
         f"{after_data['flexibility'] - before_data['flexibility']:+d}"],
        ['Strength', f"{before_data['strength']}/10", f"{after_data['strength']}/10",
         f"{after_data['strength'] - before_data['strength']:+d}"],
        ['Balance', f"{before_data['balance']}/10", f"{after_data['balance']}/10",
         f"{after_data['balance'] - before_data['balance']:+d}"],
        ['Posture', f"{before_data['posture']}/10", f"{after_data['posture']}/10",
         f"{after_data['posture'] - before_data['posture']:+d}"],
        ['Core Strength', f"{before_data['core']}/10", f"{after_data['core']}/10",
         f"{after_data['core'] - before_data['core']:+d}"]
    ]
    
    physical_table = Table(physical_data, colWidths=[120, 80, 80, 80])
    physical_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ]))
    story.append(physical_table)
    story.append(Spacer(1, 20))
    
    # Mental Metrics Summary Table
    mental_data = [
        ['Metric', 'Before', 'After', 'Change'],
        ['Stress', f"{before_data['stress']}/10", f"{after_data['stress']}/10",
         f"{after_data['stress'] - before_data['stress']:+d}"],
        ['Energy', f"{before_data['energy']}/10", f"{after_data['energy']}/10",
         f"{after_data['energy'] - before_data['energy']:+d}"],
        ['Focus', f"{before_data['focus']}/10", f"{after_data['focus']}/10",
         f"{after_data['focus'] - before_data['focus']:+d}"],
        ['Sleep', f"{before_data['sleep']}/10", f"{after_data['sleep']}/10",
         f"{after_data['sleep'] - before_data['sleep']:+d}"],
        ['Mindfulness', f"{before_data['mindfulness']}/10", f"{after_data['mindfulness']}/10",
         f"{after_data['mindfulness'] - before_data['mindfulness']:+d}"]
    ]
    
    mental_table = Table(mental_data, colWidths=[120, 80, 80, 80])
    mental_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
    ]))
    story.append(mental_table)
    story.append(Spacer(1, 30))
    
    # Detailed Analysis Section
    story.append(Paragraph("Detailed Progress Analysis", styles['CustomHeading2']))
    story.append(Spacer(1, 10))
    
    # Split analysis into sections and format
    sections = analysis.split('\n\n')
    for section in sections:
        if section.strip():
            # Check if it's a header (starts with number and dot)
            if section.strip()[0].isdigit() and '. ' in section:
                header, content = section.split('\n', 1)
                story.append(Paragraph(header.strip(), styles['CustomHeading2']))
                story.append(Paragraph(content.strip(), styles['CustomBody']))
            else:
                story.append(Paragraph(section.strip(), styles['CustomBody']))
            story.append(Spacer(1, 10))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def create_diet_pdf(client_info, dietary_plan):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),  # Changed to landscape for more width
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    styles.add(ParagraphStyle(
        name='CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1
    ))
    
    styles.add(ParagraphStyle(
        name='CustomDayHeader',
        parent=styles['Heading2'],
        fontSize=18,
        spaceBefore=20,
        spaceAfter=12,
        textColor=colors.HexColor('#2E4057')
    ))
    
    # Title
    story.append(Paragraph("7-Day Meal Plan", styles['CustomTitle']))
    story.append(Paragraph(f"for {client_info['name']}", styles['CustomTitle']))
    story.append(Spacer(1, 20))
    
    # Client Profile Table
    profile_data = [
        ['Client Profile', ''],
        ['Height', f"{client_info['height']} cm"],
        ['Weight', f"{client_info['weight']} kg"],
        ['Dietary Restrictions', ', '.join(client_info['dietary_restrictions'])],
        ['Health Goals', ', '.join(client_info['health_goals'])],
        ['Food Allergies', client_info['food_allergies']]
    ]
    
    profile_table = Table(profile_data, colWidths=[200, 300])
    profile_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    story.append(profile_table)
    story.append(Spacer(1, 30))
    
    # Initialize variables
    current_day = None
    meal_data = None
    
    # Process the dietary plan text
    lines = dietary_plan.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        # Check if this is a day header
        if any(day in line for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']):
            # Add previous day's table if it exists
            if meal_data and len(meal_data) > 1:
                table = Table(meal_data, colWidths=[120, 300, 200, 80])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('PADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('WORDWRAP', (0, 0), (-1, -1), True)
                ]))
                story.append(table)
                story.append(Spacer(1, 15))
            
            current_day = line
            story.append(Paragraph(current_day, styles['CustomDayHeader']))
            meal_data = [['Meal Time', 'Details', 'Nutrients', 'Prep Time']]
            i += 1
            continue
        
        # Process meal entry
        if any(meal in line for meal in ['Breakfast', 'Morning Snack', 'Lunch', 'Afternoon Snack', 'Dinner']):
            meal_time = line
            details = []
            nutrients = []
            prep_time = ''
            
            # Collect all information for this meal
            while i < len(lines) and not any(next_meal in lines[i] for next_meal in 
                  ['Breakfast', 'Morning Snack', 'Lunch', 'Afternoon Snack', 'Dinner']):
                line = lines[i].strip()
                if line.startswith('Main:') or line.startswith('Alternative:'):
                    details.append(line)
                elif line.startswith(('Calories:', 'Protein:', 'Carbs:', 'Fat:')):
                    nutrients.append(line)
                elif line.startswith('Prep Time:'):
                    prep_time = line.split(':')[1].strip()
                i += 1
                if i >= len(lines) or not line:
                    break
            
            # Add meal to table
            if details and nutrients:
                meal_data.append([
                    meal_time,
                    '\n'.join(details),
                    '\n'.join(nutrients),
                    prep_time
                ])
            continue
        
        i += 1
    
    # Add the last table if it exists
    if meal_data and len(meal_data) > 1:
        table = Table(meal_data, colWidths=[120, 300, 200, 80])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E4057')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('WORDWRAP', (0, 0), (-1, -1), True)
        ]))
        story.append(table)
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer

def main():
    initialize_session_state()
    set_custom_style()
    
    # Initialize client_info at the start of main
    client_info = {
        'name': '',
        'age': 0,
        'occupation': '',
        'previous_yoga_experience': '',
        'primary_goals': [],
        'specific_concerns': '',
        'work_activity_level': '',
        'stress_sources': [],
        'exercise_routine': '',
        'sleep_hours': 7,
        'diet_type': '',
        'current_medications': '',
        'height': 170,
        'weight': 70,
        'target_weight': 70,
        'dietary_restrictions': [],
        'food_allergies': '',
        'preferred_cuisine': [],
        'meal_prep_time': 30,
        'medical_conditions': '',
        'digestive_issues': '',
        'health_goals': [],
        'nutritional_needs': ''
    }
    
    # Update the title with icon and better styling
    st.markdown("# 🧘‍♀️ Yoga Progress Analysis")
    
    # Client Information section with better layout
    st.markdown("## 📋 Client Information")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        client_name = st.text_input("Client Name", placeholder="Enter client's full name")
    with col2:
        client_age = st.number_input("Age", 18, 100, value=25)
    with col3:
        assessment_date = st.date_input("Assessment Date")
    
    col1, col2 = st.columns(2)
    with col1:
        session_type = st.selectbox(
            "Session Type",
            ["In-person", "Online", "Healing-focused"],
            index=0
        )
    with col2:
        previous_yoga_experience = st.selectbox(
            "Previous Yoga Experience",
            ["None", "Beginner", "Intermediate", "Advanced"],
            index=0
        )

    # Create tabs with better styling
    tabs = st.tabs(["📝 Before Assessment", "📈 After Assessment", "📊 Analysis", "🥗 Diet Plan"])
    
    with tabs[0]:
        st.markdown("## Before Assessment")
        
        # Physical Metrics Card
        col1, col2 = st.columns(2)
        with col1:
            with st.container():
                st.markdown("### 💪 Physical Metrics")
                before_flexibility = st.slider("Flexibility Level (Before)", 0, 10, key='b_flex')
                before_strength = st.slider("Strength Level (Before)", 0, 10, key='b_str')
                before_balance = st.slider("Balance Score (Before)", 0, 10, key='b_bal')
                before_pain = st.slider("Pain Level (Before)", 0, 10, key='b_pain')
                before_posture = st.slider("Posture (Before)", 0, 10, key='b_posture')
                before_breathing = st.slider("Breathing Level (Before)", 0, 10, key='b_breathing')
                before_spine = st.slider("Spine Flexibility Level (Before)", 0, 10, key='b_spine')
                before_hips = st.slider("Hip Mobility Level (Before)", 0, 10, key='b_hips')
                before_shoulders = st.slider("Shoulder Mobility Level (Before)", 0, 10, key='b_shoulders')
                before_core = st.slider("Core Strength Level (Before)", 0, 10, key='b_core')
            with st.container():
                st.markdown("### 🧘‍♀️ Mental & Emotional Metrics")
                before_stress = st.slider("Stress Level (Before)", 0, 10, key='b_stress')
                before_energy = st.slider("Energy Level (Before)", 0, 10, key='b_energy')
                before_focus = st.slider("Focus & Clarity (Before)", 0, 10, key='b_focus')
                before_sleep = st.slider("Sleep Quality (Before)", 0, 10, key='b_sleep')
                before_anxiety = st.slider("Anxiety Level (Before)", 0, 10, key='b_anxiety')
                before_mood = st.slider("Overall Mood (Before)", 0, 10, key='b_mood')
                before_mindfulness = st.slider("Mindfulness (Before)", 0, 10, key='b_mindfulness')
        
        before_notes = st.text_area("Additional Notes (Before)")
        before_limitations = st.text_area("Current Limitations (Before)")
        before_symptoms = st.text_area("Current Symptoms (Before)")
        
        if st.button("Save Before Assessment"):
            st.session_state.before_data.update({
                'flexibility': before_flexibility,
                'strength': before_strength,
                'balance': before_balance,
                'pain': before_pain,
                'posture': before_posture,
                'breathing': before_breathing,
                'spine': before_spine,
                'hips': before_hips,
                'shoulders': before_shoulders,
                'core': before_core,
                'stress': before_stress,
                'energy': before_energy,
                'focus': before_focus,
                'sleep': before_sleep,
                'anxiety': before_anxiety,
                'mood': before_mood,
                'mindfulness': before_mindfulness,
                'notes': before_notes,
                'limitations': before_limitations,
                'symptoms': before_symptoms
            })
            st.success("Before assessment saved!")

    with tabs[1]:
        st.markdown("## After Assessment")
        
        # Physical Metrics Card
        col1, col2 = st.columns(2)
        with col1:
            with st.container():
                st.markdown("### 💪 Physical Metrics")
                after_flexibility = st.slider("Flexibility Level (After)", 0, 10, key='a_flex')
                after_strength = st.slider("Strength Level (After)", 0, 10, key='a_str')
                after_balance = st.slider("Balance Score (After)", 0, 10, key='a_bal')
                after_pain = st.slider("Pain Level (After)", 0, 10, key='a_pain')
                after_posture = st.slider("Posture (After)", 0, 10, key='a_posture')
                after_breathing = st.slider("Breathing Level (After)", 0, 10, key='a_breathing')
                after_spine = st.slider("Spine Flexibility Level (After)", 0, 10, key='a_spine')
                after_hips = st.slider("Hip Mobility Level (After)", 0, 10, key='a_hips')
                after_shoulders = st.slider("Shoulder Mobility Level (After)", 0, 10, key='a_shoulders')
                after_core = st.slider("Core Strength Level (After)", 0, 10, key='a_core')
            with st.container():
                st.markdown("### 🧘‍♀️ Mental & Emotional Metrics")
                after_stress = st.slider("Stress Level (After)", 0, 10, key='a_stress')
                after_energy = st.slider("Energy Level (After)", 0, 10, key='a_energy')
                after_focus = st.slider("Focus & Clarity (After)", 0, 10, key='a_focus')
                after_sleep = st.slider("Sleep Quality (After)", 0, 10, key='a_sleep')
                after_anxiety = st.slider("Anxiety Level (After)", 0, 10, key='a_anxiety')
                after_mood = st.slider("Overall Mood (After)", 0, 10, key='a_mood')
                after_mindfulness = st.slider("Mindfulness (After)", 0, 10, key='a_mindfulness')
        
        after_notes = st.text_area("Additional Notes (After)")
        
        if st.button("Save After Assessment"):
            st.session_state.after_data.update({
                'flexibility': after_flexibility,
                'strength': after_strength,
                'balance': after_balance,
                'pain': after_pain,
                'posture': after_posture,
                'breathing': after_breathing,
                'spine': after_spine,
                'hips': after_hips,
                'shoulders': after_shoulders,
                'core': after_core,
                'stress': after_stress,
                'energy': after_energy,
                'focus': after_focus,
                'sleep': after_sleep,
                'anxiety': after_anxiety,
                'mood': after_mood,
                'mindfulness': after_mindfulness,
                'notes': after_notes
            })
            st.success("After assessment saved!")

    with tabs[2]:
        st.markdown("## Progress Analysis")
        
        if st.button("Generate Analysis"):
            if (not st.session_state.before_data.get('flexibility') and 
                not st.session_state.after_data.get('flexibility')):
                st.error("Please complete and save both before and after assessments first!")
            else:
                try:
                    with st.spinner("Generating your progress report..."):
                        # Generate charts
                        fig1, fig2 = create_comparison_charts(
                            st.session_state.before_data, 
                            st.session_state.after_data
                        )
                        
                        # Display charts
                        st.plotly_chart(fig1)
                        st.plotly_chart(fig2)
                        
                        # Generate analysis
                        analysis = generate_analysis(
                            st.session_state.before_data,
                            st.session_state.after_data,
                            client_info
                        )
                        
                        st.subheader("Your Progress Journey")
                        st.write(analysis)
                        
                        # Generate PDF report and store in session state
                        progress_pdf = create_pdf(
                            client_info,
                            analysis,
                            st.session_state.before_data,
                            st.session_state.after_data,
                            fig1,
                            fig2
                        )
                        
                        # Store PDF data in session state
                        st.session_state.progress_pdf = progress_pdf.getvalue()
                        
                        # Add PDF download button with improved styling
                        st.markdown("### 📥 Download Your Progress Report")
                        st.download_button(
                            label="Download Complete Progress Report (PDF)",
                            data=st.session_state.progress_pdf,
                            file_name=f"yoga_progress_report_{client_info['name']}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            help="Click to download your detailed progress report including charts and analysis"
                        )
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

    with tabs[3]:
        st.markdown("## 🥗 Personalized Diet Planning")
        
        col1, col2 = st.columns(2)
        with col1:
            client_info['height'] = st.number_input("Height (cm)", 140, 220, value=170)
            client_info['weight'] = st.number_input("Weight (kg)", 30, 200, value=70)
            client_info['target_weight'] = st.number_input("Target Weight (kg)", 30, 200, value=client_info['weight'])
            client_info['meal_prep_time'] = st.select_slider(
                "Available Meal Prep Time (minutes/day)",
                options=[15, 30, 45, 60, 90, 120],
                value=30
            )

        with col2:
            client_info['dietary_restrictions'] = st.multiselect(
                "Dietary Restrictions",
                ["None", "Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", "Keto", "Paleo"],
                default=["None"]
            )
            client_info['food_allergies'] = st.text_area("Food Allergies (if any)")
            client_info['preferred_cuisine'] = st.multiselect(
                "Preferred Cuisine Types",
                ["Mediterranean", "Asian", "Indian", "Mexican", "American", "European"],
                default=["Mediterranean"]
            )

        col3, col4 = st.columns(2)
        with col3:
            client_info['medical_conditions'] = st.text_area("Medical Conditions (if any)")
            client_info['digestive_issues'] = st.text_area("Digestive Issues (if any)")

        with col4:
            client_info['health_goals'] = st.multiselect(
                "Health Goals",
                ["Weight Loss", "Muscle Gain", "Maintenance", "Energy Boost", 
                 "Better Sleep", "Digestive Health", "Reduce Inflammation"],
                default=["Maintenance"]
            )
            client_info['nutritional_needs'] = st.text_area("Specific Nutritional Needs")

        if st.button("Generate Personalized Diet Plan"):
            try:
                dietary_plan = generate_dietary_plan(client_info, st.session_state.before_data, st.session_state.after_data)
                
                # Display the plan in an organized way
                st.markdown("### Your Personalized Diet Plan")
                st.write(dietary_plan)

                # Generate PDF for diet plan and store in session state
                diet_pdf = create_diet_pdf(client_info, dietary_plan)
                
                # Store PDF data in session state
                st.session_state.diet_pdf = diet_pdf.getvalue()
                
                # Add PDF download button
                st.download_button(
                    label="📥 Download Diet Plan (PDF)",
                    data=st.session_state.diet_pdf,
                    file_name=f"diet_plan_{client_info['name']}_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    help="Click to download your personalized diet plan"
                )

            except Exception as e:
                st.error(f"An error occurred while generating the diet plan: {str(e)}")

if __name__ == "__main__":
    main() 
