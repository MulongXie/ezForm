# importing required modules
import PyPDF2

# creating a pdf file object
pdfFileObj = open('1.pdf', 'rb')

# creating a pdf reader object
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

# printing number of pages in pdf file
print(pdfReader.numPages)

# creating a page object
pageObj = pdfReader.getPage(0)

# extracting text from page
print(pageObj.extractText())

# closing the pdf file object
# pdfFileObj.close()


import os
import fitz


def conver_img(input_pdf_path,output_path):
    doc = fitz.open(input_pdf_path)
    pdf_name = (input_pdf_path.split('/')[-1]).split('.')[0]
    for pg in range(doc.pageCount):
        page = doc[pg]
        rotate = int(0)
        zoom_x = 1.0
        zoom_y = 1.0
        trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
        pm = page.getPixmap(matrix=trans, alpha=False)
        pm.writePNG(output_path+'%s_%d.JPG' % (pdf_name,pg))


input_pdf_path="1.pdf"
output_path=""
conver_img(input_pdf_path,output_path)