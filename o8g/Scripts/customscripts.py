    # Python Scripts for the Android:Netrunner LCG definition for OCTGN
    # Copyright (C) 2012  Konstantine Thoukydides

    # This python script is free software: you can redistribute it and/or modify
    # it under the terms of the GNU General Public License as published by
    # the Free Software Foundation, either version 3 of the License, or
    # (at your option) any later version.

    # This program is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU General Public License for more details.

    # You should have received a copy of the GNU General Public License
    # along with this script.  If not, see <http://www.gnu.org/licenses/>.

###==================================================File Contents==================================================###
# This file contains the autoscripting for cards with specialized effects. So called 'CustomScripts'
# * UseCustomAbility() is used among other scripts, and it just one custom ability among other normal core commands
# * CustomScipt() is a completely specialized effect, that is usually so unique, that it's not worth updating my core commands to facilitate it for just one card.
###=================================================================================================================###

collectiveSequence = []

def UseCustomAbility(Autoscript, announceText, card, targetCards = None, notification = None, n = 0):
   global reversePlayerChk
   if fetchProperty(card, 'name') == "Tollbooth":
      targetPL = findOpponent()
      # We reverse for which player the reduce effects work, because we want cards which pay for the opponent's credit cost to take effect now.
      reduction = reduceCost(card, 'FORCE', 3, True, reversePlayer = True) # We use a dry-run to see if they have a card which card reduce the tollbooth cost such as stimhack
      if reduction > 0: extraText = " (reduced by {})".format(uniCredit(reduction))  
      elif reduction < 0: extraText = " (increased by {})".format(uniCredit(abs(reduction)))
      else: extraText = ''
      if targetPL.Credits >= 3 - reduction: 
         targetPL.Credits -= 3 - reduceCost(card, 'FORCE', 3, reversePlayer = True)
         announceString = announceText + ' force {} to pay {}{}'.format(targetPL,uniCredit(3),extraText)
      else: 
         jackOut(silent = True)
         announceString = announceText + ' end the run'
   if fetchProperty(card, 'name') == "Datapike":
      targetPL = findOpponent()
      # We reverse for which player the reduce effects work, because we want cards which pay for the opponent's credit cost to take effect now.
      reduction = reduceCost(card, 'FORCE', 2, True, reversePlayer = True) # We use a dry-run to see if they have a card which card reduce the tollbooth cost such as stimhack
      if reduction > 0: extraText = " (reduced by {})".format(uniCredit(reduction))  
      elif reduction < 0: extraText = " (increased by {})".format(uniCredit(abs(reduction)))
      else: extraText = ''
      if targetPL.Credits >= 2 - reduction: 
         targetPL.Credits -= 2 - reduceCost(card, 'FORCE', 2, reversePlayer = True)
         announceString = announceText + ' force {} to pay {}{}'.format(targetPL,uniCredit(2),extraText)
      else: 
         jackOut(silent = True)
         announceString = announceText + ' end the run'
   if fetchProperty(card, 'name') == "Replicator":
      targetC = targetCards[0] # For this to be triggered a program has to have been installed, which was passed to us in an array.
      if not confirm("Would you like to replicate the {}?".format(targetC.name)):
         return 'ABORT'
      retrieveResult = RetrieveX('Retrieve1Card-grab{}-isTopmost'.format(targetC.name.replace('-','_')), announceText, card)
      shuffle(me.piles['R&D/Stack'])
      if re.search(r'no valid targets',retrieveResult[0]): announceString = "{} tries to use their replicator to create a copy of {}, but they run out of juice.".format(me,targetC.name) # If we couldn't find a copy of the played card to replicate, we inform of this
      else: announceString = "{} uses their replicator to create a copy of {}".format(me,targetC.name)
      notify(announceString)
   if fetchProperty(card, 'name') == "Data Hound":
      count = askInteger("By which amount of trace strength did you exceeded the runner's link strength?",1)
      if not count: return 'ABORT'
      targetPL = findOpponent()
      addGroupVisibility(targetPL.piles['R&D/Stack'],me) # Workaround for OCTGN bug #1242
      grabPileControl(targetPL.piles['R&D/Stack'])
      targetPL.piles['R&D/Stack'].addViewer(me)
      cardList = list(targetPL.piles['R&D/Stack'].top(count)) # We make a list of the top cards the corp can look at.
      debugNotify("Turning Runner's Stack Face Up", 2)
      if len(cardList): loopChk(cardList[len(cardList) - 1])
      if len(cardList) > 1:
         notify(":> {}'s Data Hound is sniffing through {}'s Stack".format(me,targetPL))
         choice = SingleChoice("Choose card to trash", makeChoiceListfromCardList(cardList))
         trashedC = cardList.pop(choice)
      else: trashedC = cardList.pop(0)
      debugNotify("Trashing {}".format(trashedC), 2)
      sendToTrash(trashedC)
      if len(cardList) > 1: notify("{}'s Data Hound has sniffed out and trashed {} and is now reorganizing {}'s Stack".format(me,trashedC,targetPL))
      else: notify("{} has sniffed out and trashed {}".format(me,trashedC))
      idx = 0 # The index where we're going to be placing each card.
      while len(cardList) > 0:
         if len(cardList) == 1: choice = 0
         else: choice = SingleChoice("Choose card put on the {} position of the Stack".format(numOrder(idx)), makeChoiceListfromCardList(cardList))
         movedC = cardList.pop(choice)
         movedC.moveTo(targetPL.piles['R&D/Stack'],idx) # If there's only one card left, we put it in the last available index location in the Stack. We always put the card one index position deeper, because the first card is the cover.
         idx += 1
      debugNotify("Removing Visibility", 2)
      rnd(1,100) # Delay to be able to announce names.
      targetPL.piles['R&D/Stack'].removeViewer(me)
      passPileControl(targetPL.piles['R&D/Stack'],targetPL)
      delGroupVisibility(targetPL.piles['R&D/Stack'],me) # Workaround for OCTGN bug #1242
      announceString = ':=> Sniff'
         #      __
         # (___()'`;   *Sniff*
         # /,    /`
         # \\"--\\      
         # Pity the chatbox does not support formatting :(
   if fetchProperty(card, 'name') == "Invasion of Privacy":
      cardList = []
      count = len(me.hand)
      iter = 0
      for c in me.hand:
         cardList.append(c)
         c.moveToTable(playerside * iter * cwidth(c) - (count * cwidth(c) / 2), 0 - yaxisMove(c), False)
         c.highlight = RevealedColor
         iter += 1
      notify("{} reveals {} from their hand. Target the cards you want to trash and press 'Del'".format(me,[c.name for c in cardList]))
      while not confirm("You have revealed your hand to your opponent. Return them to Grip?\n\n(Pressing 'No' will send a ping to your opponent to see if they're done reading them)"):
         notify("{} would like to know if it's OK to return their remaining cards to their Grip.".format(me))
      for c in cardList: 
         if c.group == table: c.moveTo(me.hand)
   if fetchProperty(card, 'name') == "Aggressive Secretary":
      programTargets = [c for c in table if c.Type == 'Program']
      debugNotify("Found {} Programs on table".format(len(programTargets)))
      if not len(programTargets): 
         notify("{} can find no programs to trash".format(card))
         return
      rc = payCost(2, 'not free')
      if rc == "ABORT": 
         notify("{} could not pay to use {}".format(me,card))
         return
      chosenProgs = multiChoice('Please choose {} programs to trash'.format(card.markers[mdict['Advancement']]), makeChoiceListfromCardList(programTargets),card)
      if chosenProgs == 'ABORT': return
      while len(chosenProgs) > card.markers[mdict['Advancement']]:
         chosenProgs = multiChoice('You chose too many programs. Please choose up to {} programs to trash'.format(card.markers[mdict['Advancement']]), makeChoiceListfromCardList(programTargets),card)
         if chosenProgs == 'ABORT': return
      for choiceProg in chosenProgs:
         prog = programTargets[choiceProg]
         intTrashCard(prog, fetchProperty(prog,'Stat'), "free", silent = True)
         notify(":> {} trashes {}".format(card,prog))
      announceString = ''
   if fetchProperty(card, 'name') == "Snoop":
      if re.search(r'-isFirstCustom',Autoscript): 
         remoteCall(findOpponent(),"Snoop",['Simply Reveal'])
         announceString = announceText + " reveal the runner's hand"
      else: 
         remoteCall(findOpponent(),"Snoop",['Reveal and Trash'])
         announceString = announceText + " reveal the runner's hand and trash a card"
   if fetchProperty(card, 'name') == "Punitive Counterstrike":
      barNotifyAll("000000","--The runner is setting how many agenda points they stole last turn.")
      count = askInteger("How many agenda points did you steal last turn?", 0)
      if count: InflictX('Inflict{}MeatDamage-onOpponent'.format(count), '', card)
      notify("--> {} is punished for their shenanigans with {} meat damage".format(me,count))
   if fetchProperty(card, 'name') == "Yagura":
      me.piles['R&D/Stack'].setVisibility('me')
      topC = me.piles['R&D/Stack'][0]
      cardDetails = makeChoiceListfromCardList([topC])[0]
      me.piles['R&D/Stack'].setVisibility('none')
      #notify("{}".format(topCard))
      notify("{} is looking at the top card in their R&D...".format(me))
      if confirm("The top card is:\n{}\n\nDo you want to send it to the bottom of your deck?".format(cardDetails)):
         topC.moveToBottom(me.piles['R&D/Stack'])
         announceString = announceText + " send the top card of their R&D to the bottom".format(me)
      else:
         announceString = announceText + " look at the top card of their R&D and leave it where it is".format(me)   
   if fetchProperty(card, 'name') == "Toshiyuki Sakai":
      handTargets = [c for c in me.hand if c.Type == 'Agenda' or c.Type == 'Asset']
      debugNotify("Found {} Assets / Agendas in hand".format(len(handTargets)))
      if not len(handTargets): 
         notify("{} can find no assets or agendas in your hand".format(card))
         return
      chosenInstall = SingleChoice('Please choose one asset/agenda from your hand with which to replace Toshiyuki Sakai', makeChoiceListfromCardList(handTargets))
      if chosenInstall == 'ABORT': return
      x,y = card.position
      handTargets[chosenInstall].moveToTable(x, y, True)
      handTargets[chosenInstall].markers[mdict['Advancement']] = card.markers[mdict['Advancement']]
      card.moveTo(me.hand)
      notify(":> {} replaces {} with a new card from their hand".format(me,card))
      announceString = ''
   return announceString
   
