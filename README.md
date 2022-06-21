# Analysis of the boardgamegeek.com community
Website url: http://boardgamegeek.com

BGG is the largest and most popular platform for board games. Also, BGG Rating is the most prestigious rating of board games. However, when choosing a board game, it is not enough to check the rating, often you need the opinion of an experienced board game expert whose tastes are similar to yours, so you can form a complete opinion on the game before buying it. 

BGG provides access to data related to products on the board game market, as well as to the preferences of its users (they can rate different games on the site) and, moreover, to messages and published posts on the forum. This access is provided by means of their XML API: https://boardgamegeek.com/wiki/page/BGG_XML_API2

In this project we will be trying to analyze the interaction between BGG community members within the framework of the forum in a cross-section by categories of board games. The main goal of the project is to identify and eliminate clearly biased user reviews from the total number as they are caused by the user's antipathy to this type of games. And in turn, to find experts for the relevant board games, whose tastes are more likely to coincide with the user who requested an opinion about the board game.

---
## The main goals of the project are: 
    1. Build a graph of users interactions on the forum
    2. Update it with information on users given rating of particular boardgames and genres
    3. Make a research on graph of users interactions in a slice of boardgames preferences
    4. Create TG-bot, which sends the most suitable expert reviews based on the requested board game name, excluding deliberately biased reviews.
