import getpass
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait


from parser import read_questions_from_file

# HELPER FUNCTION BLOCK ========================

def get_question_div(driver):
    """Get the parent div for the edited question."""
    return driver.find_element_by_css_selector(".multiple_choice_question.ready")

def save_question(question_div):
    """Click the submit button to save the question."""
    question_div.find_element_by_css_selector('button.submit_button').click()

def set_question_type(question_div, value):
    """Select question type from dropdown."""
    question_type = Select(question_div.find_element_by_name("question_type"))
    question_type.select_by_value(value)

def set_main_question_text(question_div, text):
    """Set the main question text using the HTML editor to avoid iframes."""
    question_div.find_element_by_link_text("HTML Editor").click()
    question_body = question_div.find_element_by_css_selector("textarea.question_content")
    question_body.send_keys(text)

# QUESTIONS ========================

def enter_text_no_question(mcq, driver):
    parent = get_question_div(driver)
    set_question_type(parent, 'text_only_question')
    set_main_question_text(parent, mcq.text)
    save_question(parent)

def enter_essay_question(mcq, driver):
    parent = get_question_div(driver)
    set_question_type(parent, 'essay_question')
    set_main_question_text(parent, mcq.text)
    save_question(parent)

def enter_mc_question(mcq, driver):
    # most of the work will be done in this div
    parent = get_question_div(driver)

    # set question type to multiple choice
    set_question_type(parent, 'multiple_choice_question')

    # add question text body
    set_main_question_text(parent, mcq.question)

    # correct number of answer choices in the HTML
    answers = parent.find_elements_by_css_selector('input[name="answer_text"].disabled_answer')
    diff = len(answers) - len(mcq.answers)
    if diff < 0:
        # add more answers
        for i in range(-diff):
            parent.find_element_by_class_name("add_answer_link").click()
    elif diff > 0:
        # remove answers
        trash = parent.find_elements_by_css_selector('a.delete_answer_link')
        for i in range(diff - 1, -1, -1):
            button = trash[i]
            div = answers[i]
            ActionChains(driver).move_to_element(div).click(button).perform()

    answers = parent.find_elements_by_css_selector('input[name="answer_text"].disabled_answer')
    corrects = parent.find_elements_by_class_name('select_answer_link')
    comments = parent.find_elements_by_class_name('comment_focus')

    assert(len(corrects) == len(answers))
    assert(len(comments) == len(answers) + 3)

    for i in range(len(answers)):
        is_correct, ans, feedback = mcq.answers[i]
        answers[i].send_keys(ans) # fill in answer
        if is_correct:
            corrects[i].click() # mark correct answer
        if feedback:
            # Click to open up comment box
            comments[i].click()
            # Wait to prevent race condition
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[contains(@class, 'switch-views__link')]")))

            # Switch to HTML view
            parent.find_element_by_css_selector('a.switch-views__link').click()
            # Enter comments
            comment_box = parent.find_element_by_css_selector('textarea.editor-toggle')
            comment_box.send_keys(feedback)
            # Click done
            parent.find_element_by_css_selector('a.btn.edit_html_done').click()

    # Save question
    save_question(parent)
 

DISPATCH = {
        "mc": enter_mc_question,
        "text": enter_text_no_question,
        "essay": enter_essay_question,
}

# MAIN ========================

def upload_questions(username, password, quiz_path, questions,
                     overwrite=True):
    """
    Upload questions to Quercus

    Arguments:
      username: Quercus login utorid
      password: Quercus login password
      quiz_path: HTTP path to the Quercus quiz
      questions: list of Question objects (see parser.py)
      overwrite: whether to remove existing questions in the Quercus quiz
    """
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=options)

    driver.get(quiz_path)

    # LOGIN
    elem = driver.find_element_by_id("username")
    elem.clear()
    elem.send_keys(username)

    elem = driver.find_element_by_id("password")
    elem.clear()
    elem.send_keys(password)
    elem.send_keys(Keys.RETURN)

    # Wait until page load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ui-id-2")))

    # Find and click on the question tab
    question_tab = driver.find_element_by_id("ui-id-2")
    question_tab.click()

    # We'll need this link later
    add_question_link = driver.find_elements_by_css_selector("a.add_question_link")[-1]

    # Remove all the existing questions
    if overwrite:
        parent = driver.find_element_by_id("questions")
        delete_buttons = parent.find_elements_by_class_name("delete_question_link")
        question_divs = parent.find_elements_by_class_name("question_text")
        for i in range(len(delete_buttons)-1, -1, -1): # need to go backwards...
            # We need to move to the question text div to make the delete button
            # visibel, and then click the button
            button = delete_buttons[i]
            div = question_divs[i]
            ActionChains(driver).move_to_element(div).click(button).perform()
            # Accept the popup confirmation for the deletion
            driver.switch_to.alert.accept()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ui-id-2")))

    # Add questions
    for q in questions:
        add_question_link.click()

        fn = DISPATCH[q.type]
        fn(q, driver)

    # Save the quiz
    driver.find_element_by_class_name("save_quiz_button").click()

    # Close the window
    #driver.close()


if __name__ == "__main__":
    EXAMPLE_FILE_PATH = "example_quiz.txt"

    import argparse
    parser = argparse.ArgumentParser(description='Upload Quercus Quiz content from text file')
    parser.add_argument('--file', type=str, help='Text file containing quiz content',
                        default=EXAMPLE_FILE_PATH)
    parser.add_argument('--url', type=str, help='URL of Quercus quiz')
    parser.add_argument('--utorid', type=str, help='UTORID for signing into Quercus')
    parser.add_argument('--overwrite', dest='overwrite', action='store_true',
                        default=False, help='Remove existing content already on Quercus')
    args = parser.parse_args()

    questions = read_questions_from_file(args.file)

    passwd = getpass.getpass("password: ").strip()
    upload_questions(args.utorid, passwd, args.url, questions, args.overwrite)
