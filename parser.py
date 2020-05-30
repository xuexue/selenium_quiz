"""
Parses the test questions from a text file
"""

class Question(object):
    pass

class TextNoQuestion(Question):
    type = "text"
    def __init__(self, text):
        self.text = text


class EssayQuestion(Question):
    type = "essay"
    def __init__(self, text):
        self.text = text

class MCQuestion(Question):
    type = "mc"

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
        if line.lower().startswith("<text>"):
            # start of a textblock
            line = next(f)
            text = ""
            if not line.lower().startswith("</text>"):
                text += line
                line = next(f)
            obj = TextNoQuestion(text.strip())
            questions.append(obj)

        elif line.lower().startswith("<essay>"):
            # start of a textblock
            line = next(f)
            text = ""
            if not line.lower().startswith("</essay>"):
                text += line
                line = next(f)
            obj = EssayQuestion(text.strip())
            questions.append(obj)


        elif line.startswith("MC."):
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


