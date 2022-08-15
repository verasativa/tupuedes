class FloatingWindow:
    def __init__(self, size):
        self.size = size
        self.data = []

    def update(self, new_datapoint):
        if len(self.data) > self.size:
            self.data = self.data[:self.size-1]
        self.data.insert(0, new_datapoint)

    def compare_splits(self, split_point):
        assert split_point < self.size
        if len(self.data) <  self.size:
            return None
        import statistics

        fist = statistics.mean(self.data[:split_point])
        second = statistics.mean(self.data[split_point:])

        return second - fist


def find_reps(peaks, valleys):
    # if plot:
    #     # fig, ax = plt.subplots(figsize = [16, 9])
    #     plt.pause(1/1000)
    #     line.set_xdata(range(detrend_data.shape[0]))
    #     line.set_ydata(detrend_data)
    #     fig.canvas.draw()
    #     # plt.xlim(0, nose_history.shape[0]
    #     # plt.plot(detrend_data)
    #     # plt.plot(peaks, detrend_data[peaks], "x")
    #     # plt.plot(valleys, detrend_data[valleys], "x")
    #     # ymin,ymax = ax.get_ylim()
    
    found_reps = []
    current_rep_candidate = None
    # Iterate over the index of index of valleys
    for valley_idx_idx  in range(len(valleys) - 1):
        previous_rep_candidate = current_rep_candidate
        current_valley_idx = valleys[valley_idx_idx]
        next_valley_idx = valleys[valley_idx_idx + 1]
        
        current_pick_idx = current_valley_idx
        # Iterate over the index of index of valleys since last peak
        for pick_idx_idx in range(len(peaks)):
            if current_pick_idx < peaks[pick_idx_idx]:
                current_pick_idx = peaks[pick_idx_idx]
                break
        if next_valley_idx > current_pick_idx:
            current_rep_candidate = (current_valley_idx, current_pick_idx, next_valley_idx)
        
        if previous_rep_candidate != current_rep_candidate:
            #print(current_rep_candidate)
            found_reps.append(current_rep_candidate)
            # if plot:
            #     ax.add_patch(Rectangle((current_valley_idx, ymin), next_valley_idx-current_valley_idx, ymax - ymin, facecolor='pink', edgecolor = 'black',
            #  fill=True,
            #  lw=1))
    
    return found_reps