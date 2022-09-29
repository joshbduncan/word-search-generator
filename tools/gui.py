from word_search_generator import WordSearch
import PySimpleGUI as sg, os, urllib.request as urlreq, random

def get_words(number,min):
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
	filename, extension = os.path.splitext(path)
	counter = 1

	while os.path.exists(path):
		path = filename + "(" + str(counter) + ")" + extension
		counter += 1

	return path

sg.theme('BluePurple')   # Add a touch of color
help_Path = """Output Path:
	The folder you want to save the puzzle to. 
	Note: Do not include a name.
"""
help_Size = """Level 1 (Easy): 
	Words can go forward in directions EAST (E), or SOUTH (S).
	
Level 2 (Intermediate): 
	Words can go forward in directions NORTHEAST (NE), EAST (E), SOUTHEAST (SE), or (S).
	
Level 3 (Expert): 
	Words can go forward and backward in directions NORTH (N), NORTHEAST (NE), EAST (E), SOUTHEAST (SE), SOUTH (S), SOUTHWEST (SW), WEST (W), or NORTHWEST (NW).

Sizes: 
	All puzzles are square so size will be the width and height. Puzzles are limited to 25 characters wide so that everything fits nicely on a US Letter or A4 sized sheet of paper.
"""
help_file_name = """Do not include file extensions in the name.
Note: Filenanes will be appended with a number if it already exists.
"""
default_path = "{}\\Documents".format(os.path.expanduser('~')).replace("\\", "/")

file_types = ['pdf', 'csv']

# All the stuff inside your window.
layout = [  [   sg.Text('Word Search Generator',size=('45','1'))],
			[   sg.Text('Output file Path',size=('15','1')), 
				sg.Text(default_path, key='out_folder',background_color='lightGrey',text_color='Black',size=('38','1')),
				sg.FolderBrowse(target='out_folder', key='path_button',size=('7','1'))],
			[   sg.Text('Filename:',size=('15','1')), 
				sg.InputText("Word Search",key="file_name", size=('45','1'),background_color='azure2'),
				sg.Button('Help', key='file_name_help',size=('5','1'))],
			[   sg.Text('File Type',size=('15','1')),
				sg.Combo(list(file_types), 'pdf', readonly=True, key='type',size=('8','10'),background_color='azure2')],
			[   sg.Text('Dificalty Level',size=('15','1')), 
				sg.Combo(['1','2','3'],"2",key="level", size=('8','3'),background_color='azure2'),
				sg.Text(' ',size=('6','1')),
				sg.Text('Puzzel Size',size=('11','1')),
				sg.Combo(list(range(10, 26)),"15",key="size",size=('8','16'),background_color='azure2'),
				sg.Button('Help', key='size_help',size=('5','1'))],
			[   sg.Checkbox('Randomize',key='random', enable_events=True,size=('12','1')),
				sg.Text('Word count',size=('8','1')),
				sg.Combo(list(range(5, 31)),"15",key="rwcount",size=('8','16'),background_color='azure2',disabled=True),
				sg.Text('Min length',size=('9','1')),
				sg.Combo(list(range(4, 13)),"5",key="rwlen",size=('8','16'),background_color='azure2',disabled=True),],
			[   sg.Button('Create', key='Create'), 
				sg.Button('Done')],
			[   sg.Text('Input up to 30 words, one word per line.')],
			[   sg.Multiline(size=(69, 25), key='textbox',background_color='azure2')]
		]  # identify the multiline via key option

# Create the Window
window = sg.Window('Word Search Generator', layout).Finalize()
#window.Maximize()
# Event Loop to process "events" and get the "values" of the inputs
while True:
	event, values = window.read()
	if event == 'Path_help':
		sg.Popup(help_Path, keep_on_top=True)
		
	elif event == 'size_help':
		sg.Popup(help_Size, keep_on_top=True)
		
	elif event == 'file_name_help':
		sg.Popup(help_file_name, keep_on_top=True)
		
	elif event == 'path_button':
		default_path = values['default_path']
		
	elif event == 'Create': #Create the puzzles.
		desired_output = "{}/{}.{}".format(default_path,values['file_name'],values['type'])
		Output = unique_path(desired_output)
		
		if values['random'] == True:
			wordlist = ', '.join(get_words(values['rwcount'],values['rwlen']))
		else:
			wordlist = values['Textbox']
			
		puzzle = WordSearch(
			wordlist, 
			level=int(values['level']), 
			size=int(values['size'])
		)
		
		puzzle.show(solution=True)
		puzzle.save(path=Output, solution=True)
		message="""Word Search has been saved to: 
	{}""".format(Output)
		sg.Popup(message, keep_on_top=True)
	elif event in (None, 'Done'): # if user closes window or clicks cancel
		break
	
	if ((event == 'random') and (values['random'] == True)):
		window['textbox'].update(disabled=True)
		window['textbox'].update(value='')
		window['textbox'].update(background_color='lightGrey')
		window['rwcount'].update(disabled=False)
		window['rwlen'].update(disabled=False)
		
	if ((event == 'random') and (values['random'] == False)):
		window['textbox'].update(disabled=False)
		window['textbox'].update(background_color='azure2')
		window['rwcount'].update(disabled=True)
		window['rwlen'].update(disabled=True)
	
window.close()
