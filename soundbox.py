#!/usr/bin/env python3

'''
Class to play audio files, randomly, from subfolders
'''
import random
import glob
import pygame

resource_dir = "resources/"
warn_short_dir = resource_dir + "warn-short/"
warn_long_dir = resource_dir + "warn-long/"
reward_dir = resource_dir + "reward/"

pygame.mixer.init()


def warn_short():
    file = get_random_file(warn_short_dir)
    play_sound(file)


def warn_long():
    file = get_random_file(warn_long_dir)
    play_sound(file)


def reward():
    file = get_random_file(reward_dir)
    play_sound(file)


def get_random_file(folder, extension="*.mp3"):
    return random.choice(glob.glob(folder+extension))


def play_sound(audio_file):
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)


if __name__ == "__main__":
    play_sound(get_random_file(warn_short_dir))
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
