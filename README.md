This is my Fitness Tracker Web App. It was made with Python, more particularly Django, using HTML&CSS for the front-end and a bit of JavaScript for styling. 

The main purpouse of the app is to ensure that the users can track all of their fitness progress. Every user can register and start tracking their workouts. 

Main functionalities are:

  -tracking workouts
  
  -being able to see registered workouts (user is able to sort by muscle group or by date for easier access to the data)
  
  -tracking BMI
  
  -being able to see records of your BMI levels (includes visual representation with Chart.js)
  
  -weather info for the users' city (using a weather API to get and display the weather information for the city that the user picked when they registed)
  
  -users have access to recommended exercises that are based on their stats such as height, weight, age, gender and more. The app recommends the best exercises for 
  a particular muscle group that the user wants to train today
  
  Recommendation logic uses scikit-learn. Using KNN and Cosine Similarity, we discover users that are close in stats to the user that requested the recommendations and based on the close neighbours'
  exercises we give recommendations to the user. (The big flaw of this model is that the app expects there to be data for the users and the exercises that they do, which I currently don't have. Also it expects
  the data to be absolutely correct and recommends exercises based on it.)
