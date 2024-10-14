import os
import openai 
import subprocess
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
import io
import tempfile

# Access environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
DOWNLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'tex'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

# Utility function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Controller Function
def process_latex_resume(file, job_description):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Attempt to decode the file content
        try:
            latex_content = file.read().decode('utf-8')
        except UnicodeDecodeError:
            latex_content = file.read().decode('latin-1')

        # Modify LaTeX file content with job description
        modified_latex_content = modify_latex_file(latex_content, job_description)
        
        # Balance braces if needed
        modified_latex_content = balance_braces(modified_latex_content)

        # Convert LaTeX to PDF in-memory
        pdf_stream = convert_to_pdf_in_memory(modified_latex_content)
        
        if pdf_stream:
            return pdf_stream
        else:
            return "Error generating PDF"
    return "Invalid file"

# Route for uploading and processing the LaTeX resume
@app.route('/custom-resume', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        job_description = request.form['job_description']

        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        # Call the controller function to handle the file
        pdf_stream = process_latex_resume(file, job_description)
        
        if isinstance(pdf_stream, str) and "Error" in pdf_stream:
            return jsonify({'error': pdf_stream}), 500
        
        # Return the PDF file as a download
        return send_file(pdf_stream, download_name='resume.pdf', as_attachment=True)

    # Render the upload form for GET requests
    return render_template('upload.html')

# Modify LaTeX file content based on job description
def modify_latex_file(tex_file, job_description):
    latex_content = tex_file

    start_marker = "\\noindent \\textbf{\\underline{WORK EXPERIENCE}}"
    end_marker = "\\noindent \\textbf{\\underline{PROJECTS}}"  

    if start_marker in latex_content and end_marker in latex_content:
        before_work_experience = latex_content.split(start_marker)[0]
        work_experience_section = latex_content.split(start_marker)[1].split(end_marker)[0]
        after_work_experience = latex_content.split(end_marker)[1]
    else:
        return "Error: Work experience section markers not found in LaTeX file."

    messages = [
        {"role": "system", "content": "You are an expert assistant for modifying LaTeX resumes."},
        {"role": "user", "content": (
            f"Here is the work experience section of a LaTeX resume: {work_experience_section}. "
            f"Here is the job description: {job_description}. "
            "I want you to identify all **key skills and relevant keywords** from the job description and **integrate them seamlessly** into the work experience section. "
            "Demonstrate how each skill was applied or relevant to the responsibilities and achievements listed, ensuring that each bullet point shows these skills in action (e.g., technical challenges, solutions, or accomplishments). "
            "Maintain the original structure, ensuring each bullet point remains exactly two lines in length. Do not reduce the length of any bullet point. "
            "Do not bold or highlight the skills; instead, **integrate them naturally** into the content of each bullet. "
            "Ensure consistency in formatting, alignment, and overall style throughout the modified section. "
            "Return only the modified LaTeX content, and ensure that all instructions are followed precisely, with no additional comments or explanations."
        )}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=1500
    )
    
    modified_work_experience = response['choices'][0]['message']['content']
    modified_content = before_work_experience + start_marker + "\n\n" + modified_work_experience + "\n\n" + end_marker + after_work_experience

    return modified_content 

# Convert LaTeX content to PDF in-memory using Dockerized pdflatex
def convert_to_pdf_in_memory(latex_content):
    try:
        pdflatex_path = '/usr/bin/pdflatex'
        with tempfile.NamedTemporaryFile(suffix=".tex", delete=False) as temp_tex:
            temp_tex.write(latex_content.encode('utf-8'))
            temp_tex.flush()

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
                temp_pdf_path = temp_pdf.name

                docker_command = [
                    'docker', 'exec', 'pdflatex-container', 'pdflatex', '-output-directory', os.path.dirname(temp_pdf_path), temp_tex.name
                ]

                # Run pdflatex in the Docker container
                subprocess.run(docker_command, check=True)

                # Read the PDF content
                with open(temp_pdf_path, 'rb') as f:
                    pdf_stream = io.BytesIO(f.read())
                    pdf_stream.seek(0)

        return pdf_stream

    except subprocess.CalledProcessError as e:
        print(f"Error generating PDF: {e}")
        return None

# Function to ensure that braces are balanced in LaTeX
def balance_braces(latex_content):
    open_braces = latex_content.count('{')
    close_braces = latex_content.count('}')
    
    if open_braces > close_braces:
        latex_content += '}' * (open_braces - close_braces)
    
    return latex_content

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
