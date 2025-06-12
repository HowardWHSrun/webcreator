# Resume to Website Creator

A stunning web application that transforms your resume into a beautiful personal website instantly! Upload your resume file or paste text, and watch as your professional website is created in real-time.

## ✨ Enhanced Features

- **🎨 Beautiful Modern Design**: Stunning gradient interface with smooth animations
- **📄 Multi-Format Support**: Upload PDF, DOCX, DOC, or TXT files
- **🚀 Instant Generation**: Website created automatically upon upload
- **👀 Real-time Preview**: See your website immediately as it's generated
- **💾 Easy Download**: Get complete website as ZIP file
- **📱 Mobile Responsive**: Beautiful design on all devices
- **🎭 Professional Templates**: Modern, clean designs that impress
- **⚡ Zero Learning Curve**: Just upload and done!

## Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. Clone or download this project to your computer
2. Open a terminal/command prompt and navigate to the project folder
3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. Start the Flask server:
   ```bash
   python app.py
   ```

2. Open your web browser and go to:
   ```
   http://localhost:5000
   ```

3. You should see the Personal Website Creator interface!

## 🎯 How to Use (Super Simple!)

### Method 1: File Upload (Recommended)
1. **Drag & drop** your resume file (PDF, DOCX, TXT) into the upload area
2. **Watch the magic happen** - your website is created instantly!
3. **Preview** your beautiful website in real-time
4. **Download** your complete website as a ZIP file

### Method 2: Text Input
1. **Paste** your resume text into the text area
2. **Click** "Create My Website" 
3. **Preview** and **download** your website

### That's it! 🎉
Your professional website is ready to upload to any hosting service!

## Resume Format Tips

For best results, format your resume text like this:

```
John Doe
Software Engineer
john.doe@email.com | (555) 123-4567 | linkedin.com/in/johndoe

Summary
Brief description of your professional background and goals...

Experience
Job Title at Company Name (Start Date - End Date)
- Key achievement or responsibility
- Another achievement with metrics

Education
Degree Name
University Name (Graduation Year)

Skills
Skill1, Skill2, Skill3, Skill4
```

## 📋 Supported File Formats & Information

### File Formats
- **PDF** (.pdf) - Most common resume format
- **Microsoft Word** (.docx, .doc) - Word documents  
- **Text Files** (.txt) - Plain text resumes

### Extracted Information
The intelligent parser can extract:
- **Personal Details**: Name, professional title, location
- **Contact Information**: Email, phone, LinkedIn, GitHub, personal websites
- **Professional Summary**: Career objectives and key qualifications
- **Work Experience**: Job titles, companies, employment dates, achievements
- **Education**: Degrees, institutions, graduation years, coursework
- **Technical Skills**: Programming languages, tools, frameworks
- **Projects**: Personal and professional project details
- **Certifications**: Professional certifications and licenses
- **Languages**: Spoken language proficiencies

## Customization

The generated website includes:
- Modern, responsive design
- Professional color scheme
- Smooth scrolling navigation
- Contact form integration ready
- Social media links
- Mobile-friendly layout

## Hosting Your Website

After downloading your website:

1. **Free Options**:
   - GitHub Pages
   - Netlify
   - Vercel

2. **Paid Options**:
   - Any web hosting service
   - WordPress hosting
   - Custom domain hosting

## Troubleshooting

### Common Issues

**"Failed to parse resume"**
- Make sure your resume text includes basic information (name, email)
- Try reformatting sections with clear headers
- Check for special characters that might interfere

**"Network error"**
- Ensure the Flask server is running (`python app.py`)
- Check that you're accessing `http://localhost:5000`
- Restart the application if needed

**Website doesn't look right**
- Try regenerating with updated information
- Check that all required fields are filled
- Refresh the preview

### Getting Help

If you encounter issues:
1. Check that all dependencies are installed correctly
2. Ensure you're using Python 3.7+
3. Try restarting the Flask application
4. Check the terminal for error messages

## Technical Details

**Built With**:
- Flask (Python web framework)
- HTML5/CSS3/JavaScript
- Font Awesome icons
- Google Fonts

**Browser Compatibility**:
- Chrome, Firefox, Safari, Edge
- Mobile browsers supported

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to fork this project and submit pull requests for improvements!

---

**Happy website building!** 🚀 