import aiy.voicehat
import logging
import threading

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)

class ButtonListener(object):
    def __init__(self):
        self._status_ui = aiy.voicehat.get_status_ui()
        self._tracker_active = False
        self._task = threading.Thread(target=self._run_task)

    def start(self):
        self._status_ui.status('power-off')
        self._task.start()

    def _run_task(self):
        aiy.voicehat.get_button().on_press(self._toggle_button)
        print("starting")
        threading.Event().wait()

    def _toggle_button(self):
        if self._tracker_active:
            self._status_ui.status('power-off')
            print("stopping tracker")
            self._tracker_active = False
        else:
            self._status_ui.status('listening')
            print("starting tracker")
            self._tracker_active = True

def main():
    ButtonListener().start()

if __name__ == '__main__':
    main()
