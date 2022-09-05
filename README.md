# CS50 FINAL PROJECT / TITLE: Reservation System

#### Video Demo: ???

#### Description:

Hey everyone, i will try to describe my humble cs50 final project which is full-stack web application developed as freshman. This project imitates reservation system where teachers (this website is focused on education) can create / delete lecture sessions entering proper inputs and students can attend. Main focus was on back-end rather than front-end except the homepage where i put some effort to get great homepage which may be good for first impression.

Techonologies employed:

-sqlite
-html
-css
-flask

Features:

-create session
-register session
-monitor participants
-take attendance
- mail verification after registering

#### Walkthrough of the Website

I aimed to be user-friendly as much as possible. First you are directed to homepage where you see href's to external social media sites, login boxes and importantly register button. After registering (there is a mail validation to prevent unexpected behaviours). After logging in if you are a teacher or admin you can create and delete sessions with buttons above and you can take attendance after checking participants, whereas students only see register button for those created sessions.

#### My Mistakes

I am not really big fan of front-end and sometimes css codes got messy but it is actually good mistake since that gave me an opportunity to come up with better design and css coding.
After completing the project i realized that mongo was a better choice than sqlite since i built database vertically most of time rather than horizontally. So, strong side of sql (keys and association of different components) was not that helpful.
Input checks might have been designed better.

#### Files and What They Do

template file, as name suggests, used to avoid redundancy and it holds fixed parts of website such as navigation bar etc.
static folder contains nearly all elements related to front-end like styles.css and so on
db file basically holds all database
application.py is the part where all routing and directing checks are done
helpers.py error-checkings and some required functions like isAdmin (to see if user is teacher or not) are implemented here
Others all these html files under templates folder are basically different html files where names actually gives a idea


#### Screenshots of the Web App

![Screenshot1](https://user-images.githubusercontent.com/67153015/188485551-b7165725-703e-4a7e-bfdb-adf8b3bcd903.png)
![Screenshot2](https://user-images.githubusercontent.com/67153015/188485584-ae4c73aa-2e4f-4c44-a6d3-56946a810df9.png)
![Screenshot3](https://user-images.githubusercontent.com/67153015/188485591-9e69fe4d-486f-4b27-bbc9-46792a7ecd7d.png)
![Screenshot4](https://user-images.githubusercontent.com/67153015/188485599-2b2dafff-8367-480f-843c-6a8c9d6ddfeb.png)
![Screenshot5](https://user-images.githubusercontent.com/67153015/188485605-9dfed781-1b84-47fc-ad71-6b07841a1193.png)
![Screenshot6](https://user-images.githubusercontent.com/67153015/188485611-82797257-ff1f-4e51-81cf-fd40677c00d4.png)