def CustomScript(card, action = 'PLAY', origin_card = None, original_action = None): # Scripts that are complex and fairly unique to specific cards, not worth making a whole generic function for them.
   global ModifyDraw, secretCred, collectiveSequence
   debugNotify(">>> CustomScript() with action: {}".format(action)) #Debug
   trash = me.piles['Heap/Archives(Face-up)']
   arcH = me.piles['Archives(Hidden)']
   deck = me.piles['R&D/Stack']
   #confirm("Customscript") # Debug
   if card.model == '23473bd3-f7a5-40be-8c66-7d35796b6031' and action == 'USE': # Virus Scan Special Ability
      clickCost = useClick(count = 3)
      if clickCost == 'ABORT': return 'ABORT'
      playVirusPurgeSound()
      for c in table: 
         foundMarker = findMarker(c,'Virus')
         if foundMarker: c.markers[foundMarker] = 0
      notify("{} to clean all viruses from their corporate grid".format(clickCost))
      return 'CLICK USED'
   elif card.model == '71a89203-94cd-42cd-b9a8-15377caf4437' and action == 'USE': # Technical Difficulties Special Ability
      knownMarkers = []
      for marker in card.markers:
         if marker[0] in markerRemovals: # If the name of the marker exists in the markerRemovals dictionary it means it can be removed and has a specific cost.
            knownMarkers.append(marker)
      if len(knownMarkers) == 0: 
         whisper("No known markers with ability to remove")
         return 'ABORT'
      elif len(knownMarkers) == 1: selectedMarker = knownMarkers[0]
      else: 
         selectTXT = 'Please select a marker to remove\n\n'
         iter = 0
         for choice in knownMarkers:
            selectTXT += '{}: {} ({} {} and {})\n'.format(iter,knownMarkers[iter][0],markerRemovals[choice[0]][0],uniClick(),markerRemovals[choice[0]][1])
            iter += 1
         sel = askInteger(selectTXT,0)
         selectedMarker = knownMarkers[sel]
      aCost = markerRemovals[selectedMarker[0]][0] # The first field in the tuple for the entry with the same name as the selected marker, in the markerRemovals dictionary. All clear? Good.
      cost = markerRemovals[selectedMarker[0]][1]
      clickCost = useClick(count = aCost)
      if clickCost == 'ABORT': return 'ABORT'
      creditCost = payCost(cost)
      if creditCost == 'ABORT':
         me.Clicks += aCost # If the player can't pay the cost after all and aborts, we give him his clicks back as well.
         return 'ABORT' 
      card.markers[selectedMarker] -= 1
      notify("{} to remove {} for {}.".format(clickCost,selectedMarker[0],creditCost))
      return 'CLICK USED'      
   elif fetchProperty(card, 'name') == 'Accelerated Beta Test' and action == 'SCORE':
      if not confirm("Would you like to initiate an accelerated beta test?"): return 'ABORT'
      iter = 0
      for c in deck.top(3):
         c.moveTo(arcH)
         loopChk(c,'Type')
         if c.type == 'ICE':
            placeCard(c,'InstallRezzed')
            c.orientation ^= Rot90
            iter +=1
            notify(" -- {} Beta Tested!".format(c))
            executePlayScripts(c,'REZ')
            autoscriptOtherPlayers('CardInstall',c)
            autoscriptOtherPlayers('CardRezzed',c)
      if iter: # If we found any ice in the top 3
         notify("{} initiates an Accelerated Beta Test and reveals {} Ice from the top of their R&D. These Ice are automatically installed and rezzed".format(me, iter))
      else: notify("{} initiates a Accelerated Beta Test but their beta team was incompetent.".format(me))
   elif fetchProperty(card, 'name') == 'Infiltration' and action == 'PLAY':
      tCards = [c for c in table if c.targetedBy and c.targetedBy == me and c.isFaceUp == False]
      if tCards: expose(tCards[0]) # If the player has any face-down cards currently targeted, we assume he wanted to expose them.
      elif confirm("Do you wish to gain 2 credits?\
                \n\nIf you want to expose a target, simply ask the corp to use the 'Expose' option on the table.\
                \n\nHowever if you have a target selected when you play this card, we will also announce that for you."):
         me.Credits += 2
         notify("--> {} gains {}".format(me,uniCredit(2)))
   elif fetchProperty(card, 'name') == "Rabbit Hole" and action == 'INSTALL':
      if not confirm("Would you like to extend the rabbit hole?"): 
         return 'ABORT'
      cardList = [c for c in deck]
      reduction = 0
      rabbits = 0
      totalCost = 0
      for c in cardList: c.moveTo(arcH)
      rnd(1,100)
      debugNotify("Entering rabbit search loop", 2)
      for c in cardList: 
         if c.model == "bc0f047c-01b1-427f-a439-d451eda01039":
            debugNotify("found rabbit!", 2)
            storeProperties(c)
            reduction += reduceCost(c, action, num(c.Cost)) #Checking to see if the cost is going to be reduced by cards we have in play.
            rc = payCost(num(c.Cost) - reduction, "not free")
            if rc == "ABORT": break
            else: totalCost += (num(c.Cost) - reduction)
            placeCard(c, action)
            rabbits += 1
            cardList.remove(c)
            if not confirm("Rabbit Hole extended! Would you like to dig deeper?"): break
      for c in cardList: c.moveTo(deck)
      rnd(1,10)
      shuffle(deck)
      if rabbits: # If the player managed to find and install some extra rabbit holes...
         if reduction > 0: extraText = " (reduced by {})".format(uniCredit(reduction)) #If it is, make sure to inform.    
         elif reduction < 0: extraText = " (increased by {})".format(uniCredit(abs(reduction)))
         else: extraText = ''
         me.counters['Base Link'].value += rabbits
         notify("{} has extended the Rabbit Hole by {} {} by paying {}{}".format(me,rabbits,uniLink(),uniCredit(totalCost),extraText))
      else: notify("{} does not find enough rabbits.".format(me))
   elif fetchProperty(card, 'name') == 'Snowflake' and action == 'USE':
      if secretCred == None:
         secretCred = askInteger("How many credits do you want to secretly spend?\n\nOnce you have selected your total, ask your opponent to spend their own amount visibly, then re-use this card.",0)
         while secretCred and (secretCred > me.Credits) or (secretCred > 2):
            if secretCred > me.Credits and confirm("You do not have that many credits to spend. Bypass?"): break
            if secretCred > 2: warn = ":::ERROR::: You cannot spend more than 2 credits!\n"
            else: warn = ''
            secretCred = askInteger("{}How many credits do you want to secretly spend?".format(warn),0)
         if secretCred != None: notify("{} has spent a hidden amount of credits for {}. Runner must now declare how many credits to spend".format(me,card))
      else: 
         notify("{} has spent {} in secret for {}'s subroutine".format(me,uniCredit(secretCred),card))
         me.Credits -= secretCred
         secretCred = None
   elif fetchProperty(card, 'name') == 'Bullfrog' and action == 'USE':
      choice = SingleChoice('Select Ability to use', ['Spend/Reveal 0-2 Credits','Move Bullfrog and runner to another server and continue run from there'], type = 'button')
      if choice == 0:
         if secretCred == None:
            secretCred = askInteger("How many credits do you want to secretly spend?\n\nOnce you have selected your total, ask your opponent to spend their own amount visibly, then re-use this card.",0)
            while secretCred and (secretCred > me.Credits) or (secretCred > 2):
               if secretCred > me.Credits and confirm("You do not have that many credits to spend. Bypass?"): break
               if secretCred > 2: warn = ":::ERROR::: You cannot spend more than 2 credits!\n"
               else: warn = ''
               secretCred = askInteger("{}How many credits do you want to secretly spend?".format(warn),0)
            if secretCred != None: notify("{} has spent a hidden amount of credits for {}. Runner must now declare how many credits to spend".format(me,card))
         else: 
            notify("{} has spent {} in secret for {}'s subroutine".format(me,uniCredit(secretCred),card))
            me.Credits -= secretCred
            secretCred = None
      else:
         choice = SingleChoice("Which server are you going to redirect the run at?", ['Remote Server','HQ','R&D','Archives'])
         if choice != None: # Just in case the player didn't just close the askInteger window.
            if choice == 0: targetServer = 'Remote'
            elif choice == 1: targetServer = 'HQ'
            elif choice == 2: targetServer = 'R&D'
            elif choice == 3: targetServer = 'Archives'
            else: return 'ABORT'
         else: return 'ABORT'
         setGlobalVariable('status','running{}'.format(targetServer)) # We change the global variable which holds on which server the runner is currently running on
         if targetServer == 'Remote': announceText = 'a remote server'
         else: announceText = 'the ' + targetServer
         notify("Bullfrog's Ability triggers and redirects the runner to {}.".format(announceText))
   elif fetchProperty(card, 'name') == 'Personal Workshop':
      if action == 'USE':
         targetList = [c for c in me.hand  # First we see if they've targeted a card from their hand
                        if c.targetedBy 
                        and c.targetedBy == me 
                        and num(c.Cost) > 0
                        and (c.Type == 'Program' or c.Type == 'Hardware')]
         if len(targetList) > 0:
            selectedCard = targetList[0]
            actionCost = useClick(count = 1)
            if actionCost == 'ABORT': return 'ABORT'
            hostCards = eval(getGlobalVariable('Host Cards'))
            hostCards[selectedCard._id] = card._id # We set the Personal Workshop to be the card's host
            setGlobalVariable('Host Cards',str(hostCards))
            cardAttachementsNR = len([att_id for att_id in hostCards if hostCards[att_id] == card._id])
            debugNotify("About to move into position", 2) #Debug
            storeProperties(selectedCard)
            orgAttachments(card)
            TokensX('Put1PersonalWorkshop-isSilent', "", selectedCard) # We add a Personal Workshop counter to be able to trigger the paying the cost ability
            announceText = TokensX('Put1Power-perProperty{Cost}', "{} to activate {} in order to ".format(actionCost,card), selectedCard)
            selectedCard.highlight = InactiveColor
            notify(announceText)
            return 'CLICK USED'
         else: 
            whisper(":::ERROR::: You need to target a program or hardware in your hand, with a cost of 1 or more, before using this action")  
            return 'ABORT'
      elif action == 'Start' and card.controller == me:
         hostCards = eval(getGlobalVariable('Host Cards'))
         PWcards = [Card(att_id) for att_id in hostCards if hostCards[att_id] == card._id]
         if len(PWcards) == 0: return 'ABORT'# No cards are hosted in the PW, we're doing nothing
         elif len(PWcards) == 1: selectedCard = PWcards[0] # If only one card is hosted in the PW, we remove a power from one of those.
         else: # Else we have to ask which one to remove.
            selectTXT = 'Personal Workshop: Please select one of your hosted cards from which to remove a power counter\n\n'
            iter = 0
            PWchoices = makeChoiceListfromCardList(PWcards)
            choice = SingleChoice("Choose one of the Personal Workshop hosted cards from which to remove a power counter", PWchoices, type = 'button', default = 0)
            selectedCard = PWcards[choice]
         TokensX('Remove1Power', "Personal Workshop:",selectedCard)
         notify("--> {}'s Personal Workshop removes 1 power marker from {}".format(me,selectedCard))
         if selectedCard.markers[mdict['Power']] == 0: # Empty of power markers means the card can be automatically installed
            host = chkHostType(selectedCard, seek = 'DemiAutoTargeted') 
            if host:
               try:
                  if host == 'ABORT': 
                     selectedCard.markers[mdict['Power']] += 1
                     delayed_whisper("-- Undoing Personal Workshop build")
                     return 'ABORT'
               except:
                  extraTXT = ' and hosted on {}'.format(host) # If the card requires a valid host and we found one, we will mention it later.
            else: extraTXT = ''
            clearAttachLinks(selectedCard) # We unhost it from Personal Workshop so that it's not trashed if PW is trashed
            placeCard(selectedCard, hostCard = host)
            orgAttachments(card)
            selectedCard.markers[mdict['PersonalWorkshop']] = 0
            selectedCard.highlight = None
            executePlayScripts(selectedCard,'INSTALL')
            autoscriptOtherPlayers('CardInstall',selectedCard)
            MUtext = chkRAM(selectedCard)
            notify("--> {} has been built{} from {}'s Personal Workshop{}".format(selectedCard,extraTXT,identName,MUtext))         
   elif fetchProperty(card, 'name') == 'Mr. Li' and action == 'USE':
      ClickCost = useClick(count = 1)
      if ClickCost == 'ABORT': return 'ABORT'
      StackTop = list(me.piles['R&D/Stack'].top(2))
      if len(StackTop) < 2:
         whisper("Your Stack is does not have enough cards. You cannot take this action")
         return 'ABORT'
      notify("--> {} is visiting Mr. Li...".format(me))
      for c in StackTop:
         debugNotify("Pulling cards to hand", 3) #Debug
         c.moveTo(me.hand)
         debugNotify(" Looping...", 4)
         loopChk(c)
         storeProperties(c)
      rnd(1,100) # A delay because it bugs out
      debugNotify("StackTop: {} in hand".format([c.name for c in StackTop])) #Debug
      returnChoice = SingleChoice('Select a card to put to the botton of your Stack', makeChoiceListfromCardList(StackTop, True), type = 'button', default = 0)
      StackTop[returnChoice].moveToBottom(me.piles['R&D/Stack'])
      catchwords = ["Excellent.","Don't leave town.","We'll be in touch.","We'll be seeing you soon...","Always a pleasure.","Remember our agreement.","Interesting request there."]
      goodbye = catchwords.pop(rnd(0, len(catchwords) - 1))
      notify('{} to have {} procure 1 card.\n- "{}"'.format(ClickCost,card,goodbye))
      return 'CLICK USED'
   elif fetchProperty(card, 'name') == "Indexing" and action == 'SuccessfulRun':
      targetPL = findOpponent()
      addGroupVisibility(targetPL.piles['R&D/Stack'],me) # Workaround for OCTGN bug #1242
      debugNotify("Taking R&D Control")
      grabPileControl(targetPL.piles['R&D/Stack'])
      if len(targetPL.piles['R&D/Stack']) < 5: count = len(targetPL.piles['R&D/Stack'])
      else: count = 5
      cardList = list(targetPL.piles['R&D/Stack'].top(count)) # We make a list of the top 5 cards the runner can look at.
      debugNotify("Taking R&D Visibility")
      targetPL.piles['R&D/Stack'].addViewer(me)
      if len(cardList): loopChk(cardList[len(cardList) - 1])
      idx = 0 # The index where we're going to be placing each card.
      while len(cardList) > 0:
         if len(cardList) == 1: choice = 0
         else: choice = SingleChoice("Choose card put on the {} position of the Stack".format(numOrder(idx)), makeChoiceListfromCardList(cardList), cancelButton = False, type = 'button')
         movedC = cardList.pop(choice)
         movedC.moveTo(targetPL.piles['R&D/Stack'],idx) # If there's only one card left, we put it in the last available index location in the Stack. 
         idx += 1
      notify("{} has successfully indexed {}'s R&D".format(me,targetPL))
      targetPL.piles['R&D/Stack'].removeViewer(me)
      passPileControl(targetPL.piles['R&D/Stack'],targetPL)
      delGroupVisibility(targetPL.piles['R&D/Stack'],me) # Workaround for OCTGN bug #1242
   elif fetchProperty(card, 'name') == "Deep Thought" and action == 'Start':
      if card.markers[mdict['Virus']] and card.markers[mdict['Virus']] >= 3:
         targetPL = findOpponent()
         debugNotify("Moving Corp's Top card to our Scripting Pile", 2)
         cardView = targetPL.piles['R&D/Stack'].top()
         cardView.moveTo(me.ScriptingPile)
         rnd(1,10)
         notify(":> Deep Thought has revealed the top card of R&D to {}".format(me))
         delayed_whisper(":> Deep Thought: {} is upcoming! Ommm...".format(cardView))
         rnd(1,10)
         cardView.moveTo(targetPL.piles['R&D/Stack'])
   elif fetchProperty(card, 'name') == "Midori" and action == 'USE':
      targetCards = findTarget('Targeted-atICE-isMutedTarget')
      if not len(targetCards):
         delayed_whisper(":::ERROR::: You need to target an installed to use this ability")
         return 'ABORT'
      tableICE = targetCards[0]
      targetCards = findTarget('Targeted-atICE-fromHand-isMutedTarget')
      if not len(targetCards):
         delayed_whisper(":::ERROR::: You need to also target an ICE in your hand to use this ability")
         return 'ABORT'
      if oncePerTurn(card) == 'ABORT': return 'ABORT'
      handICE = targetCards[0]
      storeProperties(handICE)
      x,y = tableICE.position
      handICE.moveToTable(x,y,True)
      handICE.orientation = Rot90
      tableICE.moveTo(me.hand)
      autoscriptOtherPlayers('CardInstall',handICE)
      notify('{} activates Midori to replace the approached {}, with an ICE from the HQ.'.format(me,tableICE.name))
      notify('- "Naughty Naughty..."')
   elif fetchProperty(card, 'name') == "Director Haas' Pet Project" and action == 'SCORE':
      debugNotify("about to implement Director Haas' Pet Project")
      # First we need to gather all the valid cards from hand or archives.
      installableCards = []
      for c in me.hand:
         if c.Type != 'Operation': installableCards.append(c)
      for c in me.piles['Heap/Archives(Face-up)']:
         if c.Type != 'Operation': installableCards.append(c)
      for c in me.piles['Archives(Hidden)']:
         if c.Type != 'Operation': installableCards.append(c)
      debugNotify("Finished creating installableCards[]")
      if len(installableCards) == 0:
         notify("Director Haas cannot find any cards to use for their pet project :(")
         return 'ABORT'
      if not confirm("Would you like to initiate Director Haass' Pet Project?"): return 'ABORT'
      cardChoices = []
      cardTexts = []
      chosenCList = []
      for iter in range(3):
         debugNotify("len(installableCards) = {}".format(len(installableCards)))
         debugNotify("installableCards: {}".format([rootC.name for rootC in installableCards]), 4)
         debugNotify("iter: {}/{}".format(iter,3), 4)
         del cardChoices[:]
         del cardTexts[:]
         for c in installableCards:
            if c.Rules not in cardTexts: # we don't want to provide the player with a the same card as a choice twice.
               debugNotify("Appending card", 4)
               cardChoices.append(c)
               cardTexts.append(c.Rules)
         choice = SingleChoice("Choose {} card to install in the pet project".format(numOrder(iter)), makeChoiceListfromCardList(cardChoices, includeGroup = True), [], 'Cancel')
         debugNotify("choice = {}".format(choice))
         if choice == None: break
         chosenCList.append(cardChoices[choice])
         installableCards.remove(cardChoices[choice])
         if cardChoices[choice].Type == 'Asset' or cardChoices[choice].Type == 'Agenda': # If we install an asset or agenda, we can't install any more of those so we remove them from the choice list.
            for rootC in installableCards:
               if rootC.Type == 'Asset' or rootC.Type == 'Agenda': 
                  debugNotify("{} Type = {}. Removing".format(rootC,rootC.Type))
                  installableCards.remove(rootC) 
               else:
                  debugNotify("{} Type = {}. Keeping".format(rootC,rootC.Type))            
         if len(installableCards) < 2 - iter: break
      if len(chosenCList) > 0: # If it's 0, it means the player changed their mind and pressed cancel on the first choice.
         debugNotify("chosenCList = {}".format([c.name for c in chosenCList]))
         debugNotify("About to create the new remote")
         Server = table.create("d59fc50c-c727-4b69-83eb-36c475d60dcb", 0, 0 - (40 * playerside), 1, False)
         placeCard(Server,'INSTALL')
         x,y = Server.position
         serverRoot = 0
         serverICE = 0
         debugNotify("About the place the cards in the new remote")
         for c in chosenCList:
            storeProperties(c)
            if c.Type == 'ICE':
               c.moveToTable(x - (10 * flipBoard), (120 * flipBoard) + flipModY - (70 * serverICE * playerside),True)
               c.orientation = Rot90
               serverICE += 1
            else:
               c.moveToTable(x - (serverRoot * 30 * flipBoard), (255 * flipBoard) + flipModY,True)
               serverRoot += 1
            debugNotify("Peeking() at Director Haas' Pet Project")
            c.peek()
            autoscriptOtherPlayers('CardInstall',c)
         notify("{} implements {} and installs {} ICE and {} cards in the server root".format(me,card,serverICE,serverRoot))
   elif fetchProperty(card, 'name') == "Howler" and action == 'USE':
      debugNotify("about to Howl!")
      # First we need to gather all the valid cards from hand or archives.
      installableCards = []
      for c in me.hand:
         if c.Type == 'ICE' and re.search('Bioroid',getKeywords(c)): installableCards.append(c)
      for c in me.piles['Heap/Archives(Face-up)']:
         if c.Type == 'ICE' and re.search('Bioroid',getKeywords(c)): installableCards.append(c)
      for c in me.piles['Archives(Hidden)']:
         if c.Type == 'ICE' and re.search('Bioroid',getKeywords(c)): installableCards.append(c)
      debugNotify("Finished creating installableCards[]")
      if len(installableCards) == 0:
         notify("Howler has no valid targets to shout for >_<")
         return 'ABORT'
      debugNotify("len(installableCards) = {}".format(len(installableCards)))
      debugNotify("installableCards: {}".format([rootC.name for rootC in installableCards]), 4)
      choice = SingleChoice("WAAAaaAAaa! Choose a Bioroid ICE to awaken!", makeChoiceListfromCardList(installableCards, includeGroup = True), [], 'Cancel')
      debugNotify("choice = {}".format(choice))
      if choice == None: return 'ABORT'
      chosenC = installableCards[choice]
      previousGroup = pileName(chosenC.group)
      debugNotify("chosenC = {}".format(chosenC))
      storeProperties(chosenC)
      debugNotify("About to move ICE behind the Howler")
      x,y = card.position
      chosenC.moveToTable(x, y + (40 * flipBoard))
      chosenC.orientation = Rot90
      TokensX('Put1Howler-isSilent', "", card, [chosenC,card])
      notify("{} wueaaAAAA! {} has awakened a {} from {} for the defense of this server!".format(uniSubroutine(),card,chosenC,previousGroup))
      autoscriptOtherPlayers('CardInstall',chosenC)
      autoscriptOtherPlayers('CardRezzed',chosenC)
   elif fetchProperty(card, 'name') == 'Awakening Center' and action == 'USE':
      targetList = [c for c in me.hand  # First we see if they've targeted a card from their hand
                     if c.targetedBy 
                     and c.targetedBy == me 
                     and c.Type == 'ICE'
                     and re.search('Bioroid',getKeywords(c))]
      if len(targetList) > 0:
         selectedCard = targetList[0]
         actionCost = useClick(count = 1)
         if actionCost == 'ABORT': return 'ABORT'
         hostCards = eval(getGlobalVariable('Host Cards'))
         hostCards[selectedCard._id] = card._id # We set the Awakening Center to be the card's host
         setGlobalVariable('Host Cards',str(hostCards))
         cardAttachementsNR = len([att_id for att_id in hostCards if hostCards[att_id] == card._id])
         debugNotify("About to move into position", 2) #Debug
         storeProperties(selectedCard)
         orgAttachments(card)
         TokensX('Put1Awakening Center-isSilent', "", selectedCard) # We add an Awakening Center counter to be able to trigger the rez the ice ability
         selectedCard.highlight = InactiveColor
         notify("{} has installed a Bioroid ICE in their {}".format(me,card))
         autoscriptOtherPlayers('CardInstall',selectedCard)
         return 'CLICK USED'
      else: 
         whisper(":::ERROR::: You need to target a Bioroid ICE in your HQ before using this action")  
         return 'ABORT'
   elif fetchProperty(card, 'name') == 'Escher':
      tableICE = [c for c in table if fetchProperty(c, 'Type') == 'ICE' or (not c.isFaceUp and c.orientation == Rot90)]
      if action == 'SuccessfulRun':
         for c in tableICE: c.setController(me)
         TokensX('Put1Escher-isSilent', "", card, tableICE)
         notify("{} uses non-euclidian hacks to re-organize the corporation's ICE.".format(Identity))
         delayed_whisper(":::INFO::: All ICE control has been passed to you. Jack Out to pass control back to the corporation player.")
      if action == 'JackOut':
         for c in tableICE: c.setController(findOpponent())
         TokensX('Remove1Escher-isSilent', "", card, tableICE)
         card.moveTo(card.owner.piles['Heap/Archives(Face-up)'])
   elif fetchProperty(card, 'name') == 'Scavenge' and action == 'PLAY':
      targetPrograms = findTarget('Targeted-atProgram')
      if len(targetPrograms) == 0: return 'ABORT'
      else: trashProgram = targetPrograms[0]
      intTrashCard(trashProgram, fetchProperty(trashProgram,'Stat'), "free", silent = True) # We trash it immediately as it can be picked up by scavenge itself.
      gripTargets = findTarget('Targeted-atProgram-fromHand-isMutedTarget') # First we check if the player has targeted a program from their grip as well, this way we don't have to ask.
      if len(gripTargets) > 0: 
         debugNotify("Found Hand Card Targeted group = {}".format([c.name for c in gripTargets]))
         newProgram = gripTargets[0] #If they've targeted more than one, they shouldn't have. We just select the first.
         targetPile = 'Grip'
      else:
         debugNotify("Didn't find hand card targeted")
         gripProgsNR = len([c for c in me.hand if c.Type == 'Program'])
         heapProgsNR = len([c for c in me.piles['Heap/Archives(Face-up)'] if c.Type == 'Program'])
         debugNotify("gripProgsNR = {}, heapProgsNR = {}".format(gripProgsNR,heapProgsNR))
         if gripProgsNR == 0 and heapProgsNR == 0:
            notify("{} wanted to scavenge but forgot they don't have any programs in their grip and heap")
            return 'ABORT'
         elif gripProgsNR == 0: targetPile = 'Heap'
         elif heapProgsNR == 0: targetPile = 'Grip'
         else:
            if confirm("Do you want to install the program from your heap?"):
               targetPile = 'Heap'
            else:
               targetPile = 'Grip'
         if targetPile == 'Heap':
            debugNotify("Retrieving from {}".format(targetPile))
            retrieveTuple = RetrieveX('Retrieve1Card-fromHeap-grabProgram', '', card)
            debugNotify("retrieveTuple = {}".format(retrieveTuple))
            if len(retrieveTuple[1]) == 0: 
               notify("{} scavenged their heap but couldn't find a program to install.".format(me))
               return 'ABORT'
            newProgram = retrieveTuple[1][0]
            pile = me.piles['Heap/Archives(Face-up)']
         else:
            debugNotify("Retrieving from {}".format(targetPile))
            gripTargets = findTarget('AutoTargeted-atProgram-fromHand')
            debugNotify("About to SingleChoice")
            newProgram = gripTargets[SingleChoice("Choose a program to scavenge from your grip", makeChoiceListfromCardList(gripTargets))]
            pile = me.hand
      cardCost = num(fetchProperty(newProgram, 'Cost')) - num(trashProgram.Cost)
      if cardCost < 0: cardCost = 0
      reduction = reduceCost(newProgram, 'INSTALL', cardCost, dryRun = True)
      rc = payCost(cardCost - reduction, "not free")
      if rc == 'ABORT': return 'ABORT' # If the cost couldn't be paid, we don't proceed.
      reduceCost(newProgram, 'INSTALL', cardCost) # If the cost could be paid, we finally take the credits out from cost reducing cards.
      if reduction: reduceTXT = ' (reduced by {})'.format(reduction)
      else: reduceTXT = ''
      placeCard(newProgram)
      debugNotify("Executing newProgram triggers")
      executePlayScripts(newProgram,'INSTALL')
      autoscriptOtherPlayers('CardInstall',newProgram)
      debugNotify("About to announce")
      notify("{} has trashed {} and {}d through their {} finding and installing {} for {}{}.".format(me,trashProgram,card,targetPile,newProgram,uniCredit(cardCost),reduceTXT))
   elif fetchProperty(card, 'name') == 'Same Old Thing' and action == 'USE':
      ClickCost = useClick(count = 2)
      if ClickCost == 'ABORT': return  #If the player didn't have enough clicks and opted not to proceed, do nothing.
      retrieveTuple = RetrieveX('Retrieve1Card-fromHeap-grabEvent', '', card)
      debugNotify("retrieveTuple = {}".format(retrieveTuple))
      if len(retrieveTuple[1]) == 0: 
         notify("{} tried to do the same old thing but they never did a thing in their life!".format(me))
         return 'ABORT'
      sameOldThing = retrieveTuple[1][0]
      notify("{} does the same old {}".format(me,sameOldThing))
      intPlay(sameOldThing,scripted = True)
      intTrashCard(card, fetchProperty(sameOldThing,'Stat'), "free", silent = True)
      return 'CLICK USED'
   elif fetchProperty(card, 'name') == "Motivation" and action == 'Start':
      targetPL = me
      debugNotify("Moving Top card to our Scripting Pile", 2)
      cardView = targetPL.piles['R&D/Stack'].top()
      cardView.moveTo(me.ScriptingPile)
      rnd(1,10)
      notify(":> Motivation has revealed the top card of their Stack to {}".format(me))
      delayed_whisper(":> Motivation: {} is next! Go get 'em!".format(cardView))
      rnd(1,10)
      cardView.moveTo(targetPL.piles['R&D/Stack'])
   elif fetchProperty(card, 'name') == 'Celebrity Gift' and action == 'PLAY':
      revealedCards = findTarget('Targeted-fromHand')
      del revealedCards[5:] # We don't want it to be more than 5 cards
      if len(revealedCards) == 0: 
         delayed_whisper("You need to gift something to the celebrities first you cheapskate!")
         return 'ABORT'
      iter = 0
      for c in revealedCards:
         c.moveToTable(playerside * iter * cwidth(c) - (len(revealedCards) * cwidth(c) / 2), 0 - yaxisMove(c), False)
         c.highlight = RevealedColor
         iter += 1
      notify("{} reveals {} as their celebrity gift and gains {}".format(me,[c.name for c in revealedCards],uniCredit(len(revealedCards) * 2)))
      while not confirm("You have revealed your celebrity gifts to your opponent. Return them to HQ?\n\n(Pressing 'No' will send a ping to your opponent to see if they're done reading them)"):
         notify("{} would like to know if it's OK to return their celebrity gifts to their HQ.".format(me))
      for c in revealedCards: c.moveTo(me.hand)
      me.Credits += len(revealedCards) * 2
   elif fetchProperty(card, 'name') == 'The Collective':
      if action == 'USE' or action == 'Run':
         debugNotify("Current collectiveSequence = {}".format(collectiveSequence),3)
         debugNotify("origin_card = {}. original_action = {}".format(origin_card.name,original_action),3)
         if not len(collectiveSequence):
            debugNotify("Empty collectiveSequence List")
            collectiveSequence.extend([original_action,1,origin_card.name])
         elif collectiveSequence[0] == original_action:
            debugNotify("Matched original_action")
            if original_action == 'CardAction' and collectiveSequence[2] != origin_card.name:
               debugNotify("{} and no match of {} with {}".format(action,collectiveSequence[2],origin_card.name),3)
               del collectiveSequence[:]
               collectiveSequence.extend([original_action,1,origin_card.name])
            else: 
               debugNotify("{} and matched {} with {}".format(action,collectiveSequence[2],origin_card.name),3)
               collectiveSequence[1] += 1
         else:
            debugNotify("No match on original_action")
            del collectiveSequence[:]
            collectiveSequence.extend([original_action,1,origin_card.name])
         if collectiveSequence[1] == 3:
            if oncePerTurn(card) == 'ABORT': return 'ABORT'
            else: 
               me.Clicks += 1
               notify(":> {} has streamlined their processes and gained 1 extra {}.".format(card,uniClick()))
      elif action == 'Start': del collectiveSequence[:]
      debugNotify("Exiting with collectiveSequence = {}".format(collectiveSequence))
   elif fetchProperty(card, 'name') == 'Copycat' and action == 'USE':
      runTargetRegex = re.search(r'running([A-Za-z&]+)',getGlobalVariable('status'))
      if not runTargetRegex: 
         whisper(":::ERROR::: You need to be currently running to use Copycat!")
         return 'ABORT'
      choice = SingleChoice("Which server are you continuing the run from?",['Remote Server','HQ','R&D','Archives'])
      if choice != None: # Just in case the player didn't just close the askInteger window.
         if choice == 0: Name = 'Remote'
         elif choice == 1: Name = 'HQ'
         elif choice == 2: Name = 'R&D'
         elif choice == 3: Name = 'Archives'
         else: return 'ABORT'
      myIdent = getSpecial('Identity',me)
      myIdent.target(False)
      if Name != 'Remote':
         enemyIdent = getSpecial('Identity',findOpponent())
         targetServer = getSpecial(Name,enemyIdent.controller)
         if targetServer: myIdent.arrow(targetServer, True) # If for some reason we can't find the relevant central server card (e.g. during debug), we abort gracefully
      setGlobalVariable('status','running{}'.format(Name))
      notify("{} trashes {} to switch runs to the {} server".format(me,card,Name))
      intTrashCard(card, fetchProperty(card,'Stat'), "free", silent = True)
   elif fetchProperty(card, 'name') == 'Eureka!' and action == 'PLAY':
      c = me.piles['R&D/Stack'].top()
      c.moveTo(me.piles['Heap/Archives(Face-up)'])
      rnd(0,5)
      if c.Type != 'Event':
         extraCost = num(c.Cost) - 10
         if extraCost < 0: extraCost = 0
         reduction = reduceCost(c, 'TRASH', extraCost, dryRun = True)
         if reduction > 0:
            extraText = " ({} - {})".format(extraCost,reduction)
            extraText2 = " (reduced by {})".format(uniCredit(reduction))
         elif reduction < 0:
            extraText = " ({} + {})".format(extraCost,abs(reduction))
            extraText2 = " (increased by {})".format(uniCredit(reduction))
         else:
            extraText = ''
            extraText2 = ''
         if confirm("The top card of your Stack is {}. It will cost you {}{} to install and you have {} credits. Install?".format(c.Name,extraCost - reduction,extraText,me.Credits)):
            intPlay(c, 'not free', True, 10)
         else: notify("{} almost had a breakthrough while working on {}, but didn't have the funds or willpower to follow through.".format(me,c))
      else: notify("{} went for a random breakthrough, but only remembered they should have {}'d instead.".format(me,c))
   elif fetchProperty(card, 'name') == 'Expert Schedule Analyzer' and action == 'SuccessfulRun':
      remoteCall(findOpponent(),"ESA",[])
   elif fetchProperty(card, 'name') == "Woman in the Red Dress" and action == 'Start':
      remoteCall(findOpponent(),"WitRD",[])
   elif fetchProperty(card, 'name') == 'Accelerated Diagnostics' and action == 'PLAY':
      if len(me.piles['R&D/Stack']) < 3: count = len(me.piles['R&D/Stack'])
      else: count = 3
      cardList = []
      trashedList = []
      debugNotify("Moving all cards to the scripting pile")
      for c in me.piles['R&D/Stack'].top(count): 
         c.moveTo(me.ScriptingPile)
         if fetchProperty(c, 'Type') != 'Operation': # We move all cards in execution limbo (see http://boardgamegeek.com/thread/1086167/double-accelerated-diagnostics)
            debugNotify("Appending to trashedList")
            trashedList.append(c)
         else: 
            debugNotify("Appending to cardList")
            cardList.append(c)
      debugNotify("Finished checing Types")
      if len(cardList) == 0: notify("{} initiated an Accelerated Diagnostics but their beta team was incompetent".format(me))
      else:
         debugNotify("Starting to play operations")
         opsNr = len(cardList)
         for iter in range(opsNr):
            choice = SingleChoice("Choose {} diagnostic to run".format(numOrder(iter)), makeChoiceListfromCardList(cardList,True), cancelName = 'Done')
            if choice == None: break
            intPlay(cardList[choice], 'not free', True)
            debugNotify("Card Played, trashing it")
            cardList[choice].moveTo(me.piles['Heap/Archives(Face-up)'])
            cardList.remove(cardList[choice])
         notify("{} initiated an {} for {} operations and trashed {} other cards".format(me,card,3 - len(cardList) - len(trashedList), len(cardList) + len(trashedList)))
      for c in trashedList: c.moveTo(me.piles['Archives(Hidden)']) 
      for c in cardList: c.moveTo(me.piles['Archives(Hidden)'])
   elif fetchProperty(card, 'name') == "City Surveillance" and action == 'Start': # We don't need a remote call, since it's going to be the runner pressing F1 anyway in this case.
      reduction = reduceCost(card, 'Force', 1, dryRun = True)
      if reduction > 0: extraText = " (reduced by {})".format(uniCredit(reduction)) #If it is, make sure to inform.
      elif reduction < 0: extraText = " (increased by {})".format(uniCredit(abs(reduction)))
      else: extraText = ''
      if me.Credits >= 1 - reduction and confirm("City Surveilance: Pay 1 Credit?"): 
         payCost(1 - reduction, 'not free')
         reduction = reduceCost(card, 'Force', 1)
         notify(":> {} paid {} {} to avoid the {} tag".format(me,1 - reduction, extraText, card))
      else: 
         me.Tags += 1
         notify(":> {} has been caught on {} and received 1 tag".format(me,card))
   elif fetchProperty(card, 'name') == 'Power Shutdown' and action == 'PLAY':
      count = askInteger("Trash How many cards from R&D (max {})".format(len(me.piles['R&D/Stack'])),0)
      if count > len(me.piles['R&D/Stack']): count = len(me.piles['R&D/Stack'])
      for c in me.piles['R&D/Stack'].top(count): c.moveTo(me.piles['Archives(Hidden)'])
      notify("{} has initiated a power shutdown and trashed {} cards. The runner must trash 1 installed program or hardware with an install cost of {} or less".format(me,count,count))
   elif fetchProperty(card, 'name') == 'Keyhole' and action == 'SuccessfulRun':
      targetPL = findOpponent()
      grabPileControl(targetPL.piles['R&D/Stack'])
      grabPileControl(targetPL.piles['Heap/Archives(Face-up)'])
      if len(targetPL.piles['R&D/Stack']) < 3: count = len(targetPL.piles['R&D/Stack'])
      else: count = 3
      cardList = list(targetPL.piles['R&D/Stack'].top(count)) # We make a list of the top 3 cards the runner can look at.
      debugNotify("Peeking at Corp's Stack.", 2)
      for c in targetPL.piles['R&D/Stack']: c.peek()
      update() # Delay to be able to read card info
      rnd(1,100) # More delay because apparently it wasn't enough.
      choice = SingleChoice("Choose a card to trash", makeChoiceListfromCardList(cardList, True), type = 'button')
      trashedC = cardList[choice]
      sendToTrash(trashedC)
      debugNotify("Shuffling Pile")
      shuffle(targetPL.piles['R&D/Stack'])
      notify("{} has peeked through the {} at R&D and trashed {}".format(me,card,trashedC))
      passPileControl(targetPL.piles['R&D/Stack'],targetPL)
      passPileControl(targetPL.piles['Heap/Archives(Face-up)'],targetPL)
   elif fetchProperty(card, 'name') == 'Leverage' and action == 'PLAY':
      remoteCall(findOpponent(),"Leverage",[card])
   elif fetchProperty(card, 'name') == 'Capstone' and action == 'USE':
      trashTargets = findTarget('Targeted-fromHand')
      if len(trashTargets) == 0: whisper("Capstone cannot function without at least some juice!")
      else:
         actionCost = useClick(count = 1)
         if actionCost == 'ABORT': return 'ABORT'
         count = 0
         for c in trashTargets:
            foundDuplicate = False
            for seek in table:
               if c.name == seek.name: foundDuplicate = True
            if foundDuplicate: count += 1
            c.moveTo(me.piles['Heap/Archives(Face-up)'])
         drawMany(me.piles['R&D/Stack'], count, silent = False)
         notify("{} to activate {} in order to trash {} from their hand and draw {} new cards".format(actionCost,card,[c.name for c in trashTargets],count))
         return 'CLICK USED'
   elif fetchProperty(card, 'name') == 'Rex Campaign' and action == 'Start':
      debugNotify("Checking Rex Campaign")
      if not card.markers[mdict['Power']]:
         if confirm("Your Rex Campaign has concluded. Do you want to gain 5 credits?\
                 \n\n(Pressing 'No' will remove 1 Bad Publicity instead)"):
            me.Credits += 5
            notify("--> The Rex Campaign concludes and provides {} with {}".format(me,uniCredit(5)))
         else:
            me.counters['Bad Publicity'].value -= 1
            notify("=> The Rex Campaign concludes and reduces {}'s Bad Publicity by 1".format(me))     
         sendToTrash(card)
   elif fetchProperty(card, 'name') == 'Sweeps Week' and action == 'PLAY':
      targetPL = findOpponent()
      me.Credits += len(targetPL.hand)
      notify("--> {} uses {}'s ability to gain {}".format(me,card,uniCredit(len(targetPL.hand))))
   elif fetchProperty(card, 'name') == 'Precognition' and action == 'PLAY':
      notify("{} foresees the future...".format(me))
      me.piles['R&D/Stack'].lookAt(5)
   elif fetchProperty(card, 'name') == 'Quest Completed' and action == 'PLAY':
      accessC = findTarget('Targeted-targetOpponents')
      if len(accessC): accessTarget(accessC[0], noQuestionsAsked = True)
      else: whisper("You need to target an card to access before playing this event")      
   elif action == 'USE': useCard(card)
   if fetchProperty(card, 'name') == "Executive Wiretaps" and action == 'PLAY':
      remoteCall(findOpponent(),"ExecWire",[])
   debugNotify("<<< CustomScript()", 3) #Debug
   
