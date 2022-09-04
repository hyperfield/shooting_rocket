def get_rocket_frames():
    rocket_frames = []
    for frame_no in range(1, 3):
        with open(f"frames/rocket_frame_{frame_no}.txt", "r") as frame_file:
            rocket_frames.append(frame_file.read())
    return rocket_frames
