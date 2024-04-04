import os
import glob
from natsort import natsorted
from PIL import Image
import io
from moviepy.editor import *
from array import array

def bytes_to_image_pil(byte_data):
    try:
        image = Image.open(io.BytesIO(byte_data))
        return image
    except Exception as e:
        print("Error:", e)
        print("Byte data:", byte_data)
        return None

def create_video_from_images(image_list, image_lengths, output_file, transition_types=None, transition_duration=1, fps=24 , audio_file=None, res=720):
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
    resolutions = {
        360: (480, 360),
        480: (854, 480),
        720: (1280, 720),
        1080: (1920, 1080)
    }
    width, height = resolutions[res]

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


def re_edit_video(base_video, adjustments_data, output_file):
    # Load the base video clip
    base_clip = VideoFileClip(base_video)
    
    # Apply adjustments based on the received data
    
    # Adjust brightness
    brightness = adjustments_data.get('brightness', 0)
    base_clip = base_clip.fx(vfx.colorx, brightness=brightness)
    
    # Adjust contrast
    contrast = adjustments_data.get('contrast', 1.0)
    base_clip = base_clip.fx(vfx.colorx, contrast=contrast)
    
    # Adjust saturation
    saturation = adjustments_data.get('saturation', 1.0)
    base_clip = base_clip.fx(vfx.colorx, saturation=saturation)
    
    # Convert to grayscale
    greyscale = adjustments_data.get('greyscale', False)
    if greyscale:
        base_clip = base_clip.fx(vfx.colorx, colormatrix=[0.2989, 0.5870, 0.1140])
    
    # Apply sepia effect
    sepia = adjustments_data.get('sepia', False)
    if sepia:
        base_clip = base_clip.fx(vfx.colorx, colormatrix=[[0.393, 0.769, 0.189],
                                                         [0.349, 0.686, 0.168],
                                                         [0.272, 0.534, 0.131]])
    
    # Rotate hue
    hue_rotate = adjustments_data.get('hue_rotate', 0)
    base_clip = base_clip.fx(vfx.hue, hsl_adjustment=[hue_rotate])
    
    # Invert colors
    invert = adjustments_data.get('invert', False)
    if invert:
        base_clip = base_clip.fx(vfx.invert_colors)
    
    # Apply blur
    blur = adjustments_data.get('blur', 0)
    base_clip = base_clip.fx(vfx.blur, blur)
    
    # Set opacity
    opacity = adjustments_data.get('opacity', 1.0)
    base_clip = base_clip.fx(vfx.opacity, opacity)
    
    # Apply transformations
    
    # Scale X & Y
    scaleXY = adjustments_data.get('scaleXY', 1.0)
    base_clip = base_clip.fx(vfx.resize, fx=scaleXY, fy=scaleXY)
    
    # Scale X
    scaleX = adjustments_data.get('scaleX', 1.0)
    base_clip = base_clip.fx(vfx.resize, fx=scaleX)
    
    # Scale Y
    scaleY = adjustments_data.get('scaleY', 1.0)
    base_clip = base_clip.fx(vfx.resize, fy=scaleY)
    
    # Move X
    translateX = adjustments_data.get('translateX', 0)
    base_clip = base_clip.fx(vfx.move_right, pixels=translateX)
    
    # Move Y
    translateY = adjustments_data.get('translateY', 0)
    base_clip = base_clip.fx(vfx.move_down, pixels=translateY)
    
    # Skew X
    skewX = adjustments_data.get('skewX', 0)
    base_clip = base_clip.fx(vfx.skew, x_angle=skewX)
    
    # Skew Y
    skewY = adjustments_data.get('skewY', 0)
    base_clip = base_clip.fx(vfx.skew, y_angle=skewY)
    
    # Rotate
    rotate = adjustments_data.get('rotate', 0)
    base_clip = base_clip.rotate(rotate)
    
    # Apply mix blend mode
    mix_blend_mode = adjustments_data.get('mix_blend_mode', None)
    if mix_blend_mode:
        base_clip = base_clip.fx(vfx.compositing_mode, mix_blend_mode)
    
    # Apply text overlay if provided
    text = adjustments_data.get('text', '')
    if text:
        text_duration = adjustments_data.get('text_duration', 3)  # Default duration of text
        txt_clip = (TextClip(text, fontsize=30, color='white', bg_color='black')
                    .set_position(('center', 'bottom'))
                    .set_duration(text_duration))
        base_clip = CompositeVideoClip([base_clip, txt_clip.set_duration(base_clip.duration)])
    
    # Write the edited video file
    base_clip.write_videofile(output_file)