def markerEffects(Time = 'Start'):
   mute()
   debugNotify(">>> markerEffects() at time: {}".format(Time)) #Debug
   ### Checking triggers from markers the rest of our cards.
   cardList = [c for c in table if c.markers]
   for card in cardList:
      for marker in card.markers:
         if re.search(r'Tinkering',marker[0]) and Time == 'End':
            TokensX('Remove1Keyword:Code Gate-isSilent', "Tinkering:", card)
            TokensX('Remove1Keyword:Sentry-isSilent', "Tinkering:", card)
            TokensX('Remove1Keyword:Barrier-isSilent', "Tinkering:", card)
            TokensX('Remove1Tinkering', "Tinkering:", card)
            notify("--> {} removes tinkering effect from {}".format(me,card))
         if re.search(r'Cortez Chip',marker[0]) and Time == 'End':
            TokensX('Remove1Cortez Chip-isSilent', "Cortez Chip:", card)
            notify("--> {} removes Cortez Chip effect from {}".format(me,card))
         if re.search(r'Joshua Enhancement',marker[0]) and Time == 'End': # We put Joshua's effect here, in case the runner trashes the card with Aesop's after using it
            TokensX('Remove1Joshua Enhancement-isSilent', "Joshua Enhancement:", card)
            GainX('Gain1Tags', "Joshua's Enhancements:".format(me), card)
            notify("--> Joshua's Enhancements give {} a tag".format(identName))
         if re.search(r'Test Run',marker[0]) and Time == 'End': # We put Test Run's effect here, as the card will be discarded after being played.
            notify("--> The Test Run {} is returned to {}'s stack".format(card,identName))
            rnd(1,10)
            ModifyStatus('UninstallMyself-toStack', 'Test Run:', card)
         if re.search(r'Deep Red',marker[0]) and Time == 'End': # We silently remove deep red effects
            TokensX('Remove1Deep Red-isSilent', "Deep Red:", card)
         if re.search(r'LLDS Processor',marker[0]) and Time == 'End': # We silently remove LLDS Processor bonus
            TokensX('Remove1LLDS Processor-isSilent', "LLDS Processor:", card)

