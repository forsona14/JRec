from random import Random
from enum import Enum
from Knowledge import Knowledge
from Knowledge import Process
from Knowledge import KnowledgeBoundary

#class ProgressionConfiguration:
#    def __init__(self, stage=Stage.ASSESSMENT, ):


class Stage(Enum):
    ASSESSMENT = 0
    LEARNING_AT_COMMON_PACE = 1
    LEARNING_AT_INDIVIDUAL_PACE = 2


class StudentResponse(Enum):
    UNDERSTOOD = 1
    NOT_UNDERSTOOD = 0


class ProcessStatus(Enum):
    Status_UNKNOWN = -1
    Status_UNDERSTOOD = 1
    Status_NOT_UNDERSTOOD = 0


class InteractionResponse:
    def __init__(self, process, message, end_of_assessment = False):
        self.process = process
        self.message = message
        self.end_of_assessment = end_of_assessment

class Interaction:

    ASSESSMENT_PSEUDO_COUNT = 3
    ASSESSMENT_MIN_COUNT = 20
    ASSESSMENT_MAX_COUNT = 30

    def __init__(self, book_name, init_stage = Stage.ASSESSMENT):
        self.knowledge = Knowledge(book_name)

        self.process_status = [ProcessStatus.Status_UNKNOWN for i in range(self.knowledge.uniq_num())]

        self.colored_understood = 0
        self.colored_not_understood = 0

        self.understood_ratio = -1
        self.understood_ratio_history = []

        self.process_uid_history = []
        self.student_answer_history = []
        self.num_understood = 0
        self.num_not_understood = 0

        self.num_assessment_answered = 0


        self.stage = init_stage



        # This two lists dont care processStatus
        self.easier_processes_number = \
            [sum([self.knowledge.uniq_id_easier(uid, i) for uid in range(self.knowledge.uniq_num())])
             for i in range(self.knowledge.uniq_num())]
        self.harder_processes_number = \
            [sum([self.knowledge.uniq_id_easier(i, uid) for uid in range(self.knowledge.uniq_num())])
             for i in range(self.knowledge.uniq_num())]

        self.last_process_uid = -1 # no last process at the beginning
        self.last_student_response = StudentResponse.UNDERSTOOD



        self.random = Random()

    # Select next process for assessment
    def select_next_for_assessment(self):

        # Too many assessment questions
        if self.num_assessment_answered >= Interaction.ASSESSMENT_MAX_COUNT:
            self.last_process_uid = -99
            return

        # Converged
        if self.num_assessment_answered >= Interaction.ASSESSMENT_MIN_COUNT and \
            max(self.understood_ratio_history[-5:]) < min(self.understood_ratio_history[-5:]) + 0.01:
            self.last_process_uid = -99
            return

        gain = [min(self.easier_processes_number[i] * (Interaction.ASSESSMENT_PSEUDO_COUNT + self.num_not_understood),
                    self.harder_processes_number[i] * (Interaction.ASSESSMENT_PSEUDO_COUNT + self.num_understood))
                for i in range(self.knowledge.uniq_num())]
        for i in range(self.knowledge.uniq_num()):
            if self.process_status[i] != ProcessStatus.Status_UNKNOWN:
                gain[i] = -99
        max_gain = max(gain)
        max_processes = [i for i in range(self.knowledge.uniq_num())
                         if self.process_status[i] == ProcessStatus.Status_UNKNOWN and gain[i] == max_gain]

        # TODO
        if len(max_processes) == 0:
            self.last_process_uid = -99
        else:
            self.last_process_uid = self.random.choice(max_processes)

    # Color One
    def color_one(self, uid, studentResponse):
        self.process_status[uid] = studentResponse
        if studentResponse == StudentResponse.UNDERSTOOD:
            self.colored_understood += 1
        elif studentResponse == StudentResponse.NOT_UNDERSTOOD:
            self.colored_not_understood += 1
        for i in range(self.knowledge.uniq_num()):
            if self.knowledge.uniq_id_easier(i, uid):
                self.harder_processes_number[i] -= 1
            if self.knowledge.uniq_id_easier(uid, i):
                self.easier_processes_number[i] -= 1

    # Color self.last_process_uid
    def color_last(self):
        # add to history
        self.student_answer_history.append(self.last_student_response)

        # color the last process
        self.color_one(self.last_process_uid, self.last_student_response)

        if self.last_student_response == StudentResponse.UNDERSTOOD:
            self.num_understood += 1
            for i in range(self.knowledge.uniq_num()):
                if self.process_status[i] == ProcessStatus.Status_UNKNOWN and \
                        self.knowledge.uniq_id_easier(i, self.last_process_uid):
                    self.color_one(i, StudentResponse.UNDERSTOOD)

        if self.last_student_response == StudentResponse.NOT_UNDERSTOOD:
            self.num_not_understood += 1
            for i in range(self.knowledge.uniq_num()):
                if self.process_status[i] == ProcessStatus.Status_UNKNOWN and \
                        self.knowledge.uniq_id_easier(self.last_process_uid, i):
                    self.color_one(i, StudentResponse.NOT_UNDERSTOOD)

        if self.colored_understood + self.colored_not_understood > 0:
            self.understood_ratio = \
                float(self.colored_understood) / (self.colored_understood + self.colored_not_understood)
        else:
            self.understood_ratio = -1

    ##################################################################################################


    def request(self):
        if self.stage == Stage.ASSESSMENT:
            # first request
            if self.last_process_uid == -1:
                self.select_next_for_assessment()
            # end of assessment
            if self.last_process_uid == -99:
                return InteractionResponse(None, "End of Assessment",
                                           end_of_assessment=True)
            else:
                # TODO
                return InteractionResponse(self.knowledge.UniqueProcesses[self.last_process_uid],
                                           str(round(100.0 * self.understood_ratio, 4)) + "%")


    def response(self, student_response):
        if self.stage == Stage.ASSESSMENT:
            self.last_student_response = student_response
            self.color_last()
            self.num_assessment_answered += 1
            self.understood_ratio_history.append(self.understood_ratio)
            self.select_next_for_assessment()

    def knowledge_boundary(self):
        '''
        :return: calculated student's KnowledgeBoundary
        '''

