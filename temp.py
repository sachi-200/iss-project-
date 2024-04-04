from movfun import *
import numpy as np
image_list = [
    np.random.randint(0, 255, size=(720, 1280, 3), dtype=np.uint8),
    np.random.randint(0, 255, size=(720, 1280, 3), dtype=np.uint8),
    np.random.randint(0, 255, size=(720, 1280, 3), dtype=np.uint8)
]
image_lengths = [3, 4, 5]  # Length of each image in seconds
output_file = "./output_video.mp4"
transition_types = [2, 3, 4]  # Transition types for each image
transition_duration = 1  # Duration of transition in seconds
fps = 24  # Frames per second
res = 720  # Resolution of the output video

# Call the function
create_video_from_images(
    image_list, image_lengths, output_file,
    transition_types=transition_types,
    transition_duration=transition_duration,
    fps=fps, res=res
)