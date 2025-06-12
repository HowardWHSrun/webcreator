from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import zipfile
import tempfile
from datetime import datetime
import re
import PyPDF2
import pdfplumber
from docx import Document
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class FileParser:
    @staticmethod
    def extract_text_from_pdf(file_path):
        """Extract text from PDF file"""
        text = ""
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except:
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            except:
                pass
        return text
    
    @staticmethod
    def extract_text_from_docx(file_path):
        """Extract text from DOCX file"""
        try:
            doc = Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except:
            return ""
    
    @staticmethod
    def extract_text_from_txt(file_path):
        """Extract text from TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except:
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except:
                return ""

class ResumeParser:
    def parse_resume_text(self, resume_text):
        """Parse resume text and extract structured information"""
        data = {
            'name': '',
            'title': '',
            'email': '',
            'phone': '',
            'location': '',
            'linkedin': '',
            'github': '',
            'website': '',
            'summary': '',
            'experience': [],
            'education': [],
            'skills': [],
            'projects': []
        }
        
        lines = resume_text.split('\n')
        current_section = None
        
        # Extract basic contact info
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'[\+]?[1-9]?[\d\-\(\)\s]{10,}'
        linkedin_pattern = r'linkedin\.com/in/[\w\-]+'
        github_pattern = r'github\.com/[\w\-]+'
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Extract name (usually first non-empty line)
            if not data['name'] and i < 3:
                if not re.search(email_pattern, line) and not re.search(phone_pattern, line):
                    data['name'] = line
                    continue
            
            # Extract contact information
            email_match = re.search(email_pattern, line)
            if email_match:
                data['email'] = email_match.group()
            
            phone_match = re.search(phone_pattern, line)
            if phone_match:
                data['phone'] = phone_match.group().strip()
            
            linkedin_match = re.search(linkedin_pattern, line)
            if linkedin_match:
                data['linkedin'] = 'https://' + linkedin_match.group()
            
            github_match = re.search(github_pattern, line)
            if github_match:
                data['github'] = 'https://' + github_match.group()
            
            # Identify sections
            line_lower = line.lower()
            if 'experience' in line_lower or 'work history' in line_lower:
                current_section = 'experience'
                continue
            elif 'education' in line_lower:
                current_section = 'education'
                continue
            elif 'skills' in line_lower:
                current_section = 'skills'
                continue
            elif 'projects' in line_lower:
                current_section = 'projects'
                continue
            elif 'summary' in line_lower or 'objective' in line_lower:
                current_section = 'summary'
                continue
            
            # Parse section content
            if current_section == 'summary' and not data['summary']:
                if line and not any(keyword in line_lower for keyword in ['summary', 'objective']):
                    data['summary'] = line
            elif current_section == 'skills':
                if line and not 'skills' in line_lower:
                    skills = re.split(r'[,•\-\n]', line)
                    for skill in skills:
                        skill = skill.strip()
                        if skill and skill not in data['skills']:
                            data['skills'].append(skill)
            elif current_section == 'experience':
                if line and len(line) > 10:
                    data['experience'].append({
                        'title': line,
                        'company': '',
                        'duration': '',
                        'description': ''
                    })
            elif current_section == 'education':
                if line and len(line) > 5:
                    data['education'].append({
                        'degree': line,
                        'school': '',
                        'year': ''
                    })
        
        if not data['title'] and data['experience']:
            first_job = data['experience'][0]['title']
            data['title'] = first_job.split(',')[0].split('at')[0].strip()
        
        return data

class WebsiteGenerator:
    def generate_website(self, resume_data, template='modern'):
        """Generate website files based on resume data and template"""
        templates = {
            'modern': self.generate_modern_template,
            'minimal': self.generate_minimal_template,
            'creative': self.generate_creative_template,
            'artistic': self.generate_artistic_template
        }
        return templates.get(template, self.generate_modern_template)(resume_data)
    
    def generate_modern_template(self, data):
        """Generate stunning modern template with interactive effects"""
        # Prepare dynamic sections first to avoid nested triple quotes issues
        experiences_html = '\n'.join([
            f'''<div class="timeline-item">
                    <div class="timeline-content">
                        <span class="timeline-date">Recent</span>
                        <h3>{exp['title']}</h3>
                        <h4>{exp.get('company', 'Professional Experience')}</h4>
                        <p>{exp.get('description', 'Contributed to meaningful projects and achieved significant results through dedication and expertise.')}</p>
                    </div>
                </div>''' for exp in (data.get('experience')[:4] if data.get('experience') else [{'title': 'Professional Experience'}])
        ])

        skills_html = ''.join([
            f'<div class="skill-item"><span>{skill}</span></div>' for skill in (data.get('skills') if data.get('skills') else ['Professional Skills', 'Problem Solving', 'Team Collaboration', 'Innovation', 'Leadership', 'Communication'])
        ])

        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['name']} - Portfolio</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {{
            --primary: #6366f1;
            --primary-dark: #4338ca;
            --secondary: #ec4899;
            --accent: #f59e0b;
            --dark: #0f0f23;
            --light: #f8fafc;
            --gray: #64748b;
            --white: #ffffff;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html {{
            scroll-behavior: smooth;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            line-height: 1.6;
            color: var(--dark);
            overflow-x: hidden;
            cursor: none;
        }}
        
        /* Custom Cursor */
        .cursor {{
            position: fixed;
            width: 20px;
            height: 20px;
            background: var(--primary);
            border-radius: 50%;
            pointer-events: none;
            z-index: 9999;
            transition: transform 0.2s ease;
            mix-blend-mode: difference;
        }}
        
        .cursor-follower {{
            position: fixed;
            width: 40px;
            height: 40px;
            border: 2px solid var(--primary);
            border-radius: 50%;
            pointer-events: none;
            z-index: 9998;
            transition: transform 0.3s ease;
            opacity: 0.6;
        }}
        
        /* Navigation */
        .navbar {{
            position: fixed;
            top: 0;
            width: 100%;
            background: rgba(248, 250, 252, 0.8);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(99, 102, 241, 0.1);
            z-index: 1000;
            transition: all 0.3s ease;
        }}
        
        .nav-container {{
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 2rem;
        }}
        
        .nav-logo {{
            font-size: 1.5rem;
            font-weight: 800;
            color: var(--dark);
            text-decoration: none;
        }}
        
        .nav-menu {{
            display: flex;
            gap: 2rem;
            list-style: none;
        }}
        
        .nav-link {{
            text-decoration: none;
            color: var(--gray);
            font-weight: 500;
            transition: all 0.3s ease;
            position: relative;
        }}
        
        .nav-link::after {{
            content: '';
            position: absolute;
            bottom: -5px;
            left: 0;
            width: 0;
            height: 2px;
            background: var(--primary);
            transition: width 0.3s ease;
        }}
        
        .nav-link:hover {{
            color: var(--primary);
        }}
        
        .nav-link:hover::after {{
            width: 100%;
        }}
        
        /* Hero Section */
        .hero {{
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            background: linear-gradient(135deg, var(--light) 0%, #e0e7ff 50%, #fdf2f8 100%);
            overflow: hidden;
        }}
        
        .hero::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="%236366f1" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="%23ec4899" opacity="0.1"/><circle cx="75" cy="25" r="1" fill="%236366f1" opacity="0.1"/><circle cx="25" cy="75" r="1" fill="%23ec4899" opacity="0.1"/></pattern></defs><rect width="100%" height="100%" fill="url(%23grain)"/></svg>');
            opacity: 0.6;
            animation: float 20s ease-in-out infinite;
        }}
        
        .particles {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
        }}
        
        .particle {{
            position: absolute;
            background: var(--primary);
            border-radius: 50%;
            animation: float-particle 8s ease-in-out infinite;
            opacity: 0.3;
        }}
        
        .hero-content {{
            text-align: center;
            z-index: 2;
            max-width: 800px;
            padding: 0 2rem;
        }}
        
        .hero-subtitle {{
            font-size: 1.5rem;
            color: var(--primary);
            font-weight: 600;
            margin-bottom: 1rem;
            opacity: 0;
            animation: fadeInUp 1s ease 0.2s forwards;
        }}
        
        .hero-title {{
            font-family: 'Playfair Display', serif;
            font-size: clamp(3rem, 8vw, 6rem);
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 2rem;
            background: linear-gradient(135deg, var(--dark), var(--primary), var(--secondary));
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            opacity: 0;
            animation: fadeInUp 1s ease 0.4s forwards;
        }}
        
        .hero-description {{
            font-size: 1.25rem;
            color: var(--gray);
            margin-bottom: 3rem;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
            opacity: 0;
            animation: fadeInUp 1s ease 0.6s forwards;
        }}
        
        .hero-buttons {{
            display: flex;
            gap: 1.5rem;
            justify-content: center;
            flex-wrap: wrap;
            opacity: 0;
            animation: fadeInUp 1s ease 0.8s forwards;
        }}
        
        .btn {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 1rem 2rem;
            border: none;
            border-radius: 50px;
            font-size: 1rem;
            font-weight: 600;
            text-decoration: none;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            cursor: none;
        }}
        
        .btn::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.5s ease;
        }}
        
        .btn:hover::before {{
            left: 100%;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: var(--white);
            box-shadow: 0 10px 30px rgba(99, 102, 241, 0.3);
        }}
        
        .btn-primary:hover {{
            transform: translateY(-3px);
            box-shadow: 0 20px 40px rgba(99, 102, 241, 0.4);
        }}
        
        .btn-secondary {{
            background: transparent;
            color: var(--dark);
            border: 2px solid var(--primary);
        }}
        
        .btn-secondary:hover {{
            background: var(--primary);
            color: var(--white);
            transform: translateY(-3px);
        }}
        
        /* Sections */
        .section {{
            padding: 8rem 0;
            position: relative;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
        }}
        
        .section-title {{
            font-family: 'Playfair Display', serif;
            font-size: clamp(2.5rem, 5vw, 4rem);
            font-weight: 700;
            text-align: center;
            margin-bottom: 4rem;
            color: var(--dark);
            position: relative;
        }}
        
        .section-title::after {{
            content: '';
            position: absolute;
            bottom: -1rem;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 4px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border-radius: 2px;
        }}
        
        /* About Section */
        .about {{
            background: var(--white);
        }}
        
        .about-grid {{
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 4rem;
            align-items: center;
        }}
        
        .about-image {{
            position: relative;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        
        .about-image::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            opacity: 0.1;
            z-index: 1;
        }}
        
        .about-content {{
            font-size: 1.1rem;
            line-height: 1.8;
            color: var(--gray);
        }}
        
        .about-content p:first-child {{
            font-size: 1.25rem;
            color: var(--dark);
            font-weight: 500;
        }}
        
        /* Experience Section */
        .experience {{
            background: linear-gradient(135deg, var(--light), #f1f5f9);
        }}
        
        .timeline {{
            position: relative;
            max-width: 800px;
            margin: 0 auto;
        }}
        
        .timeline::before {{
            content: '';
            position: absolute;
            left: 50%;
            top: 0;
            bottom: 0;
            width: 2px;
            background: linear-gradient(180deg, var(--primary), var(--secondary));
            transform: translateX(-50%);
        }}
        
        .timeline-item {{
            position: relative;
            margin-bottom: 4rem;
            width: 45%;
        }}
        
        .timeline-item:nth-child(odd) {{
            margin-left: 0;
        }}
        
        .timeline-item:nth-child(even) {{
            margin-left: 55%;
        }}
        
        .timeline-item::before {{
            content: '';
            position: absolute;
            width: 20px;
            height: 20px;
            background: var(--primary);
            border: 4px solid var(--white);
            border-radius: 50%;
            top: 1rem;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        }}
        
        .timeline-item:nth-child(odd)::before {{
            right: -60px;
        }}
        
        .timeline-item:nth-child(even)::before {{
            left: -60px;
        }}
        
        .timeline-content {{
            background: var(--white);
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }}
        
        .timeline-content:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        
        .timeline-content h3 {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--dark);
            margin-bottom: 0.5rem;
        }}
        
        .timeline-content h4 {{
            color: var(--primary);
            font-weight: 600;
            margin-bottom: 1rem;
        }}
        
        .timeline-date {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: var(--white);
            padding: 0.25rem 1rem;
            border-radius: 15px;
            font-size: 0.875rem;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 1rem;
        }}
        
        /* Skills Section */
        .skills {{
            background: var(--white);
        }}
        
        .skills-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
        }}
        
        .skill-item {{
            background: linear-gradient(135deg, var(--white), var(--light));
            padding: 2rem 1.5rem;
            border-radius: 15px;
            text-align: center;
            font-weight: 600;
            border: 2px solid transparent;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            cursor: none;
        }}
        
        .skill-item::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            opacity: 0;
            transition: opacity 0.3s ease;
        }}
        
        .skill-item span {{
            position: relative;
            z-index: 1;
            transition: color 0.3s ease;
        }}
        
        .skill-item:hover {{
            transform: translateY(-5px) scale(1.05);
            box-shadow: 0 20px 40px rgba(99, 102, 241, 0.2);
        }}
        
        .skill-item:hover::before {{
            opacity: 1;
        }}
        
        .skill-item:hover span {{
            color: var(--white);
        }}
        
        /* Contact Section */
        .contact {{
            background: linear-gradient(135deg, var(--dark), #1e1b4b);
            color: var(--white);
        }}
        
        .contact .section-title {{
            color: var(--white);
        }}
        
        .contact-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 4rem;
            align-items: center;
        }}
        
        .contact-info {{
            space-y: 2rem;
        }}
        
        .contact-item {{
            display: flex;
            align-items: center;
            gap: 1.5rem;
            margin-bottom: 2rem;
            font-size: 1.1rem;
        }}
        
        .contact-item i {{
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
        }}
        
        .contact-item a {{
            color: var(--white);
            text-decoration: none;
            transition: color 0.3s ease;
        }}
        
        .contact-item a:hover {{
            color: var(--accent);
        }}
        
        .contact-cta {{
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            padding: 3rem;
            border-radius: 20px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        
        .contact-cta h3 {{
            font-size: 2rem;
            margin-bottom: 1rem;
        }}
        
        .contact-cta p {{
            font-size: 1.1rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }}
        
        /* Footer */
        .footer {{
            background: var(--dark);
            color: var(--white);
            text-align: center;
            padding: 2rem 0;
            border-top: 1px solid rgba(255,255,255,0.1);
        }}
        
        /* Animations */
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        @keyframes float {{
            0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
            50% {{ transform: translateY(-10px) rotate(5deg); }}
        }}
        
        @keyframes float-particle {{
            0%, 100% {{ transform: translateY(0px) translateX(0px); opacity: 0.3; }}
            25% {{ transform: translateY(-20px) translateX(10px); opacity: 0.6; }}
            50% {{ transform: translateY(-10px) translateX(-5px); opacity: 0.4; }}
            75% {{ transform: translateY(-30px) translateX(15px); opacity: 0.7; }}
        }}
        
        /* Responsive */
        @media (max-width: 768px) {{
            .nav-menu {{
                display: none;
            }}
            
            .hero-buttons {{
                flex-direction: column;
                align-items: center;
            }}
            
            .about-grid, .contact-grid {{
                grid-template-columns: 1fr;
                gap: 2rem;
            }}
            
            .timeline::before {{
                left: 1.5rem;
            }}
            
            .timeline-item {{
                width: calc(100% - 4rem);
                margin-left: 4rem !important;
            }}
            
            .timeline-item::before {{
                left: -2.5rem !important;
            }}
            
            .cursor, .cursor-follower {{
                display: none;
            }}
            
            body {{
                cursor: default;
            }}
            
            .btn, .skill-item {{
                cursor: pointer;
            }}
        }}
    </style>
</head>
<body>
    <div class="cursor"></div>
    <div class="cursor-follower"></div>
    
    <nav class="navbar">
        <div class="nav-container">
            <a href="#home" class="nav-logo">{data['name']}</a>
            <ul class="nav-menu">
                <li><a href="#about" class="nav-link">About</a></li>
                <li><a href="#experience" class="nav-link">Experience</a></li>
                <li><a href="#skills" class="nav-link">Skills</a></li>
                <li><a href="#contact" class="nav-link">Contact</a></li>
            </ul>
        </div>
    </nav>

    <section id="home" class="hero">
        <div class="particles"></div>
        <div class="hero-content">
            <h2 class="hero-subtitle">{data['title'] or 'Professional'}</h2>
            <h1 class="hero-title">{data['name']}</h1>
            <p class="hero-description">{data['summary'] or 'Passionate professional dedicated to delivering exceptional results and driving innovation in every project.'}</p>
            <div class="hero-buttons">
                <a href="#contact" class="btn btn-primary">
                    <i class="fas fa-envelope"></i>
                    Get In Touch
                </a>
                <a href="#experience" class="btn btn-secondary">
                    <i class="fas fa-briefcase"></i>
                    View My Work
                </a>
            </div>
        </div>
    </section>

    <section id="about" class="section about">
        <div class="container">
            <h2 class="section-title">About Me</h2>
            <div class="about-grid">
                <div class="about-image">
                    <div style="width: 100%; height: 400px; background: linear-gradient(135deg, var(--primary), var(--secondary)); border-radius: 20px; display: flex; align-items: center; justify-content: center; color: white; font-size: 4rem;">
                        <i class="fas fa-user"></i>
                    </div>
                </div>
                <div class="about-content">
                    <p>{data['summary'] or 'I am a passionate professional with a dedication to excellence and innovation.'}</p>
                    <p>With expertise in my field and a commitment to continuous learning, I strive to deliver exceptional results that exceed expectations. My approach combines creativity with technical precision, ensuring every project is both innovative and practical.</p>
                    <p>I believe in the power of collaboration and am always eager to take on new challenges that push the boundaries of what's possible.</p>
                </div>
            </div>
        </div>
    </section>

    <section id="experience" class="section experience">
        <div class="container">
            <h2 class="section-title">Experience</h2>
            <div class="timeline">
                {experiences_html}
            </div>
        </div>
    </section>

    <section id="skills" class="section skills">
        <div class="container">
            <h2 class="section-title">Skills & Expertise</h2>
            <div class="skills-grid">
                {skills_html}
            </div>
        </div>
    </section>

    <section id="contact" class="section contact">
        <div class="container">
            <h2 class="section-title">Let's Work Together</h2>
            <div class="contact-grid">
                <div class="contact-info">
                    {f'<div class="contact-item"><i class="fas fa-envelope"></i><a href="mailto:{data["email"]}">{data["email"]}</a></div>' if data['email'] else ''}
                    {f'<div class="contact-item"><i class="fas fa-phone"></i><span>{data["phone"]}</span></div>' if data['phone'] else ''}
                    {f'<div class="contact-item"><i class="fab fa-linkedin"></i><a href="{data["linkedin"]}" target="_blank">LinkedIn Profile</a></div>' if data['linkedin'] else ''}
                    {f'<div class="contact-item"><i class="fab fa-github"></i><a href="{data["github"]}" target="_blank">GitHub Profile</a></div>' if data['github'] else ''}
                </div>
                <div class="contact-cta">
                    <h3>Ready to Start a Project?</h3>
                    <p>Let's discuss how we can work together to bring your ideas to life.</p>
                    <a href="mailto:{data['email'] or 'contact@example.com'}" class="btn btn-primary">
                        <i class="fas fa-paper-plane"></i>
                        Send Message
                    </a>
                </div>
            </div>
        </div>
    </section>

    <footer class="footer">
        <div class="container">
            <p>&copy; {datetime.now().year} {data['name']}. Crafted with passion and precision.</p>
        </div>
    </footer>

    <script>
        // Custom Cursor
        const cursor = document.querySelector('.cursor');
        const cursorFollower = document.querySelector('.cursor-follower');
        
        document.addEventListener('mousemove', (e) => {{
            cursor.style.transform = `translate(${{e.clientX - 10}}px, ${{e.clientY - 10}}px)`;
            cursorFollower.style.transform = `translate(${{e.clientX - 20}}px, ${{e.clientY - 20}}px)`;
        }});
        
        // Particle System
        function createParticles() {{
            const particles = document.querySelector('.particles');
            for (let i = 0; i < 50; i++) {{
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.top = Math.random() * 100 + '%';
                particle.style.width = Math.random() * 4 + 2 + 'px';
                particle.style.height = particle.style.width;
                particle.style.animationDelay = Math.random() * 8 + 's';
                particle.style.animationDuration = (Math.random() * 8 + 4) + 's';
                particles.appendChild(particle);
            }}
        }}
        
        // Smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{
                        behavior: 'smooth',
                        block: 'start'
                    }});
                }}
            }});
        }});
        
        // Navbar background on scroll
        window.addEventListener('scroll', () => {{
            const navbar = document.querySelector('.navbar');
            if (window.scrollY > 100) {{
                navbar.style.background = 'rgba(248, 250, 252, 0.95)';
                navbar.style.boxShadow = '0 4px 30px rgba(0, 0, 0, 0.1)';
            }} else {{
                navbar.style.background = 'rgba(248, 250, 252, 0.8)';
                navbar.style.boxShadow = 'none';
            }}
        }});
        
        // Initialize particles
        createParticles();
        
        // Intersection Observer for animations
        const observerOptions = {{
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        }};
        
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }}
            }});
        }}, observerOptions);
        
        // Observe timeline items and skill items
        document.querySelectorAll('.timeline-item, .skill-item').forEach(item => {{
            item.style.opacity = '0';
            item.style.transform = 'translateY(30px)';
            item.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(item);
        }});
    </script>
</body>
</html>'''

        css_content = '''* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #fff;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

.navbar {
    position: fixed;
    top: 0;
    width: 100%;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid #e1e1e1;
    z-index: 1000;
}

.nav-container {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 0;
}

.nav-logo {
    font-size: 1.5rem;
    font-weight: 700;
    color: #2563eb;
}

.nav-menu {
    display: flex;
    gap: 2rem;
}

.nav-link {
    text-decoration: none;
    color: var(--text);
    font-weight: 500;
    transition: all 0.3s ease;
}

.nav-link:hover {
    color: var(--primary);
}

.hero {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    text-align: center;
}

.hero-content {
    max-width: 800px;
    padding: 0 2rem;
}

.hero-title {
    font-size: 4rem;
    font-weight: 700;
    margin-bottom: 1rem;
}

.hero-subtitle {
    font-size: 1.5rem;
    font-weight: 400;
    margin-bottom: 2rem;
}

.hero-description {
    font-size: 1.1rem;
    margin-bottom: 3rem;
}

.hero-buttons {
    display: flex;
    gap: 1rem;
    justify-content: center;
}

.btn {
    padding: 1rem 2rem;
    border: none;
    border-radius: 50px;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.3s ease;
    cursor: pointer;
}

.btn-primary {
    background: #fff;
    color: #2563eb;
}

.btn-secondary {
    background: transparent;
    color: #fff;
    border: 2px solid #fff;
}

section {
    padding: 5rem 0;
}

.section-title {
    font-size: 2.5rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: 3rem;
    color: var(--accent);
}

.about {
    background-color: #f8fafc;
}

.about-content {
    max-width: 800px;
    margin: 0 auto;
    text-align: center;
    font-size: 1.1rem;
    line-height: 1.8;
}

.timeline {
    position: relative;
    max-width: 800px;
    margin: 0 auto;
}

.timeline-item {
    padding: 10px 40px;
    position: relative;
    background-color: inherit;
    width: 100%;
}

.timeline-content {
    padding: 20px 30px;
    background-color: white;
    position: relative;
    border-radius: 10px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    margin-bottom: 2rem;
}

.timeline-content h3 {
    font-size: 1.2rem;
    color: var(--accent);
    margin-bottom: 0.5rem;
}

.skills-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
    max-width: 800px;
    margin: 0 auto;
}

.skill-item {
    background: var(--accent);
    color: white;
    padding: 1rem;
    text-align: center;
    border-radius: 50px;
    font-weight: 500;
    transition: transform 0.3s ease;
}

.contact {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.contact .section-title {
    color: white;
}

.contact-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 4rem;
    align-items: center;
}

.contact-info {
    display: grid;
    gap: 2rem;
}

.contact-item {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.contact-item a {
    color: var(--text);
    text-decoration: none;
    transition: color 0.3s ease;
}

.contact-item a:hover {
    color: var(--accent);
}

.contact-cta {
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    padding: 3rem;
    border-radius: 20px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.2);
}

.contact-cta h3 {
    font-size: 2rem;
    margin-bottom: 1rem;
}

.contact-cta p {
    font-size: 1.1rem;
    margin-bottom: 2rem;
    opacity: 0.9;
}

.footer {
    background: #1f2937;
    color: white;
    text-align: center;
    padding: 2rem 0;
}

@media (max-width: 768px) {
    .nav-menu {
        display: none;
    }
    
    .hero-title {
        font-size: 2.5rem;
    }
    
    .hero-buttons {
        flex-direction: column;
        align-items: center;
    }
}'''

        js_content = '''document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({{
                    behavior: 'smooth'
                }});
            }});
        }});

        window.addEventListener('scroll', () => {{
            const navbar = document.querySelector('.navbar');
            if (window.scrollY > 100) {{
                navbar.style.background = 'rgba(255, 255, 255, 0.98)';
            }} else {{
                navbar.style.background = 'rgba(255, 255, 255, 0.95)';
            }}
        }});'''

        return {
            'index.html': html_content,
            'style.css': css_content,
            'script.js': js_content
        }

    def generate_minimal_template(self, data):
        """Generate clean and minimal template focused on content"""
        # Prepare dynamic sections
        experiences_html = '\n'.join([
            f'''<div class="experience-card">
                    <div class="experience-header">
                        <h3 class="experience-title">{exp['title']}</h3>
                        <span class="company-name">{exp.get('company', '')}</span>
                    </div>
                    <p class="experience-desc">{exp.get('description', '')}</p>
                </div>''' for exp in (data.get('experience', []) or [{'title': 'Professional Experience'}])
        ])

        skills_html = ''.join([
            f'<div class="skill-bubble">{skill}</div>' for skill in (data.get('skills', []) or ['Creative Design', 'Innovation', 'Problem Solving'])
        ])

        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['name']} - Creative Portfolio</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --gradient-1: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            --gradient-2: linear-gradient(135deg, #ec4899 0%, #f43f5e 100%);
            --gradient-3: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
            --dark: #0f172a;
            --light: #f8f8f8;
            --border: #e0e0e0;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        html {{
            scroll-behavior: smooth;
        }}

        body {{
            font-family: 'Poppins', sans-serif;
            color: var(--primary);
            background: var(--light);
            overflow-x: hidden;
        }}

        /* Grid Background */
        .grid-bg {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            opacity: 0.3;
            background-image: 
                linear-gradient(var(--border) 1px, transparent 1px),
                linear-gradient(90deg, var(--border) 1px, transparent 1px);
            background-size: 50px 50px;
        }}

        /* Typography */
        h1, h2, h3 {{
            font-family: 'Cormorant Garamond', serif;
            font-weight: 600;
            line-height: 1.2;
        }}

        h1 {{
            font-size: clamp(3rem, 10vw, 6rem);
            margin-bottom: 1rem;
        }}

        h2 {{
            font-size: 2.5rem;
            margin-bottom: 3rem;
            position: relative;
        }}

        h2::after {{
            content: '';
            position: absolute;
            bottom: -10px;
            left: 0;
            width: 60px;
            height: 2px;
            background: var(--accent);
        }}

        /* Layout */
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 2rem;
        }}

        /* Navigation */
        .nav {{
            position: fixed;
            top: 50%;
            right: 2rem;
            transform: translateY(-50%);
            z-index: 100;
        }}

        .nav-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 2rem;
        }}

        .nav-item {{
            position: relative;
        }}

        .nav-link {{
            text-decoration: none;
            color: var(--secondary);
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 2px;
            transition: color 0.3s ease;
            padding-right: 30px;
        }}

        .nav-link::after {{
            content: '';
            position: absolute;
            top: 50%;
            right: 0;
            width: 20px;
            height: 1px;
            background: var(--secondary);
            transition: width 0.3s ease, background 0.3s ease;
        }}

        .nav-link:hover {{
            color: var(--accent);
        }}

        .nav-link:hover::after {{
            width: 40px;
            background: var(--accent);
        }}

        /* Sections */
        section {{
            min-height: 100vh;
            display: flex;
            align-items: center;
            padding: 6rem 0;
        }}

        /* Hero Section */
        .hero {{
            position: relative;
        }}

        .hero-content {{
            max-width: 800px;
        }}

        .hero-title {{
            opacity: 0;
            animation: fadeIn 1s ease forwards;
        }}

        .hero-subtitle {{
            font-size: 1.25rem;
            color: var(--secondary);
            margin-bottom: 2rem;
            max-width: 600px;
            opacity: 0;
            animation: fadeIn 1s ease 0.3s forwards;
        }}

        /* Experience Section */
        .experience-item {{
            display: grid;
            grid-template-columns: 80px 1fr;
            gap: 2rem;
            margin-bottom: 4rem;
            opacity: 0;
            transform: translateX(-20px);
            animation: slideIn 0.6s ease forwards;
        }}

        .experience-number {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 2.5rem;
            color: var(--accent);
            opacity: 0.5;
        }}

        .experience-content h3 {{
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }}

        .company {{
            display: block;
            color: var(--secondary);
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 1rem;
        }}

        /* Skills Section */
        .skills-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
        }}

        .skill-item {{
            padding: 2rem;
            border: 1px solid var(--border);
            text-align: center;
            transition: all 0.3s ease;
            opacity: 0;
            transform: translateY(20px);
            animation: fadeInUp 0.6s ease forwards;
        }}

        .skill-item:hover {{
            border-color: var(--accent);
            transform: translateY(-5px);
        }}

        /* Contact Section */
        .contact-info {{
            display: grid;
            gap: 2rem;
            max-width: 500px;
        }}

        .contact-item {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}

        .contact-item a {{
            color: var(--primary);
            text-decoration: none;
            transition: color 0.3s ease;
        }}

        .contact-item a:hover {{
            color: var(--accent);
        }}

        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}

        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateX(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        /* Responsive Design */
        @media (max-width: 768px) {{
            .nav {{
                position: fixed;
                top: 0;
                right: 0;
                left: 0;
                transform: none;
                background: var(--background);
                padding: 1rem 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}

            .nav-list {{
                flex-direction: row;
                justify-content: center;
                gap: 1.5rem;
            }}

            .nav-link {{
                padding-right: 0;
            }}

            .nav-link::after {{
                display: none;
            }}

            section {{
                padding: 4rem 0;
            }}

            .experience-item {{
                grid-template-columns: 1fr;
                gap: 1rem;
            }}

            .experience-number {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="grid-bg"></div>

    <nav class="nav">
        <ul class="nav-list">
            <li class="nav-item"><a href="#about" class="nav-link">About</a></li>
            <li class="nav-item"><a href="#experience" class="nav-link">Experience</a></li>
            <li class="nav-item"><a href="#skills" class="nav-link">Skills</a></li>
            <li class="nav-item"><a href="#contact" class="nav-link">Contact</a></li>
        </ul>
    </nav>

    <section id="about" class="hero">
        <div class="container">
            <div class="hero-content">
                <h1 class="hero-title">{data['name']}</h1>
                <p class="hero-subtitle">{data.get('summary', 'A creative professional pushing the boundaries of innovation and design.')}</p>
            </div>
        </div>
    </section>

    <section id="experience">
        <div class="container">
            <h2>Experience</h2>
            {experiences_html}
        </div>
    </section>

    <section id="skills">
        <div class="container">
            <h2>Skills</h2>
            <div class="skills-grid">
                {skills_html}
            </div>
        </div>
    </section>

    <section id="contact">
        <div class="container">
            <h2>Connect</h2>
            <div class="contact-info">
                {f'<div class="contact-item"><span>📧</span><a href="mailto:{data["email"]}">{data["email"]}</a></div>' if data.get('email') else ''}
                {f'<div class="contact-item"><span>📱</span><span>{data["phone"]}</span></div>' if data.get('phone') else ''}
                {f'<div class="contact-item"><span>💼</span><a href="{data["linkedin"]}" target="_blank">LinkedIn Profile</a></div>' if data.get('linkedin') else ''}
                {f'<div class="contact-item"><span>💻</span><a href="{data["github"]}" target="_blank">GitHub Profile</a></div>' if data.get('github') else ''}
            </div>
        </div>
    </section>

    <script>
        // Smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({{
                    behavior: 'smooth'
                }});
            }});
        }});

        // Active section highlighting
        const sections = document.querySelectorAll('section');
        const navLinks = document.querySelectorAll('.nav-link');

        window.addEventListener('scroll', () => {{
            let current = '';
            sections.forEach(section => {{
                const sectionTop = section.offsetTop;
                const sectionHeight = section.clientHeight;
                if (scrollY >= sectionTop - 200) {{
                    current = section.getAttribute('id');
                }}
            }});

            navLinks.forEach(link => {{
                link.style.color = link.getAttribute('href').slice(1) === current ? 'var(--accent)' : 'var(--secondary)';
            }});
        }});

        // Animation on scroll
        const observerOptions = {{
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        }};

        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }}
            }});
        }}, observerOptions);

        document.querySelectorAll('.experience-item, .skill-item').forEach(el => {{
            observer.observe(el);
        }});
    </script>
</body>
</html>'''

        css_content = '''/* Creative template styles are included in the HTML */'''
        
        js_content = '''/* Creative template scripts are included in the HTML */'''

        return {
            'index.html': html_content,
            'style.css': css_content,
            'script.js': js_content
        }

    def generate_creative_template(self, data):
        """Generate bold and creative template"""
        # Prepare dynamic sections
        experiences_html = '\n'.join([
            f'''<div class="experience-card">
                    <div class="experience-header">
                        <h3 class="experience-title">{exp['title']}</h3>
                        <span class="company-name">{exp.get('company', '')}</span>
                    </div>
                    <p class="experience-desc">{exp.get('description', '')}</p>
                </div>''' for exp in (data.get('experience', []) or [{'title': 'Professional Experience'}])
        ])

        skills_html = ''.join([
            f'<div class="skill-bubble">{skill}</div>' for skill in (data.get('skills', []) or ['Creative Design', 'Innovation', 'Problem Solving'])
        ])

        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['name']} - Creative Portfolio</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --gradient-1: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            --gradient-2: linear-gradient(135deg, #ec4899 0%, #f43f5e 100%);
            --gradient-3: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%);
            --dark: #0f172a;
            --light: #f8f8f8;
            --border: #e0e0e0;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        html {{
            scroll-behavior: smooth;
        }}

        body {{
            font-family: 'Poppins', sans-serif;
            color: var(--primary);
            background: var(--light);
            overflow-x: hidden;
        }}

        /* Grid Background */
        .grid-bg {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            opacity: 0.3;
            background-image: 
                linear-gradient(var(--border) 1px, transparent 1px),
                linear-gradient(90deg, var(--border) 1px, transparent 1px);
            background-size: 50px 50px;
        }}

        /* Typography */
        h1, h2, h3 {{
            font-family: 'Cormorant Garamond', serif;
            font-weight: 600;
            line-height: 1.2;
        }}

        h1 {{
            font-size: clamp(3rem, 10vw, 6rem);
            margin-bottom: 1rem;
        }}

        h2 {{
            font-size: 2.5rem;
            margin-bottom: 3rem;
            position: relative;
        }}

        h2::after {{
            content: '';
            position: absolute;
            bottom: -10px;
            left: 0;
            width: 60px;
            height: 2px;
            background: var(--accent);
        }}

        /* Layout */
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 2rem;
        }}

        /* Navigation */
        .nav {{
            position: fixed;
            top: 50%;
            right: 2rem;
            transform: translateY(-50%);
            z-index: 100;
        }}

        .nav-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 2rem;
        }}

        .nav-item {{
            position: relative;
        }}

        .nav-link {{
            text-decoration: none;
            color: var(--secondary);
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 2px;
            transition: color 0.3s ease;
            padding-right: 30px;
        }}

        .nav-link::after {{
            content: '';
            position: absolute;
            top: 50%;
            right: 0;
            width: 20px;
            height: 1px;
            background: var(--secondary);
            transition: width 0.3s ease, background 0.3s ease;
        }}

        .nav-link:hover {{
            color: var(--accent);
        }}

        .nav-link:hover::after {{
            width: 40px;
            background: var(--accent);
        }}

        /* Sections */
        section {{
            min-height: 100vh;
            display: flex;
            align-items: center;
            padding: 6rem 0;
        }}

        /* Hero Section */
        .hero {{
            position: relative;
        }}

        .hero-content {{
            max-width: 800px;
        }}

        .hero-title {{
            opacity: 0;
            animation: fadeIn 1s ease forwards;
        }}

        .hero-subtitle {{
            font-size: 1.25rem;
            color: var(--secondary);
            margin-bottom: 2rem;
            max-width: 600px;
            opacity: 0;
            animation: fadeIn 1s ease 0.3s forwards;
        }}

        /* Experience Section */
        .experience-item {{
            display: grid;
            grid-template-columns: 80px 1fr;
            gap: 2rem;
            margin-bottom: 4rem;
            opacity: 0;
            transform: translateX(-20px);
            animation: slideIn 0.6s ease forwards;
        }}

        .experience-number {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 2.5rem;
            color: var(--accent);
            opacity: 0.5;
        }}

        .experience-content h3 {{
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }}

        .company {{
            display: block;
            color: var(--secondary);
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 1rem;
        }}

        /* Skills Section */
        .skills-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
        }}

        .skill-item {{
            padding: 2rem;
            border: 1px solid var(--border);
            text-align: center;
            transition: all 0.3s ease;
            opacity: 0;
            transform: translateY(20px);
            animation: fadeInUp 0.6s ease forwards;
        }}

        .skill-item:hover {{
            border-color: var(--accent);
            transform: translateY(-5px);
        }}

        /* Contact Section */
        .contact-info {{
            display: grid;
            gap: 2rem;
            max-width: 500px;
        }}

        .contact-item {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}

        .contact-item a {{
            color: var(--primary);
            text-decoration: none;
            transition: color 0.3s ease;
        }}

        .contact-item a:hover {{
            color: var(--accent);
        }}

        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}

        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateX(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        /* Responsive Design */
        @media (max-width: 768px) {{
            .nav {{
                position: fixed;
                top: 0;
                right: 0;
                left: 0;
                transform: none;
                background: var(--background);
                padding: 1rem 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}

            .nav-list {{
                flex-direction: row;
                justify-content: center;
                gap: 1.5rem;
            }}

            .nav-link {{
                padding-right: 0;
            }}

            .nav-link::after {{
                display: none;
            }}

            section {{
                padding: 4rem 0;
            }}

            .experience-item {{
                grid-template-columns: 1fr;
                gap: 1rem;
            }}

            .experience-number {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="grid-bg"></div>

    <nav class="nav">
        <ul class="nav-list">
            <li class="nav-item"><a href="#about" class="nav-link">About</a></li>
            <li class="nav-item"><a href="#experience" class="nav-link">Experience</a></li>
            <li class="nav-item"><a href="#skills" class="nav-link">Skills</a></li>
            <li class="nav-item"><a href="#contact" class="nav-link">Contact</a></li>
        </ul>
    </nav>

    <section id="about" class="hero">
        <div class="container">
            <div class="hero-content">
                <h1 class="hero-title">{data['name']}</h1>
                <p class="hero-subtitle">{data.get('summary', 'A creative professional crafting unique and memorable experiences through innovative design and creative solutions.')}</p>
            </div>
        </div>
    </section>

    <section id="experience">
        <div class="container">
            <h2>Experience</h2>
            {experiences_html}
        </div>
    </section>

    <section id="skills">
        <div class="container">
            <h2>Expertise</h2>
            <div class="skills-grid">
                {skills_html}
            </div>
        </div>
    </section>

    <section id="contact">
        <div class="container">
            <h2>Connect</h2>
            <div class="contact-info">
                {f'<div class="contact-item"><span>📧</span><a href="mailto:{data["email"]}">{data["email"]}</a></div>' if data.get('email') else ''}
                {f'<div class="contact-item"><span>📱</span><span>{data["phone"]}</span></div>' if data.get('phone') else ''}
                {f'<div class="contact-item"><span>💼</span><a href="{data["linkedin"]}" target="_blank">LinkedIn Profile</a></div>' if data.get('linkedin') else ''}
                {f'<div class="contact-item"><span>💻</span><a href="{data["github"]}" target="_blank">GitHub Profile</a></div>' if data.get('github') else ''}
            </div>
        </div>
    </section>

    <script>
        // Smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({{
                    behavior: 'smooth'
                }});
            }});
        }});

        // Active section highlighting
        const sections = document.querySelectorAll('section');
        const navLinks = document.querySelectorAll('.nav-link');

        window.addEventListener('scroll', () => {{
            let current = '';
            sections.forEach(section => {{
                const sectionTop = section.offsetTop;
                const sectionHeight = section.clientHeight;
                if (scrollY >= sectionTop - 200) {{
                    current = section.getAttribute('id');
                }}
            }});

            navLinks.forEach(link => {{
                link.style.color = link.getAttribute('href').slice(1) === current ? 'var(--accent)' : 'var(--secondary)';
            }});
        }});

        // Animation on scroll
        const observerOptions = {{
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        }};

        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }}
            }});
        }}, observerOptions);

        document.querySelectorAll('.experience-item, .skill-item').forEach(el => {{
            observer.observe(el);
        }});
    </script>
</body>
</html>'''

        css_content = '''/* Creative template styles are included in the HTML */'''
        
        js_content = '''/* Creative template scripts are included in the HTML */'''

        return {
            'index.html': html_content,
            'style.css': css_content,
            'script.js': js_content
        }

    def generate_artistic_template(self, data):
        """Generate unique and artistic template"""
        # Prepare dynamic sections
        experiences_html = '\n'.join([
            f'''<div class="experience-item">
                    <div class="experience-number">0{i+1}</div>
                    <div class="experience-content">
                        <h3>{exp['title']}</h3>
                        <span class="company">{exp.get('company', '')}</span>
                        <p>{exp.get('description', '')}</p>
                    </div>
                </div>''' for i, exp in enumerate(data.get('experience', []) or [{'title': 'Professional Experience'}])
        ])

        skills_html = ''.join([
            f'<div class="skill-item"><span>{skill}</span></div>' for skill in (data.get('skills', []) or ['Artistic Vision', 'Creative Design', 'Innovation'])
        ])

        html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['name']} - Artistic Portfolio</title>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=Montserrat:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #1a1a1a;
            --secondary: #4a4a4a;
            --accent: #c9a96e;
            --background: #ffffff;
            --light: #f8f8f8;
            --border: #e0e0e0;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        html {{
            scroll-behavior: smooth;
        }}

        body {{
            font-family: 'Montserrat', sans-serif;
            color: var(--primary);
            background: var(--background);
            line-height: 1.6;
        }}

        /* Grid Background */
        .grid-bg {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            opacity: 0.3;
            background-image: 
                linear-gradient(var(--border) 1px, transparent 1px),
                linear-gradient(90deg, var(--border) 1px, transparent 1px);
            background-size: 50px 50px;
        }}

        /* Typography */
        h1, h2, h3 {{
            font-family: 'Cormorant Garamond', serif;
            font-weight: 600;
            line-height: 1.2;
        }}

        h1 {{
            font-size: clamp(3rem, 10vw, 6rem);
            margin-bottom: 1rem;
        }}

        h2 {{
            font-size: 2.5rem;
            margin-bottom: 3rem;
            position: relative;
        }}

        h2::after {{
            content: '';
            position: absolute;
            bottom: -10px;
            left: 0;
            width: 60px;
            height: 2px;
            background: var(--accent);
        }}

        /* Layout */
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 2rem;
        }}

        /* Navigation */
        .nav {{
            position: fixed;
            top: 50%;
            right: 2rem;
            transform: translateY(-50%);
            z-index: 100;
        }}

        .nav-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 2rem;
        }}

        .nav-item {{
            position: relative;
        }}

        .nav-link {{
            text-decoration: none;
            color: var(--secondary);
            font-size: 0.875rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 2px;
            transition: color 0.3s ease;
            padding-right: 30px;
        }}

        .nav-link::after {{
            content: '';
            position: absolute;
            top: 50%;
            right: 0;
            width: 20px;
            height: 1px;
            background: var(--secondary);
            transition: width 0.3s ease, background 0.3s ease;
        }}

        .nav-link:hover {{
            color: var(--accent);
        }}

        .nav-link:hover::after {{
            width: 40px;
            background: var(--accent);
        }}

        /* Sections */
        section {{
            min-height: 100vh;
            display: flex;
            align-items: center;
            padding: 6rem 0;
        }}

        /* Hero Section */
        .hero {{
            position: relative;
        }}

        .hero-content {{
            max-width: 800px;
        }}

        .hero-title {{
            opacity: 0;
            animation: fadeIn 1s ease forwards;
        }}

        .hero-subtitle {{
            font-size: 1.25rem;
            color: var(--secondary);
            margin-bottom: 2rem;
            max-width: 600px;
            opacity: 0;
            animation: fadeIn 1s ease 0.3s forwards;
        }}

        /* Experience Section */
        .experience-item {{
            display: grid;
            grid-template-columns: 80px 1fr;
            gap: 2rem;
            margin-bottom: 4rem;
            opacity: 0;
            transform: translateX(-20px);
            animation: slideIn 0.6s ease forwards;
        }}

        .experience-number {{
            font-family: 'Cormorant Garamond', serif;
            font-size: 2.5rem;
            color: var(--accent);
            opacity: 0.5;
        }}

        .experience-content h3 {{
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }}

        .company {{
            display: block;
            color: var(--secondary);
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 1rem;
        }}

        /* Skills Section */
        .skills-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
        }}

        .skill-item {{
            padding: 2rem;
            border: 1px solid var(--border);
            text-align: center;
            transition: all 0.3s ease;
            opacity: 0;
            transform: translateY(20px);
            animation: fadeInUp 0.6s ease forwards;
        }}

        .skill-item:hover {{
            border-color: var(--accent);
            transform: translateY(-5px);
        }}

        /* Contact Section */
        .contact-info {{
            display: grid;
            gap: 2rem;
            max-width: 500px;
        }}

        .contact-item {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}

        .contact-item a {{
            color: var(--primary);
            text-decoration: none;
            transition: color 0.3s ease;
        }}

        .contact-item a:hover {{
            color: var(--accent);
        }}

        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}

        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateX(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}

        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        /* Responsive Design */
        @media (max-width: 768px) {{
            .nav {{
                position: fixed;
                top: 0;
                right: 0;
                left: 0;
                transform: none;
                background: var(--background);
                padding: 1rem 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}

            .nav-list {{
                flex-direction: row;
                justify-content: center;
                gap: 1.5rem;
            }}

            .nav-link {{
                padding-right: 0;
            }}

            .nav-link::after {{
                display: none;
            }}

            section {{
                padding: 4rem 0;
            }}

            .experience-item {{
                grid-template-columns: 1fr;
                gap: 1rem;
            }}

            .experience-number {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="grid-bg"></div>

    <nav class="nav">
        <ul class="nav-list">
            <li class="nav-item"><a href="#about" class="nav-link">About</a></li>
            <li class="nav-item"><a href="#experience" class="nav-link">Experience</a></li>
            <li class="nav-item"><a href="#skills" class="nav-link">Skills</a></li>
            <li class="nav-item"><a href="#contact" class="nav-link">Contact</a></li>
        </ul>
    </nav>

    <section id="about" class="hero">
        <div class="container">
            <div class="hero-content">
                <h1 class="hero-title">{data['name']}</h1>
                <p class="hero-subtitle">{data.get('summary', 'An artistic professional crafting unique and memorable experiences through innovative design and creative solutions.')}</p>
            </div>
        </div>
    </section>

    <section id="experience">
        <div class="container">
            <h2>Experience</h2>
            {experiences_html}
        </div>
    </section>

    <section id="skills">
        <div class="container">
            <h2>Expertise</h2>
            <div class="skills-grid">
                {skills_html}
            </div>
        </div>
    </section>

    <section id="contact">
        <div class="container">
            <h2>Connect</h2>
            <div class="contact-info">
                {f'<div class="contact-item"><span>📧</span><a href="mailto:{data["email"]}">{data["email"]}</a></div>' if data.get('email') else ''}
                {f'<div class="contact-item"><span>📱</span><span>{data["phone"]}</span></div>' if data.get('phone') else ''}
                {f'<div class="contact-item"><span>💼</span><a href="{data["linkedin"]}" target="_blank">LinkedIn Profile</a></div>' if data.get('linkedin') else ''}
                {f'<div class="contact-item"><span>💻</span><a href="{data["github"]}" target="_blank">GitHub Profile</a></div>' if data.get('github') else ''}
            </div>
        </div>
    </section>

    <script>
        // Smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({{
                    behavior: 'smooth'
                }});
            }});
        }});

        // Active section highlighting
        const sections = document.querySelectorAll('section');
        const navLinks = document.querySelectorAll('.nav-link');

        window.addEventListener('scroll', () => {{
            let current = '';
            sections.forEach(section => {{
                const sectionTop = section.offsetTop;
                const sectionHeight = section.clientHeight;
                if (scrollY >= sectionTop - 200) {{
                    current = section.getAttribute('id');
                }}
            }});

            navLinks.forEach(link => {{
                link.style.color = link.getAttribute('href').slice(1) === current ? 'var(--accent)' : 'var(--secondary)';
            }});
        }});

        // Animation on scroll
        const observerOptions = {{
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        }};

        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }}
            }});
        }}, observerOptions);

        document.querySelectorAll('.experience-item, .skill-item').forEach(el => {{
            observer.observe(el);
        }});
    </script>
</body>
</html>'''

        css_content = '''/* Artistic template styles are included in the HTML */'''
        
        js_content = '''/* Artistic template scripts are included in the HTML */'''

        return {
            'index.html': html_content,
            'style.css': css_content,
            'script.js': js_content
        }

# Initialize components
parser = ResumeParser()
generator = WebsiteGenerator()
file_parser = FileParser()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload-resume', methods=['POST'])
def upload_resume():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'File type not supported. Please upload PDF, DOCX, or TXT files.'})
        
        # Get template preference
        template = request.form.get('template', 'modern')
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extract text based on file type
        file_ext = filename.rsplit('.', 1)[1].lower()
        if file_ext == 'pdf':
            resume_text = file_parser.extract_text_from_pdf(file_path)
        elif file_ext in ['docx', 'doc']:
            resume_text = file_parser.extract_text_from_docx(file_path)
        else:  # txt
            resume_text = file_parser.extract_text_from_txt(file_path)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        if not resume_text.strip():
            return jsonify({'success': False, 'error': 'Could not extract text from the file. Please try a different format.'})
        
        # Parse the extracted text
        parsed_data = parser.parse_resume_text(resume_text)
        
        # Generate website with selected template
        website_files = generator.generate_website(parsed_data, template)
        
        return jsonify({
            'success': True,
            'resume_data': parsed_data,
            'website_files': website_files,
            'preview_html': website_files.get('index.html', ''),
            'template': template,
            'extracted_text': resume_text[:500] + '...' if len(resume_text) > 500 else resume_text
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error processing file: {str(e)}'})

@app.route('/api/parse-resume', methods=['POST'])
def parse_resume():
    try:
        data = request.get_json()
        resume_text = data.get('resume_text', '')
        
        if not resume_text:
            return jsonify({'error': 'No resume text provided'}), 400
        
        parsed_data = parser.parse_resume_text(resume_text)
        website_files = generator.generate_website(parsed_data)
        
        return jsonify({
            'parsed_data': parsed_data,
            'website_files': website_files
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-website', methods=['POST'])
def generate_website():
    try:
        data = request.get_json()
        resume_data = data.get('resume_data', {})
        template = data.get('template', 'modern')
        
        if not resume_data:
            return jsonify({'success': False, 'error': 'No resume data provided'})
        
        website_files = generator.generate_website(resume_data, template)
        
        return jsonify({
            'success': True,
            'resume_data': resume_data,
            'website_files': website_files,
            'preview_html': website_files.get('index.html', ''),
            'template': template
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/download-website', methods=['POST'])
def download_website():
    try:
        data = request.get_json()
        website_files = data.get('website_files', {})
        
        if not website_files:
            return jsonify({'error': 'No website files provided'}), 400
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
            with zipfile.ZipFile(tmp_file.name, 'w') as zip_file:
                for filename, content in website_files.items():
                    zip_file.writestr(filename, content)
            
            return send_file(
                tmp_file.name,
                as_attachment=True,
                download_name='personal-website.zip',
                mimetype='application/zip'
            )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080, host='127.0.0.1') 