me.setGlobalVariable("faction",None)

def pileName(group):
	if group.name == 'Table': name = 'Table'
	elif group.name == 'Heap/Archives(Face-up)':
		if group.player.getGlobalVariable('ds') == 'corp': name = 'Face-up Archives'
		else: name = 'Heap'
	elif group.name == 'R&D/Stack':
		if group.player.getGlobalVariable('ds') == 'corp': name = 'R&D'
		else: name = 'Stack'
	elif group.name == 'Archives(Hidden)': name = 'Hidden Archives'
	else:
		if group.player.getGlobalVariable('ds') == 'corp': name = 'HQ'
		else: name = 'Grip'
	return name

def shuffle(group):
	group.shuffle()

def drawMany(group, count = None, destination = None, silent = False):
	mute()
	if destination == None: destination = me.hand
	SSize = len(group)
	if SSize == 0: return 0
	if count == None: count = askInteger("Draw how many cards?", 5)
	if count == None: return 0
	for c in group.top(count):
		c.moveTo(destination)
	notify("{} draws {} cards.".format(me, count))
	return count

def mill(group):
	if len(group) == 0: return
	mute()
	count = askInteger("Mill how many cards?", 1)
	if count == None: return
	if me.getGlobalVariable("faction") == "runner": destination = me.piles['Heap/Archives(Face-up)']
	else: destination = me.piles['Archives(Hidden)']
	for c in group.top(count): c.moveTo(destination)
	notify("{} mills the top {} cards from their {} to {}.".format(me, count,pileName(group),pileName(destination)))

def moveXtopCardtoBottomStack(group):
	mute()
	if len(group) == 0: return
	count = askInteger("Move how many cards?", 1)
	if count == None: return
	for c in group.top(count): c.moveToBottom(group)
	notify("{} moves the top {} cards from their {} to the bottom of {}.".format(me, count,pileName(group),pileName(group)))

def draw(group):
	mute()
	card = group.top()
	card.moveTo(me.hand)
	notify("{} draws a card".format(me))