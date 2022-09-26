from tupuedes.pipeline import Pipeline
from tupuedes.modes import SquatMode


class ModeManager(Pipeline):
    def __init__(self, aruco_map: dict, start_mode='auto', debug=False, **kwargs):
        super().__init__(**kwargs)
        self.debug = debug
        self.current_mode = start_mode
        self.modes = {}
        if start_mode == 'squat':
            self.modes['squat'] = SquatMode(debug=debug)

    def map(self, data):
        mode = self.modes[self.current_mode]
        mode.infer(data)

        data['mode'] = {
            'name': self.current_mode,
            'display_name': mode.display_name,
            'counters': mode.counters,
            'current_pose': mode.current_pose
        }
        if self.debug:
            data['mode']['debug_line'] = mode.debug_line

        return data

    def close(self):
        pass
