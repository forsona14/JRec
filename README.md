# JRec

Required Python Package:
CaboCha-0.69, MeCab 0.996 
NLTK 3.0.0 (not compatible with newer versions)   pip install -v nltk==3.0.0
jTransliterate
enum (for Python 2.7)
enum34 (Sometimes enum doesn't work)
requests


Initialize: interface = JRecInterface()

Get a New Article:  req = interface.request()

                    req.id   //Document ID for URL
                    
                    req.text //Text
                    
User Feedback:      interface.response(True or False)

See Also: Example.py