def ASVarEffects(Time = 'Start'):
   mute()
   debugNotify(">>> ASVarEffects() at time: {}".format(Time)) #Debug
   ### Checking triggers from AutoScript Variables
   ASVars = eval(getGlobalVariable('AutoScript Variables'))
   if Time == 'Start': ASVars['Subliminal'] = 'False' # At the very start of each turn, we set the Subliminal var to False to signify no Subliminal has been played yet.
   setGlobalVariable('AutoScript Variables',str(ASVars))

def CustomEffects(Time = 'Start'):
   mute()
   debugNotify(">>> CustomEffects() at time: {}".format(Time)) #Debug
   ### Checking for specific effects that require special card awareness.
   #AwarenessList = eval(me.getGlobalVariable('Awareness'))
   if Time == 'Start': #and 'Subliminal Messaging' in AwarenessList: 
      count = sum(1 for card in me.piles['Heap/Archives(Face-up)'] if card.name == 'Subliminal Messaging')
      count += sum(1 for card in me.piles['Archives(Hidden)'] if card.name == 'Subliminal Messaging')
      if count and getGlobalVariable('Central Run') == 'False' and getGlobalVariable('Remote Run') == 'False':
         choice = 4
         while count < choice: 
            choice = askInteger("How much Subliminal Messaging do you want to take back into your HQ (Max {})?\
                             \n\n(We'll start taking from Face-Up Archives)".format(count), 1)
         grabbed = 0
         if grabbed < choice:
            for card in me.piles['Heap/Archives(Face-up)']:      
               if card.name == 'Subliminal Messaging': 
                  grabbed += 1
                  card.moveTo(me.hand)
                  notify(":> {} takes one Subliminal Messaging from Face-Up Archives to their HQ".format(me))
               if grabbed == choice: break
         if grabbed < choice:
            for card in me.piles['Archives(Hidden)']:
               if card.name == 'Subliminal Messaging': 
                  grabbed += 1
                  card.moveTo(me.hand)
                  notify(":> {} takes one Subliminal Messaging from Hidden Archives to their HQ".format(me))
               if grabbed == choice: break

