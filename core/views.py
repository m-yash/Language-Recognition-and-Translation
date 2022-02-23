from django.shortcuts import redirect, render
from .models import Document
from .forms import DocumentForm

import docx2txt
import docx

from langdetect import detect, detect_langs
import pytesseract
import cv2


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
        
        data = obj.docfile
        pytesseract.pytesseract.tesseract_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        img = cv2.imread(latest_file)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        custom_config = r'-l hin+eng+es --psm 6'
        txt = pytesseract.image_to_string(thresh, config=custom_config)
        # cv2.imshow('image',thresh)
        # cv2.waitKey(0)
        print(txt)
        try:
            print(detect_langs(txt))
        except Exception as e:
            print(e)
        
        
    else:
        
        doc = docx.Document(latest_file)
    

        fullText = []
        for para in doc.paragraphs:
            fullText.append(para.text)
        data = '\n'.join(fullText)

        print(detect(data))
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
    context = {'documents': documents, 'form': form, 'message': message, 'file': latest_file, 'content': data}
    return render(request, 'base.html', context)