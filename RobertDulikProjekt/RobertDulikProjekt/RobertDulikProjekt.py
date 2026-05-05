import pygame
import sys
import enemy
import playerclass
import logic
from pathlib import Path
import os
pygame.init()

screen = pygame.display.set_mode((1400, 780))
pygame.display.set_caption('GR-2D')
clock = pygame.time.Clock()
#formatowanie tekstu
test_font = pygame.font.Font(None, 75)
running = True
gray = (128,128,128)
custom_orange = (255,121,32)
run_text = test_font.render("RUN GAME", True, custom_orange)
export_text = test_font.render("EXPORT SCOREBOARD", True, custom_orange)
score_title = test_font.render("NAME  |  TIME  |  DEATHS", True, custom_orange)
erase_text = test_font.render("ERASE SCOREBOARD", True, custom_orange)
scores = []
score_text_rect = score_title.get_rect(center = (710,40))
run_text_rect = run_text.get_rect(center = (695,620))
exp_text_rect = export_text.get_rect(center = (695,680))
erase_text_rect = erase_text.get_rect(center = (695,740))
desktop_path = logic.get_desktop_path()
file_path = desktop_path / "GR2D_SCORES.txt"
#odczytywanie wynikow z ukrytego pliku
this_dir = Path(__file__).parent
priv_file_path = this_dir / "GR2D_SCORES.txt"
if os.path.exists(priv_file_path):
    with open(priv_file_path, "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
    lines.pop(0)
    for line in lines:
        tempscore = ["a", "a", "a"]
        parts = [part.strip() for part in line.split("|")]
        tempscore[0] = parts[1]
        tempscore[1] = parts[2]
        tempscore[2] = parts[0]
        scores.append(tempscore)

while running:
    runscore = [] #czas-0, zgony-1, nazwa-2
    screen.fill(gray)
    screen.blit(score_title, score_text_rect)
    screen.blit(run_text, run_text_rect)
    screen.blit(export_text, exp_text_rect)
    screen.blit(erase_text,erase_text_rect)
    #pokazywanie max 8 wynikow bo tyle sie miesci
    if scores:
        if len(scores) > 8:
            for i in range(8):
                single_score = scores[i]
                single_score_text = test_font.render(f"{single_score[2]} | {single_score[0]} | {single_score[1]}", True, custom_orange)
                single_score_rect = single_score_text.get_rect(center = (695, (100+(i*55)))) #max 8
                screen.blit(single_score_text,single_score_rect)
        elif len(scores) <= 7 and len(scores) >= 1:
            for i in range(len(scores)):
                single_score = scores[i]
                single_score_text = test_font.render(f"{single_score[2]} | {single_score[0]} | {single_score[1]}", True, custom_orange)
                single_score_rect = single_score_text.get_rect(center = (695, (100+(i*55)))) #max 8
                screen.blit(single_score_text,single_score_rect)
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        #szukanie myszki
        if event.type == pygame.MOUSEBUTTONDOWN:
            if run_text_rect.collidepoint(event.pos): #odpal gre
                logic.mainloop(screen, runscore)
                scores.append(runscore)
                scores.sort(key=lambda x: x[0])
                finalstring = "NAME  |  TIME  |  DEATHS\n" #autozapis
                for i in range(len(scores)):
                    single_score = scores[i]
                    tempstring = single_score[2] + " | " + single_score[0] + " | " + single_score[1] + "\n"
                    finalstring = finalstring + tempstring
                priv_file_path.write_text(finalstring)
            if erase_text_rect.collidepoint(event.pos): #wymaz wyniki
                scores = []
                finalstring = "NAME  |  TIME  |  DEATHS\n"
                for i in range(len(scores)):
                    single_score = scores[i]
                    tempstring = single_score[2] + " | " + single_score[0] + " | " + single_score[1] + "\n"
                    finalstring = finalstring + tempstring
                priv_file_path.write_text(finalstring)
            if exp_text_rect.collidepoint(event.pos): #eksportuj na pulpit
                finalstring = "NAME  |  TIME  |  DEATHS\n"
                for i in range(len(scores)):
                    single_score = scores[i]
                    tempstring = single_score[2] + " | " + single_score[0] + " | " + single_score[1] + "\n"
                    finalstring = finalstring + tempstring
                file_path.write_text(finalstring)
    clock.tick(60)