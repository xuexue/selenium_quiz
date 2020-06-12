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

class QuestionBlock(object):
    type = "block"
    def __init__(self, num_questions, num_pts):
        self.num_questions = num_questions
        self.num_pts = num_pts
        self.questions = []

    def add_question(self, obj):
        self.questions.append(obj)


def read_questions_from_file(path):
    f = open(path)

    # Used to accumulate Question and QuestionBlock objects
    questions = []

    # Boolean to determine whether questions are to be added to a
    # QuestionBlock
    question_block = False

    for line in f:
        if line.startswith("# "):
            if "[" in line and "]" in line:
                # start a new question block
                question_block = True

                # extract metadata about this question block
                # should be of the form "[1 question, 1 pt]"
                meta = line.split("[")[-1].split(" ")

                num_questions = int(meta[0])
                try:
                    num_points = int(meta[2])
                except:
                    num_points = 1 # optional

                questions.append(QuestionBlock(num_questions, num_points))
            else:
                # go back to not having question blocks
                question_block = False

        obj = None # new question object to be added (if any)
        if line.lower().startswith("<text>"):
            # start of a textblock
            line = next(f)
            text = ""
            if not line.lower().startswith("</text>"):
                text += line
                line = next(f)
            obj = TextNoQuestion(text.strip())

        elif line.lower().startswith("<essay>"):
            # start of a textblock
            line = next(f)
            text = ""
            if not line.lower().startswith("</essay>"):
                text += line
                line = next(f)
            obj = EssayQuestion(text.strip())

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

        if obj is not None:
            if question_block:
                assert type(questions[-1]) == QuestionBlock
                questions[-1].add_question(obj)
            else:
                questions.append(obj)
    return questions


if __name__ == "__main__":
    EXAMPLE_FILE_PATH = "example_quiz.txt"
    questions = read_questions_from_file(EXAMPLE_FILE_PATH )


