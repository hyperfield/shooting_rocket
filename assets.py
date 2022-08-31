def get_rocket():
    rocket_frames = []
    for frame_no in range(1, 3):
        with open(f"frames/rocket_frame_{frame_no}.txt", "r") as my_file:
            rocket_frames.append(my_file.read())
    return rocket_frames
