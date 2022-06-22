## Students:
* Kuznetsov Dmitriy Sergeevich
* Mishkina Aleksandra Ahmadovna
* Eremin Gleb


# Analysis of the boardgamegeek.com community
Website url: http://boardgamegeek.com

BGG is the largest and most popular platform for board games. Also, BGG Rating is the most prestigious rating of board games. However, when choosing a board game, it is not enough to check the rating, often you need the opinion of an experienced board game expert whose tastes are similar to yours, so you can form a complete opinion on the game before buying it. 

BGG provides access to data related to products on the board game market, as well as to the preferences of its users (they can rate different games on the site) and, moreover, to messages and published posts on the forum. This access is provided by means of their XML API: https://boardgamegeek.com/wiki/page/BGG_XML_API2

In this project we will be trying to analyze the interaction between BGG community members within the framework of the forum in a cross-section by categories of board games. The main goal of the project is to identify and eliminate clearly biased user reviews from the total number as they are caused by the user\'s antipathy to this type of games. And in turn, to find experts for the relevant board games, whose tastes are more likely to coincide with the user who requested an opinion about the board game.

---
## The main goal of the project is:
    We want to build application which helps BGG users to choose suitable boardgame for them. Just for this purpose we want to extact expert-users and reviews for considering boardgame, using its forums interactions analysis. Moreover, we want to pick such top-k experts among diverse set, that their boardgame preferencies are similiar to a considered user.

## We implemented:
There is no any open data to solve our task. Moreover, forums information, boardgames lists update in a real-time, that`s why we can just get some dataset. But there is XML-API to the bgg site.
* That is why we implemented our own python-client for XML-api (`bgg_client` subfolder). It contains Sessions construction mechanisms and classes which encapsulate BGG entities.
* We constructed mechanisms to build forums interactions-graph. (there is an example of use in `experiment.ipynb` notebook. Core mechanics provided in core application runner `__main__.py`)
* We implemented graph-analysis pipeline, which gives us apportunity to extract expert users from the graph (there is an example of use in `experiment.ipynb` notebook. Core mechanics provided in core application runner `__main__.py`)
* We implemented our own CollaborativeFilterring (in particular, Latent Factor Model) package. It gives us an apportunity to construct collaborative embeddings of users preferencies, based on ratings their set on the platform for boardgames. Therefore, we earn an apportunity to evaluate users similarities. That\`s how we extract suitable for each user expert. (there is an example of use in `experiment.ipynb` notebook. Core mechanics provided in core application runner `__main__.py`)


## Notes:
* Main runner of the application is `__main__.py`
* Application has help-string: `python3 __main__.py -h`
* Before running core-application you need to store latent factors for model. You can gain it from `experiments.ipynb` notebook. (Next time we add approtunity to run application in a learning-regime).