def markerScripts(card, action = 'USE'):
   debugNotify(">>> markerScripts() with action: {}".format(action)) #Debug
   foundSpecial = False
   for key in card.markers:
      if key[0] == 'Personal Workshop' and action == 'USE':
         foundSpecial = True
         count = askInteger("{} has {} power counters left.\nHow many do you want to pay to remove?".format(card.name,card.markers[mdict['Power']]),card.markers[mdict['Power']])
         if not count: return foundSpecial
         if count > card.markers[mdict['Power']]: count = card.markers[mdict['Power']]
         host = chkHostType(card) 
         if host:
            try:
               if count == card.markers[mdict['Power']] and host == 'ABORT': 
                  delayed_whisper("-- Undoing Personal Workshop build")
                  return foundSpecial
            except: extraTXT = ' on {}'.format(host) # If the card requires a valid host and we found one, we will mention it later.
         else: extraTXT = ''
         hostCards = eval(getGlobalVariable('Host Cards'))
         hostCard = Card(hostCards[card._id])
         reduction = reduceCost(hostCard, 'USE', count, dryRun = True)
         rc = payCost(count - reduction, "not free")
         if rc == 'ABORT': return foundSpecial # If the cost couldn't be paid, we don't proceed.
         reduceCost(hostCard, 'USE', count) # If the cost could be paid, we finally take the credits out from cost reducing cards.
         card.markers[mdict['Power']] -= count
         if reduction: reduceTXT = ' (reduced by {})'.format(reduction)
         else: reduceTXT = ''
         if card.markers[mdict['Power']] == 0: 
            clearAttachLinks(card) # We unhost it from Personal Workshop so that it's not trashed if PW is trashed
            placeCard(card)
            orgAttachments(hostCard)
            card.markers[mdict['PersonalWorkshop']] = 0
            card.highlight = None
            executePlayScripts(card,'INSTALL')
            autoscriptOtherPlayers('CardInstall',card)
            MUtext = chkRAM(card)
            notify("{} has paid {}{} in order to install {}{} from their Personal Workshop{}".format(me,uniCredit(count),reduceTXT,card,extraTXT,MUtext))
         else:
            notify("{} has paid {}{} to remove {} power counters from {} in their Personal Workshop".format(me,uniCredit(count),reduceTXT,count,card))         
      if key[0] == 'Awakening Center' and action == 'USE' and not card.isFaceUp:
         foundSpecial = True
         host = chkHostType(card) 
         hostCards = eval(getGlobalVariable('Host Cards'))
         hostCard = Card(hostCards[card._id])
         cardCost = num(fetchProperty(card, 'Cost')) - 7
         if cardCost < 0: cardCost = 0
         reduction = reduceCost(card, 'REZ', cardCost, dryRun = True)
         rc = payCost(cardCost - reduction, "not free")
         if rc == 'ABORT': return foundSpecial # If the cost couldn't be paid, we don't proceed.
         reduceCost(card, 'REZ', cardCost) # If the cost could be paid, we finally take the credits out from cost reducing cards.
         if reduction: reduceTXT = ' (reduced by {})'.format(reduction)
         else: reduceTXT = ''
         #card.markers[mdict['AwakeningCenter']] = 0
         card.highlight = None
         intRez(card,cost = 'free',silent = True)
         notify("{} has paid {}{} in order to rez {} from their {}.".format(me,uniCredit(cardCost),reduceTXT,card,hostCard))
      if key[0] == 'Escher' and action == 'USE': 
         global EscherUse
         foundSpecial = True
         if ds == 'corp': 
            whisper("Our ICE shouldn't have Escher tokens! Cleaning")
            tableICE = [c for c in table if fetchProperty(c, 'Type') == 'ICE' or (not c.isFaceUp and c.orientation == Rot90)]
            TokensX('Remove1Escher-isSilent', "", card, tableICE)
         else:
            EscherUse +=1
            if EscherUse == 1: whisper(":::ERROR::: Runners are not allowed to rez Escher ICE")
            elif EscherUse == 2: whisper("Bweep! Please don't touch that!")
            elif EscherUse == 3: whisper("Bweep! Bweep! Intruder Alert!")
            elif EscherUse == 4: whisper("Please stay where you are. Our helpful assistants will be right with you.")
            elif EscherUse == 5: whisper("Please remain calm. Assistance is on the way.")
            elif EscherUse == 6: whisper("Please remain calm...")
            elif EscherUse == 7: whisper("Remain calm...")
            elif EscherUse == 8: whisper("Suddenly it is pitch black!")
            elif EscherUse == 9: whisper("It is pitch black! You feel that you should really consider jacking out any time now...")
            elif EscherUse == 10: whisper("You are likely to be eaten by a Grue...")
            elif EscherUse == 11: 
               if confirm("Fine! A Grue 1.0 is rezzed! Run away?"):
                  me.Clicks = 0
                  jackOut()
                  notify("{} has encountered a Grue and run away. They lose the rest of their turn for wasting so much time.".format(me))
               else:
                  delayed_whisper(":> You FOOL!")
                  notify("{} was looking for trouble in the dark and has been eaten by a Grue. {} has flatlined".format(me,me))
                  for i in range(6): applyBrainDmg()
                  jackOut()
            else: EscherUse = 0
      if key[0] == 'Deep Red' and action == 'USE':
         notify("{} uses Deep Red's ability to rehost {}".format(me,card))
         me.Clicks += 1
         card.markers[key] = 0
         # We do not return True on foundSpecial as we want the rest of the script to run its course as well.
      if key[0] == 'Blackmail' and action == 'USE' and not card.isFaceUp:
         foundSpecial = True
         whisper(":::ERROR::: You cannot rez ICE during this run, you are being Blackmailed!")
   return foundSpecial
   
