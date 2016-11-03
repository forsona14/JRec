from Interaction import *

hci = Interaction("Genki12")

while True:
    response = hci.request()
    if response.end_of_assessment:
        print 'end'
        break
    else:
        print hci.num_assessment_answered + 1 , '.', response.process.sentence, response.message
        ans = input()
        if ans == 1:
            hci.response(StudentResponse.UNDERSTOOD)
        elif ans == 0:
            hci.response(StudentResponse.NOT_UNDERSTOOD)