import subprocess
import random
import glob

resource_dir = "../resources/"
warn_short_dir = resource_dir + "warn-short/"
warn_long_dir = resource_dir + "warn-long/"
reward_dir = resource_dir + "reward/"


def warn_short():
    file = get_random_file(warn_short_dir)
    play_sound(file)


def warn_long():
    file = get_random_file(warn_long_dir)
    play_sound(file)


def reward():
    file = get_random_file(reward_dir)
    play_sound(file)


def get_random_file(folder, extension="*.m4a"):
    return random.choice(glob.glob(folder+extension))


def play_sound(audio_file):
    return_code = subprocess.call(["afplay", audio_file])
    if return_code:
        print("error playing file %s: error code %s" % (audio_file, return_code))


if __name__ == "__main__":
    # play_sound(get_random_file(warn_short_dir))
    play_sound(get_random_file(resource_dir))
