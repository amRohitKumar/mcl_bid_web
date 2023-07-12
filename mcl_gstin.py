import mcl_utils as mclu
import easyocr  # for optical character recognition
import os
import re

def extract_text(filepath):
  reader = easyocr.Reader(['en'], gpu=True)
  pages = mclu.pdf2img(filepath)
  result = ""
  for imagepath in pages:
    text_extracted = reader.readtext(imagepath, paragraph="False")
    for txt in text_extracted:
      result += "\n" + txt[-1]
    os.remove(imagepath)
  return result

def getGSTIN(filepath):
  doc, docname, docloc = mclu.open_file_link(filepath)
  text = ""
  for page in doc:
    text += page.get_text()
  if text == "":
    text = extract_text(filepath)  
  gst = re.findall(r"Registration Number[ ]*:[ ]*([a-zA-Z0-9]+)|Registration Number[ ]*([a-zA-Z0-9]+)", text)
  gstin_extracted = []
  for g in gst:
    if g[0] == "" and g[1] == "":
      gstin_extracted.append("")
    elif g[0] == "":
      gstin_extracted.append(g[1])
    else:
      gstin_extracted.append(g[0])
  return gstin_extracted
