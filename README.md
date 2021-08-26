# Restaurant Recommendation System based on reviews

### Overview
Our restaurant recommendation system focuses on providing a search interface for information retrieval and recommends restaurants based on user reviews. The ranking of restaurants is done based on a free-text search query entered by the user and the reviews of the restaurants.
The project analyzes the ratings provided by the end-users and uses this data to recommend foods and restaurants to the users. The recommendation is provided on the grounds of the feedback of different people on the food items, the services offered by the restaurant, and the location mentioned by the user. Our main objective is to facilitate free-text queries for restaurant search and recommendation by improving the semantic interpretation of queries. This involves aspects matching between the query and review content.

The problem that we are trying to address is the text-based querying for restaurant search since most of the review-based recommendation systems do not provide this facility. The novelty in our project is that our system will display restaurants based on the free-text query search that matches the features in reviews of a restaurant.

### Structure
Our code consists of two parts, Web to create the interface and Python script to execute the search query. For Web, we have used Laravel framework built on PHP, which uses MVC architecture. MVC stands for Model-View-Controller, a software architectural pattern that is used for implementing user interfaces. It divides the software or application into three categories, i.e. model, view, and controller. The model implements the business logic, the view consists of the blade files, which are basically PHP embedded HTML files, and the controller handles all the actions. The UI primarily consists of a home page and a listings page.
The Python script is present along with framework modules at the top layer. The intermediate results that are saved are also present in the same directory.
For configuring the environment variables, we use the .env file, which is also present at the top layer.


### Dependencies
For Python
* pandas - to read the dataset
* nltk - to perform preprocessing
* numpy - to perform vector computations
* fuzzywuzzy - for string matching upto an extent
* pickle - to save our intermediate results to speed up computation
* json - to return data to the client

For Web
* composer - dependency manager for PHP
* apache - server to host the website

### Methodology
We use HTML and CSS for frontend designing, JS for handling event at the client side, and PHP for the backend. We use the FuzzyWuzzy library to match the name and location of the restaurant. It uses Levenshtein Distance (also known as Edit Distance) under the hood. If name or location, either of them is provided, we first filter out the restaurants based on them, then use BM25 to compute the scores and rank them according to the free-text query. BM25 internally uses TF and IDF, we compute TF for every query document pair, and IDF for every document. To get the result from our Python script, we execute shell command in PHP. That returns the list of top 50 restaurants in JSON format.

### Assumptions
* Currently showing only top 50 results
* BM25 variant implemented uses free parameters k1=1.5 and b=0.5
