def get_rocket():
    rocket_frames = []
    for i in range(1, 3):
        with open(f"frames/rocket_frame_{i}.txt", "r") as my_file:
            rocket_frames.append(my_file.read())
    return rocket_frames
