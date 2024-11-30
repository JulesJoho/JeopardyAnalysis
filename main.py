# Datascraper is an uncreative name for a module built
# specifically for this project.
import Datascraper as ds
import pandas as pd
from datetime import date as dt

pd.set_option('display.max_rows', 1000)

# This function takes in an entire row from the dataframe and poses that as a question to the user. The user presses
# enter when they're ready to answer, and then enters the code for that questions. Enter "." for a correct answer, "/"
# for and incorrect answer, and "," for a skip. Then type any number of letters to represent subjects and press enter.
# Functions returns an integer for if the question was correct or not, which is either -1, 0, or 1, as well as the
# subjects as a string
def question_asker(row):

    print("\n" + row['category'] + " for $" + str(row['value']))
    media_text = ''
    if row['media']:
        media_text = ' with media'
    ddtext = ''
    if row['DD']:
        ddtext = ' Daily Double'
    print(row['date'] + ddtext + media_text)
    none = input(row['hint'])

    while True:
        final = input(row['answer'])
        if (len(final) == 0) or ((final[0] != ',') and (final[0] != '.') and (final[0] != '/')):
            print("Please begin your answer with one of the following symbols:")
            print("\',\' for skip")
            print("\'.\' for correct")
            print("\'/\' for incorrect")
        elif len(final) < 2:
            print("Please add at least one character for the question\'s subject.")
        elif final[1:].isalpha() is False:
            print("Ensure that all subject characters are letters.")
        else:
            correct = final[0]
            subjects = final[1:]
            if correct == ",":
                correct = 0
            if correct == ".":
                correct = 1
            if correct == "/":
                correct = -1
            return correct, subjects


# This function asks the user for what they want to do after booting up, and returns a string representing their input.
# This function is maybe a little strange, but it lowers the number of indentations to be read in the main function by
# offloading those if statements.
def bootup_menu():
    while True:
        print("\nSelect from one of the following options:")
        print("1) Import new data (please do not do this while the show is airing)")
        print("2) Answer Questions")
        print("3) Analyze data")
        print("4) Other options")
        choice = input("")

        # This option results in scraping data off the j-archive website. The program will search for any games
        # not already stored in the dataframe and adds their information to jeopardydata.csv
        if choice == "1":
            return "scrape_data"

        if choice == "2":
            print("Would you like to answer a particular number of questions, or questions from a particular game?")
            print("1) Particular number")
            print("2) Particular game")
            choice = input("")

            # This option asks for a set number of questions in the dataframe to answer, and for a starting point.
            # That quantity of questions are asked to the user, and their responses are saved to the dataframe.
            if choice == "1":
                return "answer_questions"

            # This option asks the user for a particular game of Jeopardy! and then asks each unanswered question
            # from that game. The users responses are saved to the dataframe
            if choice == "2":
                return "answer_game"

            print("Enter a relevant number")

        if choice == "3":
            print("What sort of data analysis would you like to do?")
            print("1) What are the most common correct responses to Jeopardy! questions?")
            choice = input("")
            if choice == "1":
                return "response_frequencies"
            else:
                print("Not a valid answer")

        if choice == "4":

            print("Which of the following options would you like to do?")
            print("1) Create new abbreviated dataframe.")
            print("2) Organize abbreviated dataframe.")
            print("3) Delete user input")
            print("4) Remove duplicates")
            print("5) Convert dates to date object")
            choice = input("")

            # The abbreviated dataframe is saved as abvjeopardydata.csv. It consists of only the rows of
            # jeopardydata.csv that have already been answered, to allow for easier analysys of answers. This dataframe
            # is also updated automatically when a question is answered, and is sorted automatically when it is
            # analyzed. Therefore, these options exist for developer convenience.
            if choice == "1":
                return "create_abv_data"
            if choice == "2":
                return "organize_abv_data"

            if choice == "3":
                print("Are you sure? All data entered by the user, including question subjects and answers, "
                      "will be deleted.")
                print("1) Yes")
                print("2) no")
                choice = input("")

                if choice == "1":
                    return "delete_user_data"

            if choice == "4":
                return "remove_duplicates"
            if choice == "5":
                return "convert_dates"

            else:
                print("Enter a relevant number")

        else:
            print("Enter a relevant number")


# Here, the program grabs the available data. It is very important that that data is not removed from the relevant
# folder. df is the entire dataframe, containing each question. adf contains only the questions that have already been
# answered.
print("Retrieving data...")
df = pd.read_csv("jeopardydata.csv", low_memory=False)
adf = pd.read_csv("abvjeopardydata.csv", low_memory=False)
print("Welcome To Jules Johnson's Jeopardy! analysis engine!")
print("If you have any questions about what you're seeing, check the readme file or my website at julesjoho.com//posts/jeopardy/")

