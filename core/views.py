from django.shortcuts import redirect, render
from .models import Document
from .forms import DocumentForm

import docx2txt
import docx

from langdetect import detect, detect_langs, DetectorFactory
import pytesseract
import cv2

from deep_translator import GoogleTranslator
from googletrans import Translator

DetectorFactory.seed = 0

def my_view(request):
    
    message = 'Select file (.docx, .jpg)'
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'])
            newdoc.save()

            # Redirect to the document list after POST
            return redirect('my-view')
        else:
            message = 'The form is not valid. Fix the following error:'
    else:
        form = DocumentForm()  # An empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()
    
    field_name = 'docfile'
    obj = Document.objects.last()
    field_object = Document._meta.get_field(field_name)
    latest_file = 'documents/'+str(field_object.value_from_object(obj))
    print(type(latest_file), latest_file)
    
    if latest_file.endswith('.jpg'):
        translator = Translator()
        text = ''
        data = obj.docfile
        pytesseract.pytesseract.tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        img = cv2.imread(latest_file)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        #custom_config = r'-l eng+jpn --psm 6'
        custom_config = r'-l afr+amh+ara+asm+aze+bel+ben+bod+bos+bre+bul+cat+ceb+ces+chi_sim+chi_tra+chr+cos+cym+dan+dan_frak+dzo+ell+eng+enm+epo+equ+est+eus+fao+fas+fil+fin+fra+frk+frm+fry+gla+gke+glg+grc+guj+hat+heb+hin+hrv+hun+hye+iku+ind+isl+ita+ita+old+jav+jpn+kan+kat+kaz+khm+kir+kmr+kor+kur+lao+lat+lav+lit+itz+mal+mar+mkd+mlt+mon+mri+msa+mya+nep+nld+nor+oci+ori+osd+pan+pol+por+pus+que+ron+rus+san+sin+slk+slv+snd+spa+sqi+srp+sun+swa+swe+syr+tam+tat+tel+tgk+tgl+tha+tir+ton+tur+uig+ukr+urd+uzb+vie+yid+yor --psm 6'
        txt = pytesseract.image_to_string(thresh, config=custom_config)
        txt = str(txt).splitlines()
        
        translated = []
        for to_translate in txt:
            if to_translate != '':
                translated.append(translator.translate(to_translate, dest='en'))
            else:
                pass
        
        print(translated)        
        print(txt)
        
        
        try:
            for i in txt:
                if i != '':
                    print(detect_langs(i))
                else:
                    pass
            # print(detect_langs(txt))
            # txt =txt.splitlines()
        except Exception as e:
            print(e)
        # cv2.imshow('image',thresh)
        # cv2.waitKey(0)
        
        # for i in txt:
        #     text += i
    else:
        
        doc = docx.Document(latest_file)
    

        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
        data = '\n'.join(fullText)

        data_split = []
        data_split = data.split('.')
        print(data_split)
        
        try:
            for i in data_split:
                print(detect_langs(i))
        except Exception as e:
            print(e)
        # for i in data_split:
        #     print(detect(i))
        #print(detect_langs(data))
    # with open(latest_file,'rb') as f:
    #     context = f.read().decode(encoding="utf-8")
    #     f.close()
    # latest_file = Document.objects.last()
    # text = docx2txt.process('documents')
    # path = 'D:\College\Projects\ImagetoText\documents'
    # files = os.listdir(path)
    # paths = [os.path.join(path, basename) for basename in files]
    # latest_file = max(paths, key=os.path.getctime)

    # list_of_files = glob.glob('D:\College\Projects\ImagetoText\documents') 
    # latest_file = max(list_of_files, key=os.path.getctime)
    # print(latest_file)

    # for filename in os.listdir(os.getcwd()):
    #     with open(os.path.join(os.getcwd(), filename), 'r') as f:
    #         text = f.read()
    # Render list page with the documents and the form
    if txt:
        context = {'documents': documents, 'form': form, 'message': message, 'file': latest_file.replace('documents/',''), 'content': data, 'text_detected': txt, 'text_translated': translated}
    else:
        context = {'documents': documents, 'form': form, 'message': message, 'file': latest_file.replace('documents/',''), 'content': data}
    return render(request, 'base.html', context)