def setAwareness(card):
# A function which stores if a special card exists in a player's deck, and activates extra scripts only then (to avoid unnecessary load)
   if card.name == 'Subliminal Messaging': # For now we only have subliminal. In the future we might get more card names separated by OR clauses.
      AwarenessList = eval(me.getGlobalVariable('Awareness'))
      if card.name not in AwarenessList: AwarenessList.append(card.name)
      me.setGlobalVariable('Awareness',str(AwarenessList))
   
#------------------------------------------------------------------------------
# Custom Remote Functions
#------------------------------------------------------------------------------

def ESA(): # Expert Schedule Analyzer
   debugNotify(">>> Remote Script ESA()") #Debug
   mute()
   revealedCards = []
   for c in me.hand: revealedCards.append(c)
   iter = 0
   for c in revealedCards:
      c.moveToTable(playerside * iter * cwidth(c) - (len(revealedCards) * cwidth(c) / 2), 0 - yaxisMove(c), False)
      c.highlight = RevealedColor
      iter += 1
   notify("The Expert Schedule Analyzer reveals {}".format([c.name for c in revealedCards]))
   while not confirm("You have revealed your hand to your opponent. Return them to HQ?\n\n(Pressing 'No' will send a ping to your opponent to see if they're done reading them)"):
      notify("{} would like to know if it's OK to return their remaining cards to their HQ.".format(me))
   for c in revealedCards: c.moveTo(me.hand)
         
