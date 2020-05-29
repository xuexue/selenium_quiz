"""
Parses the test questions from a text file
"""

class Question(object):
    pass

class TextNoQuestion(Question):
    def __init__(self, text):
        self.text = text

class MCQuestion(Question):
    def __init__(self, question, answers, comment, ordered=False, img=None):
        self.question = question
        self.answers = answers
        self.comment = comment
        self.ordered = ordered
        self.img = img

    def randomize(self):
        if not self.ordered:
            random.shuffle(self.answers)

    def get_answer(self):
        ans = ["A", "B", "C", "D", "E"]
        for i in range(len(ans)):
            if self.answers[i][0]:
                return ans[i]
        raise ValueError("Unknown answer for question %s" + self.question)

def read_questions_from_file(path):
    f = open(path)

    questions = []
    for line in f:
        if line.startswith("MC."):
            # start of a multiple choice question
            q = line[3:].rstrip()
            ordered = next(f).rstrip() == "1"
            line = next(f).rstrip()

            img = None
            if line.startswith("img"):
                img = line.split(" ")[-1].strip()
                line = next(f).rstrip()

            answers = []
            while line:
                correct = line[0].lower() == 'x'
                choice = line[2:]
                comment = ""

                line = next(f).rstrip()
                if line.startswith('  =>'):
                    comment = line[5:].strip()
                    line = next(f).rstrip()
                answers.append((correct, choice, comment),)

            if line.startswith('=>'):
                comment = line[5:]

            obj = MCQuestion(q, answers, comment, ordered, img)
            questions.append(obj)
    return questions


