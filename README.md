# Upload Quercus Quizzes from Text File

This is a script that uses selenium to upload Quercus quizzes. You can write
your quiz questions in a text file and use the script to insert the questions
to Quercus. Text files have the advantage of being version controllable.

Example call:

```
python upload.py --url=https://q.utoronto.ca/courses/1234/quizzes/12345/edit --utorid=abcd1234 --overwrite
```

## Installation

1. This script is written in python3
2. Install selenium by following the instructions https://selenium-python.readthedocs.io/installation.html
3. You will need a browesr driver for either Chrome or Firefox. I am using the Chrome driver on a Mac

## Question Format

See `example_quiz.txt` for an example. If you want to use a different format, you can change
`parser.py`. It should be relatively straightforward to write your questions in a different
format than what I'm using here.

### Multiple Choice

- Each multiple choice question begins with the string `MC. ` followed by the question text (no newlines)
- The next line should be either a `*` if the order of the choices don't matter,
  or `1` if the order of the choices do matter.
  (Note: for now both `*` and `1` does the same thing. Later on, I plan on having the script shuffle
  the choices if the order of the choices don't matter.)
- Text next few lines will be your potential answers. Begin each answer choice with either a `* ` if it is incorrect,
  or a `x `  if it is the correct chocie.
- Each choice can have an optional feedback text in the next line, provided the feedback line
  with the characters `  =>`
- The entire question can have an optional feedback at the very end of the question; the feedback
  line should start with the character `=>`
- There should be a blank line at the end of each MC question (including the one at the very end of the fine)

```
MC. question text
*
* incorrect choice
* incorrect choice
  => optional feedback for this question
x correct choice
=> optional feedback for the entire question

```

### Text (no question)

- Begin a text block with the line `<text>`
- Add one or more line of text
- End a text block with the line `</text>`
- Add blank line before the next question

```
<text>
one or more lines of text
</text>
```

### Essay

- Begin a block with the line `<essay>`
- Add one or more line of text
- End a block with the line `</essay>`
- Add blank line before the next question

```
<essay>
Essay question text
</essay>
```

### Question Groups

A line that starts with `# ` is used to formally and informally group
questions. If a line starts with `# ` and ends with `[x questions, y pts]`,
then the script will consider the subsequent questions to be a part of 
a Quercus question group, and only `x` questions will be shown to students.
Each of those questions will be worth `y` pts each.

A line that starts with `# ` but does not end with the `[x questions, y pts]`
can be used to end a question block. You can also use it informally to group
questions.

```
# informal group

<essay>
This question will always be displayed
</essay>

# actual question group [1 question, 1 pt]

<essay>
Only one question will be displayed.
</essay>

<essay>
This question may or may not be displayed.
</essay>

# end question group

<essay>
This question will always be displayed
</essay>

<essay>
This question will always be displayed
</essay>

# informal group. this doesn't do anything

<essay>
This question will always be displayed
</essay>
```

## Supported Features

Here are the currently supported features:

- Removing existing questions in a quiz
- Multiple choices questions
    - Entering feedback for the entire question
    - Entering feedback for each choice
- Text (no question)
- Essay questions
- Question groups

Here are the features I'd like to support:

- Assigning points per question
- Numerical answer
- Matching
- Fill in the blank

