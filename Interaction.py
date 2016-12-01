# This Python file uses the following encoding: utf-8
# encoding: utf-8
from random import Random
from enum import IntEnum
from Knowledge import Knowledge
from Knowledge import KnowledgeBoundary

#class ProgressionConfiguration:
#    def __init__(self, stage=Stage.ASSESSMENT, ):


class Stage(IntEnum):
    ASSESSMENT = 0
    LEARNING_AT_COMMON_PACE = 1
    LEARNING_AT_INDIVIDUAL_PACE = 2

    ASSESSMENT_EVALUATION = 3

    END = 9


class StudentResponse(IntEnum):
    UNDERSTOOD = 5
    ALMOST_UNDERSTOOD = 4
    SOMEWHAT_UNDERSTOOD = 3
    LITTLE_UNDERSTOOD = 2
    NOT_UNDERSTOOD = 1


class ProcessStatus(IntEnum):
    Status_UNKNOWN = -1
    Status_UNDERSTOOD = 1
    Status_NOT_UNDERSTOOD = 0


class InteractionResponse:
    def __init__(self, process, message, stage):
        self.process = process
        if process != None:
            self.text = process.text
            #self.translation = process.translation
            #if len(process.vocabulary_explanation) == 0:
            #    self.vocabulary_explanation = "No vocabulary Explanation."
            #else:
            #    # self.vocabulary_explanation = '''<dl class="dl-horizontal vocabulary_explanation"><dt>私:</dt><dd>I</dd></dl>'''
            #    self.vocabulary_explanation = '<dl class="dl-horizontal">'
            #   for k in process.vocabulary_explanation.keys():
            #        self.vocabulary_explanation += '<dt>' + k + '</dt><dd>' + process.vocabulary_explanation[k] + '</dd>'
            #    self.vocabulary_explanation += '</dl>'
        self.message = message
        self.stage = stage

class Interaction:


#############################################################################################################
    PRESET_VERSION = -1


    # Configs:


    ASSESSMENT_PSEUDO_COUNT = 1
    ASSESSMENT_MIN_COUNT = 20
    ASSESSMENT_MAX_COUNT = 30

    ASSESSMENT_EVALUATION_UNDERSTOOD_NUM = 2
    ASSESSMENT_EVALUATION_UNKNOWN_RECOMBINATION_NUM = 2
    ASSESSMENT_EVALUATION_UNKNOWN_NEWKNOWLEDGE_NUM = 2
    ASSESSMENT_EVALUATION_NOT_UNDERSTOOD_NUM = 2



