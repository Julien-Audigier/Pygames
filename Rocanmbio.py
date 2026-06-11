import pygame
import os
import random
os.environ['SDL_AUDIODRIVER'] = 'dummy'
pygame.init()

def askList(list, question):
    for item in list:
        print(f"{list.index(item)+1}. {item}")
    return (list[int(input(question+"    "))-1])

aiPlay = ""
plays = ["Rock", "Paper", "Scissors"]

while True:
    if input("Play? (Y or N)") == "Y":
        aiPlay = plays[random.randint(0,2)]
        playerPlay = askList(plays,"Which one?")
        match aiPlay:
            case "Rock":
                if playerPlay == "Paper":
                    print("player wins")
                elif playerPlay == "Scissors":
                    print("Ai wins")
                else:
                    print("tie")
            case "Paper":
                    if playerPlay == "Paper":
                        print("tie")
                    elif playerPlay == "Scissors":
                        print("player wins")
                    else:
                        print("ai wins")
            case "Scissors":
                if playerPlay == "Paper":
                    print("player losses")
                elif playerPlay == "Scissors":
                    print("tie")
                else:
                    print("player wins")

