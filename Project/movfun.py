import os
import glob
from natsort import natsorted
from PIL import Image
import io
from moviepy.editor import *

def bytes_to_image_pil(byte_data):
    image = Image.open(io.BytesIO(byte_data))
    return image

def create_video_from_images(image_list, image_lengths, output_file, transition_types=None, transition_duration=1, fps=24 , audio_file=None):
    # # Get absolute path of the image directory
    # base_dir = os.path.realpath(image_dir)
    
    # # Change directory to the image directory
    # os.chdir(base_dir)
    
    # # Get all the jpg, jpeg, and png files in the directory
    # file_list = glob.glob('*.jpg') + glob.glob('*.jpeg') + glob.glob('*.png')
    
    # # Sort the images
    # file_list_sorted = natsorted(file_list, reverse=False)
    file_list_sorted=[]
    for image_da in image_list:
        image=bytes_to_image_pil(image_da)
        file_list_sorted.append(image)

    # Check if the length of file_list_sorted matches the length of image_lengths
    if len(file_list_sorted) != len(image_lengths):
        print("Number of images and lengths do not match.")
        return
    
    # If transition_types is None, set all transitions to None
    if transition_types is None:
        transition_types = [None] * (len(file_list_sorted) - 1)
    
    # Create clips from images with specified durations and add transitions
    clips = []
    for i, (image_file, length) in enumerate(zip(file_list_sorted, image_lengths)):
        image_clip = ImageClip(image_file).set_duration(length)
        if i < len(transition_types):
            transition = transition_types[i]
            if transition == 1:
                # No transition
                pass
            elif transition == 2:
                # Crossfade in
                if i != 0:
                    image_clip = image_clip.crossfadein(transition_duration)
            elif transition == 3:
                # Crossfade out
                if i != len(file_list_sorted) - 1:
                    image_clip = image_clip.crossfadeout(transition_duration)
            elif transition == 4:
                # Crossfade in and out
                if i != 0:
                    image_clip = image_clip.crossfadein(transition_duration).set_start(length - transition_duration)
                if i != len(file_list_sorted) - 1:
                    image_clip = image_clip.crossfadeout(transition_duration)
            elif transition == 5:
                # Slide transition
                if i != 0:
                    image_clip = image_clip.slide_in(transition_duration).set_start(length - transition_duration)
                if i != len(file_list_sorted) - 1:
                    image_clip = image_clip.slide_out(transition_duration)
        clips.append(image_clip)
    
    # Concatenate clips into a single video clip
    concat_clip = concatenate_videoclips(clips, method="compose")
    
    if audio_file:
        audio_clip = AudioFileClip(audio_file)
        concat_clip = concat_clip.set_audio(audio_clip)

    # Write the video file
    concat_clip.write_videofile(output_file, fps=fps)

def add_audio_to_video(video_file, audio_file, output_file):
    # Load the video clip
    video_clip = VideoFileClip(video_file)
    
    # Load the audio clip
    audio_clip = AudioFileClip(audio_file)
    
    # Set the audio of the video clip
    video_clip = video_clip.set_audio(audio_clip)
    
    # Write the video file with the combined audio
    video_clip.write_videofile(output_file, codec="libx264", audio_codec="aac")

def add_text_to_video(video_file, text, text_duration, output_file):
    # Load the video clip
    video_clip = VideoFileClip(video_file)
    
    # Create a text clip
    txt_clip = TextClip(text, fontsize=30, color='white', bg_color='black').set_position(('center', 'bottom')).set_duration(text_duration)
    
    # Composite the text clip on top of the video clip
    final_clip = CompositeVideoClip([video_clip, txt_clip.set_duration(video_clip.duration)])
    
    # Write the final video file
    final_clip.write_videofile(output_file, codec="libx264", audio_codec="aac")



