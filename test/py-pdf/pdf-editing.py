import fitz

doc = fitz.open('1.pdf')

fontsize_to_use = 48
text = "absolutely not"
fontname_to_use = "Times-Roman"
text_lenght = fitz.getTextlength(text, fontname=fontname_to_use, fontsize=fontsize_to_use)

for page in doc:
    rect_x1 = 50
    rect_y1 = 100
    rect_x2 = rect_x1 + text_lenght + 2  # needs margin
    rect_y2 = rect_y1 + fontsize_to_use + 2  # needs margin
    rect = (rect_x1, rect_y1, rect_x2, rect_y2)

    ## Uncomment if you wish to display rect
    # page.drawRect(rect,color=(.25,1,0.25))

    page.insertTextbox(rect, text, fontsize=fontsize_to_use, fontname=fontname_to_use, color=(0, 0, 0))
    page.insertText((50,100), text, fontsize=fontsize_to_use, fontname=fontname_to_use, color=(0,0,0))
    page.insertImage(rect, filename='0.jpg')

doc.save('write.pdf')