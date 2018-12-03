import pickle
f = open("high_scores.dat","rb")
j = pickle.load(f)
print j 
