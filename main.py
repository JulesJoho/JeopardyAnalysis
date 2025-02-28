# Datascraper is an uncreative name for a module built
# specifically for this project.
import matplotlib.pyplot as plt
import numpy as np
import Datascraper as ds
import pandas as pd
from datetime import date as dt
from unidecode import unidecode
from matplotlib.ticker import PercentFormatter
from string import ascii_lowercase
import ast

pd.set_option('display.max_rows', 1000)
pd.set_option('display.max_columns', None)


# This is a little function that I'm honestly astonished isn't in Pandas to begin with. Given a dataframe, produces the
# Pareto front of that data, along the columns x and y. All columns in the optional "other" list are included as well.
# This version of the function is optimized for 2d pareto fronts.
def pareto_front_2D(df, x, y, other=None):
    if other is None:
        other = []
    front = df[other + [x] + [y]].copy()

    front = front.dropna()

    # The point with the highest y value has the lowest possible x value. if something had a lower x value, it must also
    # have a lower x value, and so is not worth including in the front. We also do it the other direction.

    front = front.sort_values(by=[y, x], ascending=False, ignore_index=True)
    x_record = front.iloc[0][x]
    front = front[front[x] >= x_record]

    front = front.sort_values(by=[x, y], ascending=False, ignore_index=True)
    y_record = front.iloc[0][y]
    front = front[front[y] >= y_record]

    front.reset_index(drop=True, inplace=True)

    for i in front.index:

        if front.loc[i][y] < y_record:
            front.drop(index=i, inplace=True)

        elif front.loc[i][y] > y_record:
            y_record = front.loc[i][y]

        elif (i != 0) and (front.loc[i][x] < front.loc[i - 1][x]):
            front.drop(index=i, inplace=True)

    return front


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
        final = input(row['response'])
        if (len(final) == 0) or ((final[0] != ',') and (final[0] != '.') and (final[0] != '/') and (final[0] != ';')):
            print("Please begin your answer with one of the following symbols:")
            print("\',\' for skip")
            print("\'.\' for correct")
            print("\'/\' for incorrect")
            print("\';\' to edit the previous answer")
        elif final[0] == ';':
            pass
        elif len(final) < 2:
            print("Please add at least one character for the question\'s subject.")
        elif final[1:].isalpha() is False:
            print("Ensure that all subject characters are letters.")
        else:
            accuracy = final[0]
            subjects = final[1:]
            if accuracy == ",":
                accuracy = 0
            if accuracy == ".":
                accuracy = 1
            if accuracy == "/":
                accuracy = -1
            return accuracy, subjects


# Similar to question_asker, this takes in a row of the dataframe, and simply prints it, without asking for any inut
# from the user
def question_displayer(row):
    print("\n" + row['category'] + " for $" + str(row['value']))
    media_text = ''
    if row['media']:
        media_text = ' with media'
    ddtext = ''
    if row['DD']:
        ddtext = ' Daily Double'
    print(row['date'] + ddtext + media_text)
    print(row['hint'])


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
            print("2) What is my accuracy per game?")
            print("3) What is my accuracy per topic?")
            choice = input("")
            if choice == "1":
                print("Would you like to split results by point value?")
                print("1) Yes")
                print("2) No")
                while True:
                    choice = input("")
                    if choice == "1":
                        return "response_frequencies_by_value"
                    elif choice == "2":
                        return "response_frequencies"
                    else:
                        print("Please print either 1 or 2")
            elif choice == "2":
                return "accuracy_per_game"
            elif choice == "3":
                return "accuracy_per_topic"
            else:
                print("Not a valid answer")

        if choice == "4":

            print("Which of the following options would you like to do?")
            print("3) Delete user input")
            print("4) Remove duplicates")
            print("5) Convert dates to date object")
            choice = input("")

            # The abbreviated dataframe is saved as abvjeopardydata.csv. It consists of only the rows of
            # jeopardydata.csv that have already been answered, to allow for easier analysys of answers. This dataframe
            # is also updated automatically when a question is answered, and is sorted automatically when it is
            # analyzed. Therefore, these options exist for developer convenience.
            if choice == "1":
                return "rename columns"

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


