#!/usr/bin/env python3
"""
Demo script for the Personal Website Creator
This script demonstrates how to use the resume parser and website generator programmatically.
"""

from app import ResumeParser, WebsiteGenerator
import json

def demo_resume_parsing():
    """Demonstrate resume parsing with sample data"""
    print("🔍 Demo: Resume Parsing")
    print("=" * 50)
    
    # Sample resume text
    sample_resume = """John Doe
Software Engineer
john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe | github.com/johndoe

Summary
Experienced software engineer with 5+ years developing scalable web applications and microservices. Passionate about clean code, performance optimization, and mentoring junior developers.

Experience
Senior Software Engineer at Tech Corp (2020-Present)
Led development of microservices architecture serving 1M+ users
Improved system performance by 40% through optimization initiatives
Mentored 5 junior developers and conducted technical interviews

Software Engineer at StartupXYZ (2018-2020)
Built responsive web applications using React and Node.js
Implemented CI/CD pipelines reducing deployment time by 60%
Collaborated with cross-functional teams in agile environment

Education
Bachelor of Science in Computer Science
University of Technology (2014-2018)

Skills
JavaScript, TypeScript, Python, React, Node.js, Express, MongoDB, PostgreSQL, AWS, Docker, Kubernetes, Git, Agile/Scrum"""

    # Parse the resume
    parser = ResumeParser()
    parsed_data = parser.parse_resume_text(sample_resume)
    
    print("✅ Parsed resume data:")
    print(json.dumps(parsed_data, indent=2))
    print()
    
    return parsed_data

def demo_website_generation(resume_data):
    """Demonstrate website generation"""
    print("🏗️  Demo: Website Generation")
    print("=" * 50)
    
    generator = WebsiteGenerator()
    website_files = generator.generate_website(resume_data)
    
    print("✅ Generated website files:")
    for filename in website_files.keys():
        print(f"  - {filename}")
    
    # Save files to demo_output directory
    import os
    output_dir = "demo_output"
    os.makedirs(output_dir, exist_ok=True)
    
    for filename, content in website_files.items():
        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            f.write(content)
    
    print(f"\n💾 Files saved to '{output_dir}' directory")
    print(f"📂 Open '{output_dir}/index.html' in your browser to see the generated website!")
    print()

def demo_different_resume_formats():
    """Test parsing with different resume formats"""
    print("🧪 Demo: Different Resume Formats")
    print("=" * 50)
    
    formats = {
        "Minimal Format": """Jane Smith
Data Scientist
jane@email.com | 555-0123

Summary
Data scientist with expertise in machine learning and analytics.

Skills
Python, R, SQL, TensorFlow, Pandas""",
        
        "Detailed Format": """Michael Johnson
Product Manager | michael.johnson@company.com | (555) 987-6543
LinkedIn: linkedin.com/in/michaeljohnson | Portfolio: michaeljohnson.dev

Professional Summary
Experienced product manager with 7+ years in tech startups and enterprise companies. Expert in agile methodologies, user research, and data-driven decision making.

Professional Experience
Senior Product Manager - TechCorp Inc. (2021-Present)
• Launched 3 major product features resulting in 25% user growth
• Led cross-functional team of 12 engineers and designers
• Implemented data analytics framework improving conversion by 15%

Product Manager - Innovation Labs (2019-2021)
• Managed product roadmap for B2B SaaS platform
• Conducted user interviews and market research
• Collaborated with engineering on technical specifications

Education & Certifications
MBA in Technology Management - Stanford University (2019)
BS in Computer Science - UC Berkeley (2017)
Certified Scrum Product Owner (CSPO)

Core Competencies
Product Strategy, Agile/Scrum, User Research, Data Analysis, A/B Testing, Roadmap Planning, Stakeholder Management"""
    }
    
    parser = ResumeParser()
    
    for format_name, resume_text in formats.items():
        print(f"\n📄 Testing: {format_name}")
        print("-" * 30)
        
        parsed = parser.parse_resume_text(resume_text)
        print(f"Name: {parsed['name']}")
        print(f"Title: {parsed['title']}")
        print(f"Email: {parsed['email']}")
        print(f"Skills: {len(parsed['skills'])} skills found")
        print(f"Experience: {len(parsed['experience'])} entries found")

def main():
    """Run all demos"""
    print("🚀 Personal Website Creator - Demo")
    print("=" * 60)
    print()
    
    # Demo 1: Basic parsing and generation
    parsed_data = demo_resume_parsing()
    demo_website_generation(parsed_data)
    
    # Demo 2: Different formats
    demo_different_resume_formats()
    
    print("✨ Demo completed!")
    print("\nTo try the web interface:")
    print("1. Run: python app.py")
    print("2. Open: http://localhost:5000")
    print("3. Paste your resume and start building!")

if __name__ == "__main__":
    main() 