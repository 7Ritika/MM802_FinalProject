import streamlit as st
import requests
from PIL import Image
import io

def display_recommendations(recommendations):
    st.write("Top 5 Recommended Products:")
    images = []
    for recommendation in recommendations:
        try:
            image_data = requests.get(recommendation['product_url']).content
            image = Image.open(io.BytesIO(image_data))
            images.append(image)
        except Exception as e:
            st.error(f"Failed to load image: {e}")
    st.image(images, width=150, use_column_width=True)

def fetch_and_display_recommendations(age, gender):
    try:
        response = requests.post('http://127.0.0.1:5000/recommend', json={'age': age, 'gender': gender})
        if response.status_code == 200:
            product_data = response.json()
            if product_data and 'recommendations' in product_data:
                recommendations = product_data['recommendations']
                if recommendations:
                    display_recommendations(recommendations)
                else:
                    st.write("No product recommendations available.")
            else:
                st.write("No product recommendations available.")
        else:
            st.error(f"Failed to get product recommendations. Status code: {response.status_code}")
    except Exception as e:
        st.error(f"Failed to fetch recommendations. Error: {e}")

def main():
    st.title('Demographic Enhanced Recommendation System')

    method = st.radio("Choose an input method:", ("Upload Image", "Capture Image"))
    image_data = None

    if method == "Upload Image":
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            image_data = uploaded_file.read()
            image = Image.open(io.BytesIO(image_data))
            st.image(image, caption='Uploaded Image', use_column_width=True)

    elif method == "Capture Image":
        img_file_buffer = st.camera_input("Take a picture")
        if img_file_buffer is not None:
            image_data = img_file_buffer.getvalue()
            image = Image.open(io.BytesIO(image_data))
            st.image(image, caption='Captured Image', use_column_width=True)

    if image_data and st.button('Process Image'):
        try:
            files = {'image': image_data}
            response = requests.post('http://127.0.0.1:5000/upload', files=files)
            if response.status_code == 200:
                processed_image = Image.open(io.BytesIO(response.content))
                st.image(processed_image, caption='Processed Image', use_column_width=True)
                
                detected_age = response.headers.get('Age')
                detected_gender = response.headers.get('Gender')
                
                if detected_age and detected_gender:
                    fetch_and_display_recommendations(int(detected_age), detected_gender)
                else:
                    st.error('Failed to detect age and gender.')
            else:
                st.error(f"Error from server: {response.status_code}. Message: {response.text}")
        except Exception as e:
            st.error(f"Failed to process the image. Error: {e}")

if __name__ == '__main__':
    main()
