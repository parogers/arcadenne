
# Arcadenne

A simple arcade cabinet interface for [Retroarch](https://www.retroarch.com/).

I wanted something very simple for my PI arcade cabinet. Although [EmulationStation](https://www.emulationstation.org/) is really nice, I found it too complicated for my set up. Similarly the interface for Retroarch is just too complicated for what I'm looking for.

My design requirements:

* Navigation is done through a single button, plus left/right directional controls
* Games are displayed in a single list (ie. no nested menus)
* The list of games should be navigated one at a time, carousel style, with the currently selected game taking up a clear majority of the screen space
* Game title cards are automatically generated from the ROMs and updated when new ones are added
* If a title card isn't available, the name of the game (guessed from the file name) should appear in large font
* Controls input mapping is managed through Retroarch
