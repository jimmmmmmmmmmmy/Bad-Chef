# router for /recommendations/ endpoint that returns 10 recipes the user
# hasn't favorited yet

# fetch all recipes including user's favorited recipes
# generate embeddings for each recipe based on tags and ingredients
# use kNN to find similar recipes, excluding user favorites
# return top 10

# use sentence-bert to convert tags and ignredients into vectors
# probably do the embeddings like once a day?  
# on request, fetch embeddings, run kNN, return results?
# knn for fast lookups
# offline embedding to save time