# There are some names that are different from others, either for including parentheses, or for including diacriticals.
# This function removes those aspects of a word.
def name_cleaner(name: str):
    if name[0] == "(":
        return unidecode(name[1:].replace(")", "", 1))
    return unidecode(name)


# Here, the program grabs the available data. It is very important that that data is not removed from the relevant
# folder. df is the entire dataframe, containing each question.
print("Retrieving data...")
df = pd.read_csv("jeopardydata.csv", low_memory=False)
params = open("params.txt", "r").read()
topic_dict = ast.literal_eval(params.split("topics =")[1].split("}")[0].strip() + "}")

print("Welcome To Jules Johnson's Jeopardy! analysis engine!")
print("If you have any questions about what you're seeing, check the "
      "readme file or my website at julesjoho.com/posts/jeopardy/")

while True:
    userinput = bootup_menu()

    # This option results in scraping data off the j-archive website. The program will search for any games
    # not already stored in the dataframe and adds their information to jeopardydata.csv
    if userinput == "scrape_data":
        latest_game = df.iloc[0]['game_name']

        newdf = pd.DataFrame([], columns=['category', 'hint', 'response',
                                          'value', 'jtype', 'media',
                                          'DD', 'date', 'game_name',
                                          'accuracy', 'subjects', 'date_answered'])

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

        # Finally, the new data is added to the existing dataframe and saved.
        if new_data:
            df = pd.concat([newdf, df])
            df.to_csv('jeopardydata.csv', index=False)

    # This option asks for a set number of questions in the dataframe to answer, and for a starting point.
    # That quantity of questions are asked to the user, and their responses are saved to the dataframe.
    elif userinput == "answer_questions":

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

            if pd.isna(df.iloc[i]["accuracy"]):
                accuracy, subjects = question_asker(df.iloc[i])
                df.at[i, "accuracy"] = accuracy
                df.at[i, "subjects"] = subjects
                df.at[i, "date_answered"] = str(dt.today())

                counter += 1

            if counter == rounds:
                break

            i += 1

        print("Saving answers ...")
        df.to_csv('jeopardydata.csv', index=False)

    # This option asks the user for a particular game of Jeopardy! and then asks each unanswered question
    # from that game. The users responses are saved to the dataframe
    elif userinput == "answer_game":

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

                if pd.isna(df.iloc[i]["accuracy"]):
                    accuracy, subjects = question_asker(df.iloc[i])
                    df.at[i, "accuracy"] = accuracy
                    df.at[i, "subjects"] = subjects
                    df.at[i, "date_answered"] = str(dt.today())

                found = True
            elif found:
                break

        if found is False:
            print("Game not found")
        else:
            print("Saving answers ...")
            df.to_csv('jeopardydata.csv', index=False)

    # In this option, the program generates a list of frequencies of different responses. This list may or may not be
    # sorted by point value.
    elif (userinput == "response_frequencies") or (userinput == "response_frequencies_by_value"):

        end_date = input(
            "What is the end date you would like to consider? Enter date as YYYY-MM-DD. If you would like to use the "
            "present, enter anything besides a date. \n")

        try:
            end_date = str(dt.fromisoformat(end_date))
        except:
            end_date = str(dt.today())

        start_date = input("What is the lower date you would like to consider? If you would like to use the begining of"
                           " the show, enter anything besides a date\n")

        try:
            start_date = str(dt.fromisoformat(start_date))
        except:
            start_date = str(dt.fromisoformat("1984-09-10"))

        mask = (df['date'] <= end_date) & (df['date'] > start_date)

        if userinput == "response_frequencies":

            sf = df.loc[mask]["response"].value_counts()

            responses = pd.DataFrame({"response": sf.index, "count": sf.values})

            for i in range(len(responses)):
                responses.at[i, 'response'] = name_cleaner(responses.at[i, 'response'])

            responses = responses.groupby(['response']).sum()

            responses = responses.sort_values(by=['count'], ascending=False, ignore_index=True)

            print(responses.head(500))

            responses.plot(logy=True)

            plt.ylabel('total number of answers')
            plt.xlabel('index')
            plt.show()

            responses.to_csv('response_count.csv', index=True)

            responses.plot.line()

        elif userinput == "response_frequencies_by_value":

            dfm = df.loc[mask]

            print("working...")

            # This is a huge pain, but it works effectively. In this chunk of code here, the specific rows of each point
            # value are added.

            j1cols = ['J1 200', 'J1 400', 'J1 600', 'J1 800', 'J1 1000']
            J1values = [200, 400, 600, 800, 1000]
            j2cols = ['J2 400', 'J2 800', 'J2 1200', 'J2 1600', 'J2 2000']
            J2values = [400, 800, 1200, 1600, 2000]

            answer_series_list = []

            for i in range(5):
                sf = dfm.loc[(dfm["jtype"] == 1) & (dfm["value"] == J1values[i])]["response"].value_counts()
                answer_series_list.append(pd.DataFrame({"response": sf.index, j1cols[i]: sf.values}))

            for i in range(5):
                sf = dfm.loc[(dfm["jtype"] == 2) & (dfm["value"] == J2values[i])]["response"].value_counts()
                answer_series_list.append(pd.DataFrame({"response": sf.index, j2cols[i]: sf.values}))

            print("working...")

            sf = dfm.loc[dfm["jtype"] == 0]["response"].value_counts()
            answer_series_list.append(pd.DataFrame({"response": sf.index, "final": sf.values}))
            print("working...")

            answers = pd.merge(answer_series_list[0], answer_series_list[1], on='response', how='outer')

            for i in range(2, 11):
                answers = pd.merge(answers, answer_series_list[i], on='response', how='outer')

            for i in range(len(answers)):
                answers.at[i, 'response'] = name_cleaner(answers.at[i, 'response'])

            print("working...")

            answers['total'] = answers.sum(axis=1, numeric_only=True)

            # In the next two "paragraphs", I'm creating the special columns for totals and average values within the
            # single and double Jeopardy tables. I also create the total point sum for these values.

            answers['J1 total'] = answers[j1cols].sum(axis=1, numeric_only=True)
            weight = pd.DataFrame([1, 2, 3, 4, 5], index=j1cols)
            answers['J1 average'] = 200 * (answers * weight[0]).sum(1)
            for i in range(len(answers)):
                if answers.at[i, 'J1 total'] != 0:
                    answers.at[i, 'J1 average'] = answers.at[i, 'J1 average'] / answers.at[i, 'J1 total']
                    answers.at[i, 'J1 interest'] = (answers.at[i, 'J1 average'] - 600) * answers.at[i, 'J1 total'] / 200
            answers['J1 average'] = answers['J1 average'].astype(float)

            answers['J2 total'] = answers[j2cols].sum(axis=1, numeric_only=True)
            weight = pd.DataFrame([1, 2, 3, 4, 5], index=j2cols)
            answers['J2 average'] = 400 * (answers * weight[0]).sum(1)
            for i in range(len(answers)):
                if answers.at[i, 'J2 total'] != 0:
                    answers.at[i, 'J2 average'] = answers.at[i, 'J2 average'] / answers.at[i, 'J2 total']
                    answers.at[i, 'J2 interest'] = (answers.at[i, 'J2 average'] - 1200) * answers.at[
                        i, 'J2 total'] / 200
            answers['J2 average'] = answers['J2 average'].astype(float)

            answers = answers.sort_values(by=['total'], ascending=False, ignore_index=True)
            print(answers.head(50))

            # After this, I create a table for the line graph showing how values in this table drop over time.

            inputed = False
            while inputed == False:
                print("What would you like to see?")
                print("1) line graphs showing frequencies of answers")
                print("2) A scatter plot of answer frequencies vs average values")
                print("3) The pareto front of a scatter plot of answer frequencies vs average values")
                print("4) A histogram of average point values for answers")
                print("5) A scatter plot displaying the highest interest regions against the other points")
                userinput = input()
                if userinput in ["1", "2", "3", "4", "5"]:
                    inputed = True
                else:
                    print("Please enter a valid input")

            if userinput == "1":

                answers['total'].plot(loglog=True)

                plt.ylabel('total number of answers')
                plt.xlabel('index')

                answers['total'].plot(loglog=True)

                xdata = np.array(range(1, 1 + len(answers)))
                xlogdata = np.log(xdata)
                ydata = answers['total'].values
                ylogdata = np.log(ydata)

                weights = np.array([1])
                for i in range(len(answers) - 1):
                    weights = np.append(weights, xlogdata[i + 1] - xlogdata[i])

                fit = np.polyfit(xlogdata, ylogdata, 2, w=weights)
                a = fit[0]
                b = fit[1]
                c = fit[2]

                plt.plot(xdata, np.exp(a * xlogdata ** 2 + b * xlogdata + c))
                plt.show()

                print("total fit:", fit)

                # And here, I make the tables comparing the answer frequencies and their curves of best fit

                j1colors = ['#ff0000', '#f39600', '#32f300', '#001ef3', '#9f00f3']
                j2colors = ['#840000', '#846400', '#008407', '#020084', '#560084']
                j1fits = []
                j2fits = []
                j1_column_lengths = []
                j2_column_lengths = []

                for i in range(5):
                    answers = answers.sort_values(by=[j1cols[i]], ascending=False, ignore_index=True)
                    answers[j1cols[i]].plot(loglog=True, label=j1cols[i], color=j1colors[i])
                    ydata = answers[j1cols[i]].dropna().values
                    ylogdata = np.log(ydata)
                    j1fits.append(np.polyfit(xlogdata[:len(ydata)], ylogdata, 2, w=weights[:len(ydata)]))
                    j1_column_lengths.append(len(ydata))

                for i in range(5):
                    answers = answers.sort_values(by=[j2cols[i]], ascending=False, ignore_index=True)
                    answers[j2cols[i]].plot(loglog=True, label=j2cols[i], color=j2colors[i])
                    ydata = answers[j2cols[i]].dropna().values
                    ylogdata = np.log(ydata)
                    j2fits.append(np.polyfit(xlogdata[:len(ydata)], ylogdata, 2, w=weights[:len(ydata)]))
                    j2_column_lengths.append(len(ydata))

                plt.ylabel('total number of answers')
                plt.xlabel('index')
                plt.legend()
                plt.show()

                for i in range(5):
                    plt.loglog(xdata[:j1_column_lengths[i]], np.exp(j1fits[i][0] * xlogdata[:j1_column_lengths[i]] ** 2
                                                                    + j1fits[i][1] * xlogdata[:j1_column_lengths[i]] +
                                                                    j1fits[i][2]),
                               label=j1cols[i], color=j1colors[i])

                for i in [0, 1, 2, 3, 4]:
                    plt.loglog(xdata[:j2_column_lengths[i]], np.exp(j2fits[i][0] * xlogdata[:j2_column_lengths[i]] ** 2
                                                                    + j2fits[i][1] * xlogdata[:j2_column_lengths[i]] +
                                                                    j2fits[i][2]),
                               label=j2cols[i], color=j2colors[i])

                plt.ylabel('total number of answers')
                plt.xlabel('index')
                plt.legend()
                plt.show()

                for i in j1fits:
                    print(i)
                for i in j2fits:
                    print(i)

            elif userinput == "2":

                answers.plot.scatter(x='J1 total', y='J1 average', s=1)
                plt.show()

                answers.plot.scatter(x='J2 total', y='J2 average', s=1)
                plt.show()

            elif userinput == "3":

                front1 = pareto_front_2D(answers, x='J1 total', y='J1 average', other=['response'])
                front2 = pareto_front_2D(answers, x='J2 total', y='J2 average', other=['response'])

                ax = answers.plot.scatter(x='J1 total', y='J1 average', s=1)
                front1.plot.line(x='J1 total', y='J1 average', ax=ax, color='orange')
                plt.show()

                ax = answers.plot.scatter(x='J2 total', y='J2 average', s=1)
                front2.plot.line(x='J2 total', y='J2 average', ax=ax, color='orange')
                plt.show()

                front1.to_csv('front1.csv', index=False)
                front2.to_csv('front2.csv', index=False)

            elif userinput == "4":

                answers[answers['J1 total'] > 3].hist(column='J1 average', bins=15)
                plt.show()

                answers[answers['J2 total'] > 3].hist(column='J2 average', bins=15)
                plt.show()

            elif userinput == "5":

                ax = answers.plot.scatter(x='J1 total', y='J1 average', s=1, color="blue")
                answers = answers.sort_values(by='J1 interest', ascending=False, ignore_index=True)
                answers.head(100).plot.scatter(x='J1 total', y='J1 average', ax=ax, s=1, color="orange")
                plt.show()

                ax = answers.plot.scatter(x='J2 total', y='J2 average', s=1, color="blue")
                answers = answers.sort_values(by='J2 interest', ascending=False, ignore_index=True)
                answers.head(100).plot.scatter(x='J2 total', y='J2 average', ax=ax, s=1, color="orange")
                plt.show()
            answers.to_csv('answers_ordered.csv', index=False)
    
    # As you might expect, this gives the number of correct responses, the proportion of correct responses, the coryat
    # score, and other important pieces of data to give an overview of ones performance each game.
    elif userinput == "accuracy_per_game":

        adf = df.dropna().copy()
        
        games = adf.value_counts(subset=["game_name", "date", "accuracy"])
        games = games.to_frame().reset_index()

        # Here, I'm separating those counts into discreet dataframes
        games_correct = games[games.accuracy == 1.0]
        games_skip = games[games.accuracy == 0.0]
        games_incorrect = games[games.accuracy == -1.0]

        # And here, I rename the rows so these dataframes can be
        games_correct = games_correct.drop('accuracy', axis=1)
        games_correct = games_correct.rename(columns={'count': 'correct'})
        games_skip = games_skip.drop('accuracy', axis=1)
        games_skip = games_skip.rename(columns={'count': 'skip'})
        games_incorrect = games_incorrect.drop('accuracy', axis=1)
        games_incorrect = games_incorrect.rename(columns={'count': 'incorrect'})

        # Here, I combine all those split dataframes into one big one.
        games = games_correct.merge(games_skip, on=['game_name', 'date'], how='outer')
        games = games.merge(games_incorrect, on=['game_name', 'date'], how='outer')

        games.fillna(0, inplace=True)
        games["total"] = games["correct"] + games["skip"] + games["incorrect"]

        games["correct_rate"] = (games["correct"] * 100) // games["total"]
        games["skip_rate"] = (games["skip"] * 100) // games["total"]
        games["incorrect_rate"] = (games["incorrect"] * 100) // games["total"]

        games["coryat"] = 0

        for index, row in adf.dropna().iterrows():
            coryat_adjuster = int(row["accuracy"]) * int(row["value"])
            games.loc[games["game_name"] == row["game_name"], "coryat"] += coryat_adjuster

        games.loc[games["total"] == 61, "complete"] = True
        df.sort_values('game_name')

        for idx in games.loc[games["complete"] != True].index:
            itr = 0
            while True:
                if df.loc[itr, "game_name"] == games.loc[idx, "game_name"] and not df.loc[itr, "accuracy"] in [-1, 0, 1]:
                    games.loc[idx, "complete"] = False
                    break
                elif df.loc[itr, "game_name"] < games.loc[idx, "game_name"]:
                    games.loc[idx, "complete"] = True
                    break
                itr += 1

        print(games.to_string())
        games[games['complete'] == True].hist(column='coryat', bins=15)
        plt.title('Distribution of Coryat scores')
        plt.show()

        # This reorganizes the dataframe in a way that makes graphing the cumulative distribution much easier
        games = games[games['complete'] == True]
        games = games.sort_values(by=['coryat'], ascending=True, ignore_index=True)
        games = games.reset_index(names='rank')
        games['rank'] = games['rank'].div(games['complete'].sum())

        # Here, I graph the full cumulative distribution of coryat scores
        min_coryat = games['coryat'].min()
        max_coryat = games['coryat'].max()
        ax = games.plot.line(x='coryat', y='rank', xlim=(min_coryat, max_coryat), ylim=(0, 1), legend=False)
        ax.fill_between(games['coryat'], games['rank'], alpha=0.2, where=(games['coryat'] >= min_coryat))
        ax.grid(True)

        # I want to add a few key points to add context to the previous graph. Here's how I do that.
        median_coryat = int(games['coryat'].median())
        median_coryat_label = "({},50%)".format(str(median_coryat))
        plt.plot(median_coryat, 0.5, marker='o', color='black')  # Add the point
        plt.annotate(median_coryat_label, (median_coryat, 0.5), textcoords="offset points", xytext=(6, 6), ha='right')  # Add the label

        total = len(games)
        benchmarks = [30000, 20000]

        for benchmark in benchmarks:
            if min_coryat < benchmark:
                ratio_under_bench = len(games[games.coryat < benchmark])/total
                ratio_label = "({},{}%)".format(str(benchmark), str(int(ratio_under_bench * 100)))
                plt.plot(benchmark, ratio_under_bench, marker='o', color='black')
                plt.annotate(ratio_label, (benchmark, ratio_under_bench), textcoords="offset points", xytext=(6, 6), ha='right')


        ax.set_xlabel('Coryat score')
        ax.set_ylabel('percentage under that score')
        plt.title('Cumulative distribution of Coryat scores')
        plt.gca().yaxis.set_major_formatter(PercentFormatter(1))
        plt.show()

    # This option analyzes all the already answered questions to look for patterns in the accuracy of topics.
    elif userinput == "accuracy_per_topic":

        # adf is the abbreviated dataframe, in fact, that's what adf stands for.
        # stdf is the simplified topic dataframe. We'll hope to do some more complicated analysis on topics later
        # I normally would be reluctant to choose such abbreviated names, as I find it can cause confusion. However,
        # due to the somewhat awkward way Pandas requires dataframe names to be repeated while altering dataframes,
        # it's just too temping to abbreviate in order to save space.

        adf = df.dropna().copy()
        stdf = pd.DataFrame(columns=["correct", "skip", "incorrect", "correct_score", "skip_score", "incorrect_score"])

        # Earlier drafts of this function used some fancy math to increment each column by index. While that made for
        # some nice code golf, it wasn't very easily readable. This provides a more human-friendly approach.
        accuracy_translator = {1: "correct", 0: "skip", -1: "incorrect"}
        score_translator = {1: "correct_score", 0: "skip_score", -1: "incorrect_score"}

        # This adds a row to stdf for each letter
        for char in ascii_lowercase:
            stdf.loc[char] = [0, 0, 0, 0, 0, 0]

        # this loop runs through adf and appends each question to stdf appropriately
        for index in range(len(adf)):
            for char in adf.loc[index, 'subjects']:
                stdf.loc[char, accuracy_translator[int(adf.loc[index, 'accuracy'])]] += 1
                stdf.loc[char, score_translator[int(adf.loc[index, 'accuracy'])]] += int(adf.loc[index, 'value'])

        # It feels important to drop the unused letter categories after calculating their total. The alternative is to
        # check all 3 other columns for 0s.

        stdf['total'] = stdf[["correct", "skip", "incorrect"]].sum(axis=1)
        stdf["total_score"] = stdf[["correct_score", "skip_score", "incorrect_score"]].sum(1)
        stdf.drop(stdf.loc[stdf['total'] == 0].index, inplace=True)

        stdf["correct_rate"] = stdf["correct"] / stdf["total"]
        stdf["skip_rate"] = stdf["skip"] / stdf["total"]
        stdf["incorrect_rate"] = stdf["incorrect"] / stdf["total"]
        stdf["average_value"] = stdf["total_score"] / stdf["total"]

        stdf = stdf.sort_values(by='correct_rate', ascending=True)

        stdf = stdf.rename(index=topic_dict)

        print(stdf.to_string())

        print("What data would you like to see?")
        print("1) Accuracy rate and quantity by topic")
        print("2) Scores by topic")
        answer = int(input())
        if answer == 1:
            # Here's me making a graph that relates the accuracy rates of all the different topics
            colors = ['deepskyblue', 'coral', 'red']
            ax = stdf[["correct_rate", "skip_rate", "incorrect_rate"]].plot.barh(xlim=(0, 1), stacked=True, width=0.94, color=colors)

            for i in range(len(stdf)):
                plt.text(0.01, i - 0.35, str(int(stdf["correct_rate"].iloc[i]*100)) + '%', ha='left')

            ax.set_ylabel('topic')
            ax.set_xlabel('accuracy')
            plt.title('Accuracy by topic')
            plt.gca().xaxis.set_major_formatter(PercentFormatter(1))
            ax.grid(True, axis='x')
            plt.show()

            # And here's me making a graph that relates the accuracy amounts of each topic
            stdf = stdf.sort_values(by='correct', ascending=True)

            max_total = stdf.total.max()

            ax = stdf[["correct", "skip", "incorrect"]].plot.barh(xlim=(0, max_total), stacked=True, width=0.94, color=colors)

            # Here's sort of a clunky method that I use to put the labels on this bar chart
            for i in range(len(stdf)):
                correct_str = str(int(stdf["correct"].iloc[i]))
                if stdf["correct"].iloc[i]/max_total > len(correct_str)/80:
                    plt.text(0.005 * max_total, i - 0.35, correct_str, ha='left')
                skip_str = str(int(stdf["skip"].iloc[i]) + int(stdf["incorrect"].iloc[i]))
                if stdf["skip"].iloc[i]/max_total > len(skip_str)/70:
                    plt.text(stdf["correct"].iloc[i] + 0.003 * max_total, i - 0.35, str(int(stdf["skip"].iloc[i]) + int(stdf["incorrect"].iloc[i])), ha='left')

            ax.set_ylabel('topic')
            ax.set_xlabel('count')
            plt.title('Accuracy by topic')
            ax.grid(True, axis='x')
            plt.show()

        elif answer == 2:

            stdf = stdf.sort_values(by='average_value', ascending=True)

            colors = ['deepskyblue', 'coral', 'red']

            max_value = stdf["average_value"].max()
            ax = stdf["average_value"].plot.barh(xlim=(600, 1200), width=0.94, color='deepskyblue')

            for i in range(len(stdf)):
                plt.text(605, i - 0.35, '$' + str(int(stdf["average_value"].iloc[i])), ha='left')

            ax.set_ylabel('topic')
            ax.set_xlabel('value')
            plt.title('Average value of hints by topic')
            ax.grid(True, axis='x')
            plt.show()

            # And here's me making a graph that relates the accuracy amounts of each topic
            stdf = stdf.sort_values(by='correct_score', ascending=True)
            total_score_possible = adf["value"].sum()

            stdf["correct_score_ratio"] = stdf["correct_score"].div(total_score_possible)
            stdf["skip_score_ratio"] = stdf["skip_score"].div(total_score_possible)
            stdf["incorrect_score_ratio"] = stdf["incorrect_score"].div(total_score_possible)

            max_total_ratio = stdf.total_score.max()/total_score_possible

            ax = stdf[["correct_score_ratio", "skip_score_ratio", "incorrect_score_ratio"]].plot.barh(xlim=(0, max_total_ratio),
                                                                                                      stacked=True, width=0.94,
                                                                                                      color=colors)

            # Here's sort of a clunky method that I use to put the labels on this bar chart
            for i in range(len(stdf)):

                correct_str = str(float(stdf["correct_score_ratio"].iloc[i]*100))[:3]+'%'
                if stdf["correct_score_ratio"].iloc[i] > len(correct_str) * max_total_ratio / 120:
                    plt.text(0.005 * max_total_ratio, i - 0.35, correct_str, ha='left')

                skip_str = str(float(stdf["skip_score_ratio"].iloc[i]*100) + float(stdf["incorrect_score_ratio"].iloc[i]*100))[:3] + '%'
                if stdf["skip_score_ratio"].iloc[i] > len(skip_str) * max_total_ratio / 120:
                    plt.text(stdf["correct_score_ratio"].iloc[i] + 0.003 * max_total_ratio, i - 0.35, skip_str, ha='left')

            ax.set_ylabel('topic')
            ax.set_xlabel('percentage')
            plt.title('Breaking down score by topic')
            ax.grid(True, axis='x')
            plt.show()

            # I want to make one more version of this chart, resembling something more like a population pyramid

            stdf = stdf.sort_values(by='total_score', ascending=True)
            graph_width = max(stdf["correct_score_ratio"].max(), stdf["incorrect_score_ratio"].max()
                              + stdf["skip_score_ratio"].max()) * 1.1
            stdf["correct_score_ratio"] = stdf["correct_score_ratio"] * (-1)

            ax = stdf[["correct_score_ratio", "skip_score_ratio", "incorrect_score_ratio"]].plot.barh(
                xlim=(-graph_width, graph_width), stacked=True, width=0.94, color=colors)

            stdf["correct_score_ratio"] = stdf["correct_score_ratio"] * (-1)

            for i in range(len(stdf)):

                correct_str = str(float(stdf["correct_score_ratio"].iloc[i] * 100))[:3] + '%'
                skip_str = str(float(stdf["skip_score_ratio"].iloc[i] * 100) +
                               float(stdf["incorrect_score_ratio"].iloc[i] * 100))[:3] + '%'

                plt.text(-stdf["correct_score_ratio"].iloc[i], i - 0.35, correct_str, ha='right')
                plt.text(stdf["skip_score_ratio"].iloc[i] + stdf["incorrect_score_ratio"].iloc[i], i - 0.35, skip_str, ha='left')

            ax.set_ylabel('topic')
            ax.set_xlabel('percentage')
            plt.title('Breaking down score by topic')
            plt.gca().xaxis.set_major_formatter(PercentFormatter(1))
            ax.grid(True, axis='x')
            plt.show()

        else:
            print("not a valid input.")

    # Just in case there are duplicates, here we remove them.
    elif userinput == "remove_duplicates":
        df = df.drop_duplicates(subset=["date", "hint"])

        df.to_csv('jeopardydata.csv', index=False)

    # Converts all dates to strings, if they aren't already.
    elif userinput == "convert_dates":
        for i in range(len(df)):
            if i % 10000 == 0:
                print(i)
            try:
                df.at[i, 'date'] = str(df.at[i, 'date'])
            except:
                # break
                pass

        df.to_csv('jeopardydata.csv', index=False)

# Here's the to-do's for this project:
# 2) code in a way to look at ones accuracy over a stretch of time. Both by percentage, and by Coryat score. Both by
#       game, and by stretch of time.
# 3) Same as #2, but organized by subject
# 4) See all the answered/unanswered questions within a subject