while True:
    userinput = bootup_menu()

    # This option results in scraping data off the j-archive website. The program will search for any games
    # not already stored in the dataframe and adds their information to jeopardydata.csv
    if userinput == "scrape_data":
        latest_game = df.iloc[0]['game_name']

        newdf = pd.DataFrame([], columns=['category', 'hint', 'answer',
                                          'value', 'jtype', 'media',
                                          'DD', 'date', 'game_name',
                                          'correct', 'subjects', 'date_answered'])

        print("Searching for new data...")
        # Once we're certain we've found all the new questions,
        # done_searching is set to True and the loop is exited.
        done_searching = False
        new_data = False
        for season in (ds.find_seasons()):

            for game in ds.find_games_in_season(season):
                todaysdf = ds.webpage_to_dataframe(game)
                # this checks to see if the game currently being examined
                # is already present in the dataframe
                if todaysdf.iloc[0]['game_name'] == latest_game:
                    done_searching = True
                    break
                newdf = pd.concat([newdf, todaysdf])
                new_data = True

            if done_searching:
                break

        newdf.to_csv('newdata.csv', index=False)

        # Finally, the new data is added to the existing dataframe and saved.
        if new_data:
            df = pd.concat([newdf, df])
            df.to_csv('jeopardydata.csv', index=False)

    # This option asks for a set number of questions in the dataframe to answer, and for a starting point.
    # That quantity of questions are asked to the user, and their responses are saved to the dataframe.
    if userinput == "answer_questions":

        while True:
            rounds = input("How many questions would you like to answer?")
            starting_point = input("How far down into the dataframe would you like to start analyzing questions?")

            if (rounds.isnumeric() is False) or (starting_point.isnumeric() is False):
                print("please only enter a number")

            else:
                rounds = int(rounds)
                starting_point = int(starting_point)
                break

        counter = 0
        i = starting_point
        while True:

            if pd.isna(df.iloc[i]["correct"]):

                correct, subjects = question_asker(df.iloc[i])
                df.at[i, "correct"] = correct
                df.at[i, "subjects"] = subjects
                df.at[i, "date_answered"] = dt.today()
                adf.loc[len(adf.index)] = df.iloc[i]

                counter += 1

            if counter == rounds:
                break

            i += 1

        print("Saving answers ...")
        df.to_csv('jeopardydata.csv', index=False)
        adf.to_csv('abvjeopardydata.csv', index=False)

    # This option asks the user for a particular game of Jeopardy! and then asks each unanswered question
    # from that game. The users responses are saved to the dataframe
    if userinput == "answer_game":

        print("What game would you like to answer questions from?")
        game_name = input("For example, you can enter \"Show #8948\" or just \"8948\"")

        if game_name.isnumeric():
            game_name = "Show #" + game_name

        print("Searching for that game...")

        # This is a bool that states if the relevant game has been found in the dataframe
        found = False

        # This loop looks through the entire dataframe for questions from the relevant game
        for i in range(len(df)):
            if df.iloc[i]["game_name"] == game_name:

                if pd.isna(df.iloc[i]["correct"]):
                    correct, subjects = question_asker(df.iloc[i])
                    df.at[i, "correct"] = correct
                    df.at[i, "subjects"] = subjects
                    df.at[i, "date_answered"] = dt.today()
                    adf.loc[len(adf.index)] = df.iloc[i]

                found = True
            elif found:
                break

        if found is False:
            print("Game not found")
        else:
            print("Saving answers ...")
            df.to_csv('jeopardydata.csv', index=False)
            adf.to_csv('abvjeopardydata.csv', index=False)

    if userinput == "response_frequencies":

        end_date = input("What is the end date you would like to consider? Enter date as YYYY-MM-DD. If you would like to use the present, "
                           "enter anything besides a date. \n")

        try:
            end_date = dt.fromisoformat(end_date)
        except:
            end_date = dt.today()


        start_date = input("What is the lower date you would like to consider? If you would like to use the begining of"
                           "the show, enter anything besides a date\n")

        try:
            start_date = dt.fromisoformat(start_date)
        except:
            start_date = dt.fromisoformat("1984-09-10")

        mask = (df['date'] > start_date) & (df['date'] <= end_date)


        index = df.loc[mask]["answer"].value_counts()
        print(index.head(500))

        index.to_csv('index.csv', index=True)


    # The abbreviated dataframe is saved as abvjeopardydata.csv. It consists of only the rows of jeopardydata.csv
    # that have already been answered, to allow for easier analysys of answers. This dataframe is also updated
    # automatically when a question is answered, and is sorted automatically when it is analyzed. Therefore, these
    # options exist for developer convenience.
    if userinput == "create_abv_data":

        newdata = df.dropna(subset=["correct"])

        newdata.to_csv('abvjeopardydata.csv', index=False)

    if userinput == "organize_abv_data":

        adf = adf.sort_values(by=["date", "jtype", "category", 'value'], ascending=[False, True, True, True],
                              ignore_index=True)
        adf.to_csv('abvjeopardydata.csv', index=False)

    if userinput == "remove_duplicates":

        df = df.drop_duplicates(subset= ["date", "hint"])
        adf = adf.drop_duplicates(subset=["date", "hint"])

        df.to_csv('jeopardydata.csv', index=False)
        adf.to_csv('abvjeopardydata.csv', index=False)

    #
    if userinput == "convert_dates":
        for i in range(len(df)):
            if i % 10000 == 0:
                print(i)
            df.at[i, 'date'] = dt.fromisoformat(df.at[i, 'date'])

        for i in range(len(adf)):
            if i % 10000 == 0:
                print(i)
            adf.at[i, 'date'] = dt.fromisoformat(adf.at[i, 'date'])

        df.to_csv('jeopardydata.csv', index=False)
        adf.to_csv('abvjeopardydata.csv', index=False)
