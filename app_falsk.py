from pdfminer.high_level import extract_text
import nltk
import re
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
from flask import Flask, Response, request

PHONE_REG = re.compile(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]')
EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('stopwords')

app = Flask(__name__)

RESERVED_WORDS = [
    'school',
    'college',
    'univers',
    'academy',
    'faculty',
    'institute',
    'faculdades',
    'Schola',
    'schule',
    'lise',
    'lyceum',
    'lycee',
    'polytechnic',
    'kolej',
    'ünivers',
    'okul',
]

SKILLS_DB = [
    'machine learning',
    'data science',
    'python',
    'word',
    'excel',
    'mongo',
    'mssql',
    'html',
    'css',
    'bootstrap',
    'uikit',
    'automation',
    'ruby on rails',
    'ror',
    'postgresQL',
    'nlp',
    'tkinter',
    'pydocx',
    'javascript',
    'Ruby',
    'c',
    'c++',
    'tailwind',
    'ajax',
    'django',
    'firebase',
    'postgresql',
    'restapi',
    'git',
    'redux',
]

def extract_text_from_pdf(pdf_path):
    txt = extract_text(pdf_path)
    if txt:
        return txt.replace('\t', ' ')
    
def extract_names(text):
    nltk_results = ne_chunk(pos_tag(word_tokenize(text)))
    for nltk_result in nltk_results:
        if type(nltk_result) == Tree:
            name = ''
            for nltk_result_leaf in nltk_result.leaves():
                name += nltk_result_leaf[0] + ' '
            return name
 
def extract_phone_number(resume_text):
    phone = re.findall(PHONE_REG, resume_text)
 
    if phone:
        number = ''.join(phone[0])
 
        if resume_text.find(number) >= 0 and len(number) <= 16:
            return number
    return None

def extract_emails(resume_text):
    return re.findall(EMAIL_REG, resume_text)
 
def extract_skills(input_text):
    stop_words = set(nltk.corpus.stopwords.words('english'))
    word_tokens = nltk.tokenize.word_tokenize(input_text)
    filtered_tokens = [w for w in word_tokens if w not in stop_words]
    filtered_tokens = [w for w in word_tokens if w.isalpha()]
    bigrams_trigrams = list(map(' '.join, nltk.everygrams(filtered_tokens, 2, 3)))
    found_skills = set()
    
    for sent in nltk.sent_tokenize(input_text):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if hasattr(chunk, 'label') and (chunk.label() == 'skills' or chunk.label() =='skill'):
                found_skills.add(
                    ' '.join(chunk_leave[0] for chunk_leave in chunk.leaves())
                )
                
    for token in filtered_tokens:
        if token.lower() in SKILLS_DB:
            found_skills.add(token)
    
    for ngram in bigrams_trigrams:
        if ngram.lower() in SKILLS_DB:
            found_skills.add(ngram)
 
    return found_skills

def extract_education(input_text):
    organizations = []
    for sent in nltk.sent_tokenize(input_text):
        for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
            if hasattr(chunk, 'label') and chunk.label() == 'ORGANIZATION':
                organizations.append(' '.join(c[0] for c in chunk.leaves()))

    education = set()
    for org in organizations:
        for word in RESERVED_WORDS:
            if org.lower().find(word) >= 0:
                education.add(org)
 
    return education

@app.route("/")
def index():
    return Response("{'message': 'Server is up and running....'}", status=200, mimetype='application/json')

@app.route("/cv-data", methods=["POST"])
def get_urls():
    try:
        if not request.is_json:
            return 'Missing JSON in request', 400
        data = request.get_json()
        cv_data = data.get('cv')
        text = extract_text_from_pdf(cv_data)
        phone_number = extract_phone_number(text)
        email = extract_emails(text)
        education = extract_education(text)
        skills = extract_skills(text)
        name = extract_names(text)
        return {"name":name,"skills":skills,"education":education,"email":email,"phone_number":phone_number}
    except Exception as e:
        return Response("{'message': '"+str(e)+"'}", status=500, mimetype='application/json')        
            
            
if __name__ == '__main__':
    app.run(port=5102)