def WitRD(): # Woman in the Red Dress   
   debugNotify(">>> Remote Script WitRD()") #Debug     
   mute()   
   cardView = me.piles['R&D/Stack'].top()
   debugNotify("Flipping top R&D card")
   cardView.isFaceUp = True
   rnd(1,10)
   notify(":> The Woman in the Red Dress has revealed {}".format(cardView))
   if confirm("Do you want to draw {} to your HQ?".format(cardView.name)):
      notify("{} decided to take {} to their hand".format(me,cardView))
      cardView.moveTo(me.hand)
   else: cardView.isFaceUp = False      

def Snoop(scenario = 'Simply Reveal', cardList = None):
   debugNotify(">>> Remote Script Snoop() with Scenario = {}".format(scenario)) #Debug     
   mute()
   if not cardList: cardList = []
   if scenario == 'Remote Corp Trash Select':
      choice = SingleChoice("Choose one card to trash", makeChoiceListfromCardList(cardList,True))
      if choice != None: 
         cardList[choice].moveTo(cardList[choice].owner.piles['Heap/Archives(Face-up)'])
         notify("{} decided to trash {} from the cards snooped at".format(me,cardList[choice]))
         cardList.remove(cardList[choice])
      for c in cardList: c.setController(c.owner)
      remoteCall(findOpponent(),"Snoop",['Recover Hand',cardList])            
   elif scenario == 'Recover Hand':
      for c in cardList: c.moveTo(me.hand)
   else:
      count = len(me.hand)
      if count == 0: 
         notify("There are no cards in the runner's Grip to snoop at")
         return
      iter = 0
      for c in me.hand:
         cardList.append(c)
         c.moveToTable(playerside * iter * cwidth(c) - (count * cwidth(c) / 2), 0 - yaxisMove(c), False)
         c.highlight = RevealedColor
         iter += 1
      notify("Snoop reveals {}".format([c.name for c in cardList]))
      if scenario == 'Simply Reveal':
         while not confirm("You have revealed your hand to your opponent. Return them to Grip?\n\n(Pressing 'No' will send a ping to your opponent to see if they're done reading them)"):
            notify("{} would like to know if it's OK to return their remaining cards to their Grip.".format(me))
         for c in cardList: c.moveTo(me.hand)
      elif scenario == 'Reveal and Trash':
         for c in cardList: c.setController(findOpponent())
         remoteCall(findOpponent(),"Snoop",['Remote Corp Trash Select',cardList])
         
