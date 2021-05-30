import json

lines = []
with open('india_states.txt') as f:
    lines = f.readlines()

states = {}
for line in lines:
    
    words = line.split()
    print(words)
    tmp = 1
    state = ""
    while "(" not in words[tmp]:
        state += words[tmp] + " "
        tmp += 1
    states[words[0]] = {"name":state, "lat": float(words[tmp+1]), "lon": float(words[tmp+2])}
print(states)

with open("india_states.json", "w") as outfile: 
    json.dump(states, outfile)