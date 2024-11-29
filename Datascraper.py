# See PyCharm help at https://www.jetbrains.com/help/pycharm/
import requests
from bs4 import BeautifulSoup
import re
import pandas

class clue:

    clue: str
    answer: str
    category: str
    value: int
    jtype: int
    media: bool
    DD: bool
    date: str
    game_name: str

    def __init__(self, hint:str = "", answer:str = "", category:str = "", value:int = 0, jtype:int = 0, media:bool = False, DD:bool = False, date: str = "", game_name: str = ""):

        self.hint = hint
        self.answer = answer
        self.category = category
        self.value = value
        self.jtype = jtype
        self.media = media
        self.DD = DD
        self.date = date
        self.game_name = game_name


    def printclue(self):
        print(self.category + " | " + self.hint + " | " + self.answer + " | " + str(self.value) + " | " + str(self.media) + " | " + str(self.DD))

    def gain_category(self, categories: list[str]):

        index = int(self.category) - 1
        self.category = categories[index]

    def cleanstring(self, word:str):
        word = word.replace("&amp;", "&")
        word = word.replace("\\", "")
        word = word.replace("<span class=\"nobreak\">--</span>", ". ")
        word = word.replace("<br/>", "")

        return word

    def cleanself(self):
        self.category = self.cleanstring(self.category)
        self.hint = self.cleanstring(self.hint)
        self.answer = self.cleanstring(self.answer)

    def removeLink(self):
        if self.hint.find("</a>") == -1:
            self.media = False
        else:
            self.hint = self.hint.replace("</a>", "")
            self.hint = re.sub("<a href=\"https://www\.j-archive\.com/media/.*\" target=\"_blank\">", "", self.hint)
            self.media = True

    def makelist(self):

        return [self.category, self.hint, self.answer, self.value, self.jtype, self.media, self.DD, self.date, self.game_name, "", "", ""]


#Takes in a board, which is a string of html code, and returns only the useful lines
def strip_board(board):
    newboard = board.split('\n')
    categories = []
    clues = []

    for line in newboard:
        if len(line) > 23:
            if (line.find("<tr><td class=\"category_name\">") != -1) or (line.find("<tr><td class=\"category_comments\">(") != -1):
                categories.append(line)
            if (line.find("<td class=\"clue_text\" id=") != -1) or (line.find("<td class=\"clue_value_daily_double\">DD:") != -1):
                clues.append(line)

    return clues, categories

# Takes in a stretch of relevant lines, and returns only their segments that corespond to clues. Add's Ken's hints when appropriate.
def define_categories(cats):
    newcats = []
    for line in cats:
        if (line.find("<tr><td class=\"category_name\">") != -1):
            newcats.append(line[30:-10])
        if (line.find("<tr><td class=\"category_comments\">(") != -1):
            if len(newcats) != 0:
                newcats[-1] = newcats[-1] + " -- " + line[35:-12]

    return newcats

# This returns an array of "clues", which is an object previously defined
def define_clues(clues, jtype, date, game_name):

    newclues = []
    holdDD = True

    for line in clues:
        if(line.find("<td class=\"clue_value_daily_double\">DD:") != -1):
            holdDD = True
        else:
            #there's an extra letter added for double and triple jeopardy. I'm adding that in here.
            exta_letter = 0
            if jtype != 1:
                exta_letter = 1
            if line[37+ + exta_letter] == ">":
                newclues.append(clue(jtype = jtype, DD = holdDD, date = date, game_name= game_name))
                holdDD = False
                newclues[-1].hint = line[38+exta_letter:-5]
            else:
                hold = line.split("correct_response\">")[1].split("</em>")[0]
                if hold[:3] == "<i>":
                    newclues[-1].answer = hold[3:-4]
                else:
                    newclues[-1].answer = hold
                newclues[-1].category = line[33+exta_letter]
                newclues[-1].value = int(line[35+exta_letter]) * 200 * jtype

    return newclues

#Assigns categories to the clues defined earlier
def give_categories(clues: list, categories: list[str]):

    for clue in clues:
        clue[2] = categories[int(clue[2])-1]

    return clues

#Assigns a point value to the clue defined earlier. jtype is the jeopardy round. 1 for single Jeopardy, 2 for double, and 0 for final.
def give_values(clues: list, jtype: int):

    for clue in clues:
        clue[-1] = int(clue[-1]) * jtype * 200

    return clues

def extract_date(line:str):

    line = line.split("aired")[1]

    return line[1:-8]

def extract_game_name(line:str):

    line = line.split("Archive - ")[1]
    line = line.split(", aired")[0]

    print(line)

    return line

