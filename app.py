from pdfminer.high_level import extract_text
import nltk
import re
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
PHONE_REG = re.compile(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]')
EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('stopwords')
import textract
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

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
    'nuces',
    'national',
    'university',
    
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
    'photoshop',
    'asp.net',
    'asp',
    'c#',
    '2d',
    '3d',
    'data analyst',
    'spss', 
    'stata',
    'microsoft office',
    'microsoft office access',
    'Oracle',
    'oop',
    'illustrator',
    'adobe xd',
    'adobe',
    'UI/Ux',
    'pythondeveloper'
]

EDUCATION = [
            'BE','B.E.', 'B.E', 'BS', 'B.S','C.A.','c.a.','B.Com','B. Com','M. Com', 'M.Com','M. Com .',
            'ME', 'M.E', 'M.E.', 'MS', 'M.S',
            'BTECH', 'B.TECH', 'M.TECH', 'MTECH',
            'PHD', 'phd', 'ph.d', 'Ph.D.','MBA','mba','graduate', 'post-graduate','5 year integrated masters','masters',
            'SSC', 'HSC', 'CBSE', 'ICSE', 'X', 'XII'
        ]
Main_heading_list = ["hobbies","Skill","education","work","certification","affiliation","projects",
                    "researches","publication","activities","information","interests","career","qualification","academic","expertise","objectives",
                     "training","volunteering","languages","studies","miscellaneous","education","employment","profile",
                     "summary","Competencies","Operating","ICT"]

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
            if hasattr(chunk, 'label') and (chunk.label() == 'ORGANIZATION'):
                organizations.append(' '.join(c[0] for c in chunk.leaves()))
                
    education = set()
    for org in organizations:
        for word in RESERVED_WORDS:
            if org.lower().find(word) >= 0:
                education.add(org)
    return education

def extract_experience(resume_text):
        
    wordnet_lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    word_tokens = nltk.word_tokenize(resume_text)

    filtered_sentence = [w for w in word_tokens if not w in stop_words and 
    wordnet_lemmatizer.lemmatize(w) not in stop_words] 
    sent = nltk.pos_tag(filtered_sentence)
    cp = nltk.RegexpParser('P: {<NNP>+}')
    cs = cp.parse(sent)
    test = []
    
    for vp in list(cs.subtrees(filter=lambda x: x.label()=='P')):
        test.append(" ".join([i[0] for i in vp.leaves() if len(vp.leaves()) >= 2]))
    x = [x[x.lower().index('experience') + 10:] for i, x in enumerate(test) if x and 
    'experience' in x.lower()]
    if x == []:
         x = [x[x.lower().index('work history') + 12:] for i, x in enumerate(test) if x and 
    'work history' in x.lower()]
    
    return x
    
if __name__ == '__main__':
    file = 'updated cv faizan international.pdf'
    if file.endswith('docx') or file.endswith('doc'):
        text = textract.process(file)
    elif file.endswith('pdf'):
        text = extract_text_from_pdf(file)
    elif file.endswith('txt'):
        f = open(file, 'r')
        text = f.read()
    
    phone_number = extract_phone_number(text)
    email = extract_emails(text)
    education = extract_education(text)
    experience = extract_experience(text)
    for data in experience:
        if '|' in data:
            data = data.split('|')
            if data[0].lower().strip() in SKILLS_DB:
                descination = data[0].strip()
                compney = data[1]
                experience = {
                    "Compney":compney,
                    "Descination":descination
                }
    skills = extract_skills(text)
    name = extract_names(text)
    print("name: ",name)
    print("experience: ",experience)
    print("phone_number: ",phone_number)
    print("email: ",email)
    print("skills: ",skills)
    print("education: ",education)