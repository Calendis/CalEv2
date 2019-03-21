# Name generation lists for species, and function to generate names
from random import randint
from math import atanh

syllables = ["os", "en", "an", "dod", "ta", "ar", "cha", "as", "bo", "om", "ca", "pri", "cri", "cy", "alk", "che", "cos", "demt", "des",
"di", "dys", "ko", "los", "we", "er", "fla", "fol", "fosp", "hil", "hun", "jol", "mar", "ple", "qu", "ray", "ar", "rizz", "spel", "ur",
"yal", "zan", "zyk", "alc", "um", "is", "ach", "rel", "cen", "eb", "hi", "chu", "ti", "hu", "wu", "eng", "il", "ia", "tok", "num", "e", "ib",
"us", "um", "ium", "ius", "lia", "mia", "mo", "re", "ol", "na", "io", "zon", "a", "o", "pha", "ge", "rus", "sus", "ai", "kar"]

def generate_name(genes):
	syllable_indices = []
	pc = 2*genes["point_count"]%len(syllables)
	syllable_indices.append(pc)
	size = 3*genes["size"]%len(syllables)
	syllable_indices.append(size)
	# Calculates hue
	r = genes["colour"][0]
	g = genes["colour"][1]
	b = genes["colour"][2]
	maxrgb = max([r, g, b])
	minrgb = min([r, g, b])
	if maxrgb == minrgb:
		minrgb = maxrgb-1	
	if maxrgb == r:
		hue = (g-b)/(maxrgb-minrgb)
	elif maxrgb == g:
		hue = 2 + (b-r)/(maxrgb-minrgb)
	elif maxrgb == b:
		hue = 4 + (r-g)/(maxrgb-minrgb)

	hue = 5*(60*int(hue))%len(syllables)	
	syllable_indices.append(hue)

	#bb = 7*int(atanh(genes["behaviour_bias"]))%len(syllables)
	#syllable_indices.append(bb)

	name = ""
	for i in syllable_indices:
		name += syllables[i]
	return name