def webpage_to_dataframe(webpage: str):

    webpage_response = requests.get(webpage)

    webpage = webpage_response.content

    soup = BeautifulSoup(webpage, "html.parser")
    soup = str(soup)

    date = extract_date(soup.split("\n")[12])
    game_name = extract_game_name(soup.split("\n")[12])

    #This is an array that keeps track of which rounds exist within the game. The first item corresponds to single jeopardy, then double, triple, and final
    roundCounter = []

    split_names = ["<h2>Jeopardy! Round</h2>", "<h2>Double Jeopardy! Round</h2>", "<h2>Triple Jeopardy! Round</h2>", "<h2>Final Jeopardy! Round</h2>"]

    for line in split_names:
        if soup.find(line) != -1:
            roundCounter.append(1)
        else:
            roundCounter.append(0)

    df = pandas.DataFrame([], columns=['category', 'hint', 'answer', 'value', 'jtype', 'media', 'DD', 'date', 'game_name', 'correct', 'subjects', 'date_answered'])

    for i in range(1,5):
        if roundCounter[-i] == 1:

            soup = soup.split(split_names[-i])
            clues, categories = strip_board(soup[1])
            soup = soup[0]

            if i == 1:
                category = define_categories(categories)[0]
                hint = clues[0][35:-6]
                answer = clues[1].split("correct_response")[-1][2:-10]

                fjclue = clue(hint= hint, answer= answer, category= category, date= date, game_name= game_name, value= 0, jtype= 0)
                fjclue.removeLink()
                fjclue.cleanself()

                if fjclue.answer != "=":
                    df.loc[-1] = fjclue.makelist()
                    df.index = df.index + 1

            else:
                categories = define_categories(categories)
                clues = define_clues(clues, 5-i, date= date, game_name= game_name)

                for i in clues:
                    i.gain_category(categories)
                    i.cleanself()
                    i.removeLink()
                    i.date = date

                    if i.answer != "=":
                        df.loc[-1] = i.makelist()
                        df.index = df.index + 1


    df = df.sort_values(by = ["jtype", "category", 'value'], ignore_index= True)

    return df


#given a particular game of jeopardy, gives the URL of the next game after that one as a string
def nextgame(webpage: str):

    webpage_response = requests.get(webpage)

    webpage = webpage_response.content

    soup = BeautifulSoup(webpage, "html.parser")
    soup = str(soup)

    soup = soup.split("\n")

    link = ""

    for line in soup:
        if (line.find("next game ") != -1):
            link = line
            break

    if link == "":
        return "none"

    link = link.split("game_id=")[1]
    link = link.split("next game")[0][:-3]
    link = "https://j-archive.com/showgame.php?game_id=" + link

    return link

#given a particular game of jeopardy, gives the URL of the last game before that one as a string
def prevgame(webpage: str):

    webpage_response = requests.get(webpage)

    webpage = webpage_response.content

    soup = BeautifulSoup(webpage, "html.parser")
    soup = str(soup)

    soup = soup.split("\n")

    link = ""

    for line in soup:
        if (line.find("previous game") != -1):
            link = line
            break

    if link == "":
        return "none"

    link = link.split("game_id=")[1]
    link = link.split("previous game")[0][:-12]
    link = "https://j-archive.com/showgame.php?game_id=" + link

    return link

# this function looks to find what the most recent game on the jeopardy archive is, and returns the url as a string
def recentGame():

    webpage_response = requests.get("https://j-archive.com/index.php")

    webpage = webpage_response.content

    soup = BeautifulSoup(webpage, "html.parser")
    soup = str(soup)

    soup = soup.split("\n")

    link = ""

    for line in soup:
        if (line.find("from show #") != -1):
            link = line
            break

    link = link.split("game_id=")[1]
    link = link.split("from show")[0][:-2]
    link = "https://j-archive.com/showgame.php?game_id=" + link

    return link

#the season in question here is the URL of a season's directory as a string. Returns a list of games in that season.
def find_games_in_season(webpage):

    webpage_response = requests.get(webpage)
    webpage = webpage_response.content
    soup = BeautifulSoup(webpage, "html.parser")
    soup = str(soup)
    soup = soup.split("\n")

    links = []

    for line in soup:
        if line.find("showgame.php?game_id=") != -1:
            hold = line.split("showgame.php?game_id=")[1]
            hold = hold.split("\"")[0]

            hold = "https://j-archive.com/showgame.php?game_id=" + hold

            links.append(hold)

    return links

def find_seasons():

    webpage_response = requests.get("https://j-archive.com/listseasons.php")
    webpage = webpage_response.content
    soup = BeautifulSoup(webpage, "html.parser")
    soup = str(soup)
    soup = soup.split("\n")

    links = []

    for line in soup:
        if line.find("showseason.php?season=") != -1:
            hold = line.split("showseason.php?season=")[1]
            hold = hold.split("\"")[0]

            hold = "https://j-archive.com/showseason.php?season=" + hold

            links.append(hold)

    return links