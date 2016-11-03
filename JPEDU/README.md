# JPEDU

Required Python Package:
CaboCha-0.69, MeCab 0.996 
NLTK 3.0.0 (not compatible with newer versions)   pip install -v nltk==3.0.0
jTransliterate
enum (for Python 2.7)


//
from JPEDU.Interaction import *

// Initialize
hci = Interaction('SJ12')

// Get Next Sentence and Message
response = hci.request()
sentence = hci.process.sentence
message = hci.message

// Student's feedback
hci.response(StudentResponse.NOT_UNDERSTOOD)
hci.response(StudentResponse.UNDERSTOOD)