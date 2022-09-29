from word_search_generator import WordSearch
import PySimpleGUI as sg, os, urllib.request as urlreq, random

def get_words(number,min):
    # number is the count of words. Min is the minimum length the words should be.
	word_site = "https://www.mit.edu/~ecprice/wordlist.10000"
	response = urlreq.urlopen(word_site).read().decode().splitlines()
	words = []
	for x in range(number):
		while True:
			word = random.choice(response)
			if len(word) >= min:
				words.append(word)
				break
	return words

def unique_path(path):
    # Adds "(x)" to the filename if already exists where x is an itteritive number.
	filename, extension = os.path.splitext(path)
	counter = 1
	while os.path.exists(path):
		path = filename + "(" + str(counter) + ")" + extension
		counter += 1
	return path

# Add a touch of color
sg.theme('BluePurple')

# Help Text for the filename field
help_file_name = """Do not include file extensions in the name.
\tNote: Filenanes will be appended with a number if it already exists.
"""

# Help Text for the level and size fields
help_Size = """Level 1 (Easy):
\tWords can go forward in directions EAST (E), or SOUTH (S).

Level 2 (Intermediate):
\tWords can go forward in directions NORTHEAST (NE), EAST (E), SOUTHEAST (SE), or (S).

Level 3 (Expert):
\tWords can go forward and backward in directions NORTH (N), NORTHEAST (NE), EAST (E), SOUTHEAST (SE), SOUTH (S), SOUTHWEST (SW), WEST (W), or NORTHWEST (NW).

Sizes:
\tAll puzzles are square so size will be the width and height. Puzzles are limited to 25 characters wide so that everything fits nicely on a US Letter or A4 sized sheet of paper.
"""

# Sets the default path to the documents folder.
default_path = "{}\\documents".format(os.path.expanduser('~')).replace("\\", "/")

# Building out the UI
layout = [  [   sg.Text('Word Search Generator',size=('45','1'))],
			[   sg.Text('Output file Path',size=('15','1')),
				sg.Text(default_path, key='out_folder',background_color='lightGrey',text_color='Black',size=('38','1')),
				sg.FolderBrowse(target='out_folder', key='path_button',size=('7','1'))],
			[   sg.Text('Filename:',size=('15','1')),
				sg.InputText("Word Search",key="file_name", size=('45','1'),background_color='azure2'),
				sg.Button('Help', key='file_name_help',size=('5','1'))],
			[   sg.Text('File Type',size=('15','1')),
				sg.Combo(list(['pdf', 'csv']), 'pdf', readonly=True, key='type',size=('8','10'),background_color='azure2')],
			[   sg.Text('Dificalty Level',size=('15','1')),
				sg.Combo(['1','2','3'],"2",key="level", size=('8','3'),background_color='azure2'),
				sg.Text(' ',size=('6','1')),
				sg.Text('Puzzle Size',size=('11','1')),
				sg.Combo(list(range(10, 26)),"15",key="size",size=('8','16'),background_color='azure2'),
				sg.Button('Help', key='size_help',size=('5','1'))],
			[   sg.Checkbox('Randomize',key='random', enable_events=True,size=('12','1')),
				sg.Text('Word count',size=('8','1')),
				sg.Combo(list(range(5, 31)),"15",key="rwcount",size=('8','16'),background_color='azure2',disabled=True),
				sg.Text('Min length',size=('9','1')),
				sg.Combo(list(range(4, 13)),"5",key="rwlen",size=('8','16'),background_color='azure2',disabled=True),],
			[   sg.Checkbox('Include Answer',key='answer',size=('12','1')),
				sg.Button('Create', key='Create'),
				sg.Button('Done')],
			[   sg.Text('Input up to 30 words, one word per line.')],
			[   sg.Multiline(size=(69, 25), key='textbox',background_color='azure2')]
		]  # identify the multiline via key option

# Create the Window
window = sg.Window('Word Search Generator', layout).Finalize()

# Event Loop to process "events" and get the "values" of the inputs
while True:
	event, values = window.read()

	# Show help text for puzzle size.
	if event == 'size_help':
		sg.Popup(help_Size, keep_on_top=True)

	# Show help text for file names.
	elif event == 'file_name_help':
		sg.Popup(help_file_name, keep_on_top=True)

	# Browsing for the output folder.
	elif event == 'path_button':
		default_path = values['default_path']

	# Create button was pushed.
	elif event == 'Create':
		desired_output = "{}/{}.{}".format(default_path,values['file_name'],values['type'])
		Output = unique_path(desired_output)

		# Use random words or textbox words
		if values['random'] == True:
			wordlist = ', '.join(get_words(values['rwcount'],values['rwlen']))
		else:
			wordlist = values['Textbox']

		# Creating the Puzzle
		puzzle = WordSearch(
			wordlist,
			level=int(values['level']),
			size=int(values['size'])
		)

		# Saving to disk
		if values['answer'] == True:
			puzzle.save(path=Output, solution=True)
		else:
			puzzle.save(path=Output, solution=False)

		# Telling you that it saved and where it saved to.
		message="Word Search has been saved to: \n\t{}".format(Output)
		sg.Popup(message, keep_on_top=True)

	 # Enable randomized options when randomize is checked and disable the textbox.
	elif ((event == 'random') and (values['random'] == True)):
		window['textbox'].update(disabled=True)
		window['textbox'].update(background_color='lightGrey')
		window['rwcount'].update(disabled=False)
		window['rwlen'].update(disabled=False)

	# Disable randomized options when randomize is checked and Enable the textbox.
	elif ((event == 'random') and (values['random'] == False)):
		window['textbox'].update(disabled=False)
		window['textbox'].update(background_color='azure2')
		window['rwcount'].update(disabled=True)
		window['rwlen'].update(disabled=True)

	# if user closes window or clicks cancel
	elif event in (None, 'Done'):
		break

window.close()