#############################################################################################################

    def __init__(self, simple_ui, init_stage = Stage.ASSESSMENT):
        self.knowledge = Knowledge(simple_ui)

        self.process_status = [ProcessStatus.Status_UNKNOWN for i in range(self.knowledge.uniq_num())]
        self.assessed_status = [False for i in range(self.knowledge.num())]

        self.colored_understood = 0
        self.colored_not_understood = 0

        self.understood_ratio = -1
        self.understood_ratio_history = []

        self.student_response_history = []
        self.num_understood = 0
        self.num_not_understood = 0
        self.num_assessment_answered = 0

        self.assess_eval = []
        self.assess_eval_pointer = 0
        self.assess_eval_results = []


        self.stage = init_stage
        self.num_in_current_stage = 0



        # This two lists dont care processStatus
        self.easier_processes_number = \
            [sum([self.knowledge.uniq_id_easier(uid, i) for uid in range(self.knowledge.uniq_num())])
             for i in range(self.knowledge.uniq_num())]
        self.harder_processes_number = \
            [sum([self.knowledge.uniq_id_easier(i, uid) for uid in range(self.knowledge.uniq_num())])
             for i in range(self.knowledge.uniq_num())]

        self.last_process_uid = -1 # no last process at the beginning
        self.last_process_id = -1
        self.last_student_response = StudentResponse.UNDERSTOOD


        if Interaction.PRESET_VERSION > 0:
            self.version = Interaction.PRESET_VERSION
        else:
            self.version = - Interaction.PRESET_VERSION
        self.random = Random()

    # Select next process for assessment
    def select_next_for_assessment(self):

        # Too many assessment questions
        if self.num_assessment_answered >= Interaction.ASSESSMENT_MAX_COUNT:
            self.last_process_id = -99
            return

        # Converged
        if self.num_assessment_answered >= Interaction.ASSESSMENT_MIN_COUNT and \
            max(self.understood_ratio_history[-5:]) < min(self.understood_ratio_history[-5:]) + 0.01:
            self.last_process_id = -99
            return

        if (self.num_not_understood == self.num_understood):
            gain = [min(self.easier_processes_number[i], self.harder_processes_number[i])
                    for i in range(self.knowledge.uniq_num())]
        else:
            if Interaction.ASSESSMENT_PSEUDO_COUNT >= 0:
                gain = [min(
                    self.easier_processes_number[i] * (Interaction.ASSESSMENT_PSEUDO_COUNT + self.num_not_understood),
                    self.harder_processes_number[i] * (Interaction.ASSESSMENT_PSEUDO_COUNT + self.num_understood))
                    for i in range(self.knowledge.uniq_num())]
                #gain = [self.harder_processes_number[i] * (Interaction.ASSESSMENT_PSEUDO_COUNT + self.num_not_understood) +
                #        self.easier_processes_number[i] * (Interaction.ASSESSMENT_PSEUDO_COUNT + self.num_understood)
                #        for i in range(self.knowledge.uniq_num())]
            else: # disable psedo_count
                gain = [min(self.easier_processes_number[i] , self.harder_processes_number[i])
                        for i in range(self.knowledge.uniq_num())]
                #gain = [self.easier_processes_number[i] + self.harder_processes_number[i]
                #        for i in range(self.knowledge.uniq_num())]

        for i in range(self.knowledge.uniq_num()):
            if self.process_status[i] != ProcessStatus.Status_UNKNOWN:
                gain[i] = -99
        max_gain = max(gain)
        max_processes = [i for i in range(self.knowledge.uniq_num())
                         if self.process_status[i] == ProcessStatus.Status_UNKNOWN and gain[i] == max_gain]

        # TODO
        if len(max_processes) == 0:
            self.last_process_id = -99
        else:
            self.num_in_current_stage += 1
            self.last_process_uid = self.random.choice(max_processes)
            self.last_process_id = self.random.choice(
                [i for i in range(self.knowledge.num()) if self.knowledge.data[i].uniq_id == self.last_process_uid])

    def select_next_for_assessment_evaluation(self):
        if len(self.assess_eval) == 0:
            kb = self.knowledge_boundary()
            self.assess_eval.append(
                [i for i in range(self.knowledge.num()) if self.assessed_status[i] == False and
                 self.process_status[self.knowledge.data[i].uniq_id] == ProcessStatus.Status_UNDERSTOOD])
            self.assess_eval.append(
                [i for i in range(self.knowledge.num()) if self.assessed_status[i] == False and
                self.process_status[self.knowledge.data[i].uniq_id] == ProcessStatus.Status_UNKNOWN
                and kb.classify(self.knowledge.data[i]) == KnowledgeBoundary.ReCombination])
            self.assess_eval.append(
                [i for i in range(self.knowledge.num()) if self.assessed_status[i] == False and
                self.process_status[self.knowledge.data[i].uniq_id] == ProcessStatus.Status_UNKNOWN
                and kb.classify(self.knowledge.data[i]) == KnowledgeBoundary.NewKnowledge])
            self.assess_eval.append(
                [i for i in range(self.knowledge.num()) if self.assessed_status[i] == False and
                self.process_status[self.knowledge.data[i].uniq_id] == ProcessStatus.Status_NOT_UNDERSTOOD])
            self.random.shuffle(self.assess_eval[0])
            self.random.shuffle(self.assess_eval[1])
            self.random.shuffle(self.assess_eval[2])
            self.random.shuffle(self.assess_eval[3])
            self.assess_eval[0] = self.assess_eval[0][:self.ASSESSMENT_EVALUATION_UNDERSTOOD_NUM]
            self.assess_eval[1] = self.assess_eval[1][:self.ASSESSMENT_EVALUATION_UNKNOWN_RECOMBINATION_NUM]
            self.assess_eval[2] = self.assess_eval[2][:self.ASSESSMENT_EVALUATION_UNKNOWN_NEWKNOWLEDGE_NUM]
            self.assess_eval[3] = self.assess_eval[3][:self.ASSESSMENT_EVALUATION_NOT_UNDERSTOOD_NUM]
            self.assess_eval = self.assess_eval[0] + self.assess_eval[1] + self.assess_eval[2] + self.assess_eval[3]
            #self.random.shuffle(self.assess_eval)
            self.assess_eval_pointer = 0

        if  self.assess_eval_pointer < len(self.assess_eval):
            self.num_in_current_stage += 1
            self.last_process_id = self.assess_eval[self.assess_eval_pointer]
            self.assess_eval_pointer += 1
        else:
            self.last_process_id = -99


    # Color One
    def color_one(self, uid, studentResponse):
        if studentResponse == StudentResponse.UNDERSTOOD or studentResponse == StudentResponse.ALMOST_UNDERSTOOD:
            new_status = ProcessStatus.Status_UNDERSTOOD
        elif studentResponse == StudentResponse.NOT_UNDERSTOOD or studentResponse == StudentResponse.LITTLE_UNDERSTOOD:
            new_status = ProcessStatus.Status_NOT_UNDERSTOOD
        else:
            return
        self.process_status[uid] = new_status
        if new_status == ProcessStatus.Status_UNDERSTOOD:
            self.colored_understood += 1
        elif new_status == ProcessStatus.Status_NOT_UNDERSTOOD:
            self.colored_not_understood += 1
        for i in range(self.knowledge.uniq_num()):
            if self.knowledge.uniq_id_easier(i, uid):
                self.harder_processes_number[i] -= 1
            if self.knowledge.uniq_id_easier(uid, i):
                self.easier_processes_number[i] -= 1

    # Color self.last_process_uid
    def color_last(self):
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

    def message_generation(self):
        return ""
        kb = self.knowledge_boundary()
        message = str(self.score()) + "<br>"
        message += str(self.knowledge.num()) + "<br>"
        for p in self.knowledge.data:
            if self.stage == Stage.ASSESSMENT_EVALUATION and p.id == self.last_process_id:
                pref = "====>>"
            else:
                pref = ""
            if self.process_status[p.uniq_id] == ProcessStatus.Status_UNKNOWN:
                if kb.classify(p) == KnowledgeBoundary.ReCombination:
                    message += '<b style="color:yellow">' + pref + p.sentence + '<br></b>'
                else:
                    message += '<b style="color:gray">' + pref + p.sentence + '<br></b>'
            elif self.process_status[p.uniq_id] == ProcessStatus.Status_UNDERSTOOD:
                message += '<b style="color:green">' + pref + p.sentence + '<br></b>'
            elif self.process_status[p.uniq_id] == ProcessStatus.Status_NOT_UNDERSTOOD:
                message += '<b style="color:red">' + pref + p.sentence + '<br></b>'
            else:
                message += '<b style="color:black">' + p.sentence + " " + str(self.process_status[p.uniq_id]) + '<br></b>'
        return message

    ##################################################################################################


    def request(self):
        if self.stage == Stage.ASSESSMENT:
            # first request
            if self.last_process_id == -1:
                self.select_next_for_assessment()

            # end of assessment
            if self.last_process_id == -99:
                self.last_process_id = -1
                self.last_process_uid = -1
                self.stage = Stage.ASSESSMENT_EVALUATION
                return InteractionResponse(None, self.message_generation(), Stage.ASSESSMENT_EVALUATION)
            else:
                # TODO
                return InteractionResponse(self.knowledge.data[self.last_process_id],
                                           self.message_generation(), Stage.ASSESSMENT)
                #return InteractionResponse(self.knowledge.UniqueProcesses[self.last_process_uid],
                #                           str(round(100.0 * self.understood_ratio, 4)) + "%")

        ##################################################################################################

        elif self.stage == Stage.ASSESSMENT_EVALUATION:
            # first request
            if self.last_process_id == -1:
                self.select_next_for_assessment_evaluation()

            # end of assessment_evaluation
            if self.last_process_id == -99:
                self.last_process_id = -1
                self.last_process_uid = -1
                self.stage = Stage.END
                return InteractionResponse(None, self.message_generation(), Stage.END)
            else:
                # TODO
                return InteractionResponse(self.knowledge.data[self.last_process_id],
                                           self.message_generation(), Stage.ASSESSMENT_EVALUATION)

        elif self.stage == Stage.END:
            return InteractionResponse(None, self.message_generation(), Stage.END)

    def response(self, student_response):

        if self.stage == Stage.ASSESSMENT:
            self.student_response_history.append(self.last_process_id * 10 + student_response)
            self.last_student_response = student_response
            self.assessed_status[self.last_process_id] = True
            self.color_last()
            self.num_assessment_answered += 1
            self.understood_ratio_history.append(self.understood_ratio)
            self.select_next_for_assessment()

        ##################################################################################################

        elif self.stage == Stage.ASSESSMENT_EVALUATION:
            self.student_response_history.append(self.last_process_id * 10 + student_response)
            self.last_student_response = student_response
            self.assessed_status[self.last_process_id] = True
            self.color_last()
            self.num_assessment_answered += 1
            self.understood_ratio_history.append(self.understood_ratio)
            self.select_next_for_assessment_evaluation()

    def knowledge_boundary(self):
        '''
        :return: calculated student's KnowledgeBoundary
        '''
        kb = KnowledgeBoundary(self.knowledge)
        for his in self.student_response_history:
            if his % 10 > StudentResponse.SOMEWHAT_UNDERSTOOD:
                kb.add(self.knowledge.data[his/10])
        return kb

    def score(self):
        if len(self.understood_ratio_history) == 0:
            return -1
        else:
            return self.understood_ratio_history[-1]


