import streamlit as st
import os
from utils import zoom_video, flip_video, copy_video, init, cleanup, get_temp_video_path

st.set_page_config(page_title="Demo", layout="wide", page_icon="📊")
# ---------------------------------- Page Styling -------------------------------------

with open("css/style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

# ---------------------------------- App View -----------------------------------------

# Créez un dossier "input" et mettez-y vos vidéos
TEMP_FOLDER = r"temp"


def main():
    init()
    cleanup()
    st.write("## Video Manipulation App")

    # Upload video file
    uploaded_file = st.sidebar.file_uploader("Upload video file", type=["mp4"])

    if uploaded_file is None:
        st.warning('Load file to process')
        return

    st.sidebar.write("---")
    # Logger in the sidebar for displaying messages
    logger = st.sidebar.empty()

    filters_row = st.columns((1, 2, 2, 1))
    zoom_factor_percent = filters_row[1].slider("Select zoom factor (%)", 100, 200, 110)
    operations = filters_row[2].multiselect(label='Choose Operations', options=['Flip', 'Copy'],
                                            placeholder="All", default=['Flip', 'Copy'])
    if len(operations) == 0:
        operations = ['Flip', 'Copy']

    flip = 'Yes' if 'Flip' in operations else 'No'
    copy = 'Yes' if 'Copy' in operations else 'No'

    if st.button('Apply'):
        cleanup()
        with st.spinner('Processing...'):
            # Save uploaded file to a temporary file in the temp folder
            temp_file_path = os.path.join(TEMP_FOLDER, "uploaded_video.mp4")
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(uploaded_file.read())

            # Perform zoom operation
            zoom_success = zoom_video(factor_percent=zoom_factor_percent)
            if not zoom_success:
                st.error("Failed to zoom video")
                os.remove(temp_file_path)
                return
            else:
                logger.info(f"Video zoomed to {zoom_factor_percent}%")

            # Perform flip operation
            if flip == 'Yes':
                flip_success = flip_video()
                if not flip_success:
                    st.error("Failed to flip video")
                    os.remove(temp_file_path)
                    return
                else:
                    logger.info("Video flipped successfully")

            # Perform copy operation
            if copy == 'Yes':
                success = copy_video()
                if not success:
                    st.error("Failed to copy video")
                    os.remove(temp_file_path)
                    return
                else:
                    logger.info("Video COPIED")

            # Display processed video
            processed_video_path = get_temp_video_path()

            out_row = st.columns((2, 1))
            out_row[0].success("Video processed successfully!")
            out_row[1].download_button(label='Download Processed Video :inbox_tray:',
                                       data=open(processed_video_path, 'rb').read(),
                                       file_name=os.path.basename(processed_video_path))

            st.subheader("Processed Video")
            st.video(processed_video_path)
            logger.success("Processing complete")


if __name__ == "__main__":
    main()