def Leverage(card): # Leverage
   mute()
   barNotifyAll('#000000',"The corporation is deliberating if the runner's leverage is sufficient.")
   #notify(" - {} is deliberating if the runner's leverage is sufficient.".format(me))
   if confirm("Your opponent has just played Leverage. Do you want to take 2 Bad Publicity in order to allow them to still suffer damage until their next turn?"):
      me.counters['Bad Publicity'].value += 2
      notify("The corporation has decided to take 2 Bad Publicity. Beware!")
   else:
      CreateDummy('CreateDummy-with99protectionAllDMG-onOpponent', '', card)
      notify("--> The corporation has caved in to the runner's leverage. The runner cannot take any damage until the start of their next turn.")
      
def ExecWire(): # Expert Schedule Analyzer
   debugNotify(">>> Remote Script ExecWire()") #Debug
   mute()
   revealedCards = []
   for c in me.hand: revealedCards.append(c)
   iter = 0
   for c in revealedCards:
      c.moveToTable(playerside * iter * cwidth(c) - (len(revealedCards) * cwidth(c) / 2), 0 - yaxisMove(c), False)
      c.highlight = RevealedColor
      iter += 1
   notify("The Executive Wiretaps reveal {}".format([c.name for c in revealedCards]))
   while not confirm("You have revealed your hand to your opponent. Return them to HQ?\n\n(Pressing 'No' will send a ping to your opponent to see if they're done reading them)"):
      notify("{} would like to know if it's OK to return their remaining cards to their HQ.".format(me))
   for c in revealedCards: c.moveTo(me.hand)
         
      