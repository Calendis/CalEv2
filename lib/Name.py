# Name generation lists for species, and function to generate names
from random import randint

name_1 = [
"Achen",
"Andod",
"Anta",
"Archa",
"Az",
"Blos",
"Bomb",
"Cap",
"Cri",
"Cy",
"Chalk",
"Che",
"Cos",
"Demt",
"Des",
"Di",
"Dys",
"Er",
"Flan",
"Fold",
"Fosp",
"Hill",
"Holg",
"Hunn",
"Joll",
"Mar"
"Pel",
"Ple",
"Qu",
"Ray",
"Rizz",
"Spel",
"Ur",
"Yal",
"Zan",
"Zyk"
]
name_2 = [
"alchum",
"ar",
"aris",
"ario",
"barel",
"cenia",
"eb",
"ehio",
"engil"
"enic",
"enum",
"erium",
"esta",
"etok",
"eus",
"ia",
"ibus",
"ilia",
"in",
"ium",
"ius",
"ko",
"kolia",
"kolos",
"mia",
"more",
"olna",
"oria",
"orum",
"os",
"ozona",
"phage",
"rus",
"sus",
"tain",
"tokar",
"us"
]

def generate_name():
	name = name_1[randint(0, len(name_1)-1)]+name_2[randint(0, len(name_2)-1)]+" "+name_1[randint(0, len(name_1)-1)].lower()+name_2[randint(0, len(name_2)-1)]
	return name