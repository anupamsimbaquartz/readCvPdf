from fastapi import FastAPI, File, UploadFile
import pdfminer
from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import re
import docx2txt

app = FastAPI()

# functions to process pdf...
file_names = []

def remove_punctuations(line):
    return re.sub(r'(\.|\,)', '', line)
def open_pdf_file(file_name):
    
    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    pagenums = set()
    infile = open(file_name, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close()

    result = []

    for line in text.split('\n'):
        line2 = line.strip()
        if line2 != '':
            result.append(line2)
    return (result)



    def remove_punctuations(line):
        return re.sub(r'(\.|\,)', '', line)

def preprocess_document(document):
    for index, line in enumerate(document):
        line = line.lower()
        line = remove_punctuations(line)
        
        line = line.split(' ')
        while '' in line:
            line.remove('')
            
        while ' '  in line:
            line.remove(' ')
            
            
        document[index] = ' '.join(line)
    return (document)




def get_email(document):
    #Further optimization to be done.
    emails = []
    pattern = re.compile(r'\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}')
    for line in document:
        matches = pattern.findall(line)
        for mat in matches:
            if len(mat) > 0:
                emails.append(mat)
    #print (emails)
    return (emails)


def get_phone_no(document):
    #This function has to be further modified better and accurate results.
    #Possible phone number formats - Including +91 or just with the numbers.
    
    mob_num_regex = r'''(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)
                        [-\.\s]*\d{3}[-\.\s]??\d{4}|\d{5}[-\.\s]??\d{4})'''
    pattern = re.compile(mob_num_regex)
    matches = []
    for line in document:
        match = pattern.findall(line)
        for mat in match:
            if len(mat) > 9:
                matches.append(mat)

    return (matches)

def get_education(document):
    education_terms = []
    with open('education.txt', 'r') as file:
        education_terms = file.readlines()
    
    education_terms = [term.strip('\n') for term in education_terms]
    education = []
    for line in document:
        for word in line.split(' '):
            if len(word) > 2 and word in education_terms:
                if line not in education:
                    education.append(line)
    #print (education)
    return (education)


def get_skills(document):
    skill_terms = []
    with open('valid_skill.txt', 'r') as file:
        skill_terms = file.readlines()
    
    skill_terms = [term.strip('\n') for term in skill_terms]
    skills = []
    
    for line in document:
        words = line.split(' ')
        
        for word in words:
            if word in skill_terms:
                if word not in skills:
                    skills.append(word)
                    
        word_pairs = []
        for i in zip(words[:-1], words[1:]):
            word_pairs.append(i[0] + ' ' + i[1])   #This is to find skills like 'data science' i.e skills containint two words.    return (skills)
            
        for pair in word_pairs:
            if pair in skill_terms:
                if pair not in skills:
                    skills.append(pair)
                    
    return (skills)

def get_experience(document):
    pattern1 = re.compile(r'(jan(uary)?|feb(ruary)?|mar(ch)?|apr(il)?|may|jun(e)?|jul(y)?|aug(ust)?|sep(tember)?|oct(ober)?|nov(ember)?|dec(ember)?)(\s|\S)(\d{2,4}).*(jan(uary)?|feb(ruary)?|mar(ch)?|apr(il)?|may|jun(e)?|jul(y)?|aug(ust)?|sep(tember)?|oct(ober)?|nov(ember)?|dec(ember)?)(\s|\S)(\d{2,4})')
    pattern2 = re.compile(r'(\d{2}(.|..)\d{4}).{1,4}(\d{2}(.|..)\d{4})')
    pattern3 = re.compile(r'(\d{2}(.|..)\d{4}).{1,4}(present)')
    pattern4 = re.compile(r'(jan(uary)?|feb(ruary)?|mar(ch)?|apr(il)?|may|jun(e)?|jul(y)?|aug(ust)?|sep(tember)?|oct(ober)?|nov(ember)?|dec(ember)?)(\s|\S)(\d{2,4}).*(present)')
    patterns = [pattern1, pattern2, pattern3, pattern4]
    experience = []
    for index, line in enumerate(document):
        for pattern in patterns:
            exp = pattern.findall(line)
            if len(exp) > 0:
                experience.append(document[index:index+4])
                
    return (experience)



email_ids = []
phone_nos = []
education_1 = []
education_2 = []
skills_1 = []
skills_2 = []
experience_1 = []
experience_2 = []

def get_details(file_names):
    for file_name in file_names:
        if file_name.endswith('.pdf'):
            document = open_pdf_file(file_name)
        elif file_name.endswith('.docx'):
            document = open_docx_file(file_name)
        
        
        email = get_email(document)
        phone_no = get_phone_no(document)
        document = preprocess_document(document)
        #print ('\n\n')
        #print (file_name)
        #print ('Email is {} phone number is {}'.format(email, phone_no))
        if len(email_ids) > 0:
            email_ids.append(email[0])
        else:
            email_ids.append('')
            
        if len(phone_no) > 0:
            phone_nos.append(phone_no[0])
        else:
            phone_nos.append('')
        
        education = get_education(document)
        #print ('Education ', get_education(document))
        if len(education) > 1:
            education_1.append(education[0])
            education_2.append(education[1])
        elif len(education) == 1:
            education_1.append(education[0])
            education_2.append('')
        elif len(education) == 0:
            education_1.append('')
            education_2.append('')
            
        skills = get_skills(document)
        #print ('Skills ', skills)
        
        if len(skills) > 1:
            skills_1.append(skills[0])
            skills_2.append(skills[1])
        elif len(skills) == 1:
            skills_1.append(skills[0])
            skills_2.append('')
        elif len(skills) == 0:
            skills_1.append('')
            skills_2.append('')
            
        experience = get_experience(document)
        #print ('Experience ', get_experience(document))
        if len(experience) > 1:
            experience_1.append(experience[0])
            experience_2.append(experience[1])
        elif len(experience) == 1:
            experience_1.append(experience[0])
            experience_2.append('')
        elif len(experience) == 0:
            experience_1.append('')
            experience_2.append('') 

@app.post("/files/")
async def create_file(file: bytes = File()):
    return {"file_size": len(file)}
@app.get("/")
async def sdfsdfsf():
    return {"file_size": "dsadasd"}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    import os
    print(os.getcwd())
    file_location = f"{os.getcwd()}/{file.filename}"
    print("sdasdasdaaaaaaaaaaaaa",file_location)
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    print("file saved on server")
    # apply operations to fetch data...
    file_names.append(file.filename)
    email_ids = []
    phone_nos = []
    education_1 = []
    education_2 = []
    skills_1 = []
    skills_2 = []
    experience_1 = []
    experience_2 = []

    for file_name in file_names:
        print("======================= file",file_name)
        if file_name.endswith('.pdf'):
            print("inside if")
            document = open_pdf_file(file_name)
        elif file_name.endswith('.docx'):
            document = open_docx_file(file_name)
        
        
        email = get_email(document)
        phone_no = get_phone_no(document)
        document = preprocess_document(document)
        #print ('\n\n')
        #print (file_name)
        #print ('Email is {} phone number is {}'.format(email, phone_no))
        if len(email_ids) > 0:
            email_ids.append(email[0])
        else:
            email_ids.append('')
            
        if len(phone_no) > 0:
            phone_nos.append(phone_no[0])
        else:
            phone_nos.append('')
        
        education = get_education(document)
        #print ('Education ', get_education(document))
        if len(education) > 1:
            education_1.append(education[0])
            education_2.append(education[1])
        elif len(education) == 1:
            education_1.append(education[0])
            education_2.append('')
        elif len(education) == 0:
            education_1.append('')
            education_2.append('')
            
        skills = get_skills(document)
        #print ('Skills ', skills)
        
        if len(skills) > 1:
            skills_1.append(skills[0])
            skills_2.append(skills[1])
        elif len(skills) == 1:
            skills_1.append(skills[0])
            skills_2.append('')
        elif len(skills) == 0:
            skills_1.append('')
            skills_2.append('')
            
        experience = get_experience(document)
        #print ('Experience ', get_experience(document))
        if len(experience) > 1:
            experience_1.append(experience[0])
            experience_2.append(experience[1])
        elif len(experience) == 1:
            experience_1.append(experience[0])
            experience_2.append('')
        elif len(experience) == 0:
            experience_1.append('')
            experience_2.append('')    

    os.remove(file.filename)
    print("file removed from server")
    return {"filename": file.filename,"email":email,"phone":phone_no,"education":education,"experience":experience}