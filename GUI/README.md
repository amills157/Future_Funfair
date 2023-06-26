# Future Funfair - GUI
### File Structure
`html`: contains all html files - there is one of the menu (this is the main script to be run), and one for each attack
`js`: contains all .js files, contains one for the menu and one for each attack
`styles.css`: contains styling for all html pages

### Running the Web App
The UI has been designed to run from a simple web server. To run with a minimal setup you can use the python `http.server` module - This should be run from within the base `GUI` folder:

`python -m http.server` (python3)

This will default to http://localhost:8000

When you first load the page it will show the content of the `GUI` folder. Click through html -> menu.html. This will then load the main menu / homepage. 

From there you can navigate the UI as you would any website, using the inbuilt buttons and options. 

### Using this in the activity
This UI is designed for use as part of the Future Funfair activity. It contains all information based on the attacks that currently work on the system as well as a (simple) breakdown of what a Cyber Physical System is and a link to local CyBoK material. 

As the UI (and wider activity) is designed to run in a local access network there are no external links to resources. 

### Updating the UI
###### Adding New Attacks:
If you wish to add new attacks, please create a new html and js file. You can copy the contents of any of the current attack files and change the information as necessary. 

###### Adapting the Current Attacks:
Currently, the information displayed on the web page is found within the .html file and can be updated from here.