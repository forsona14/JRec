# JRec

Initialize: interface = JRecInterface()

Get a New Article:  req = interface.request()

                    req.id   //Document ID for URL
                    
                    req.text //Text
                    
User Feedback:      interface.response(True or False)
