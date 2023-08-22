# Use the official Python image as the base image
FROM python:3.9

# Set the working directory within the container
WORKDIR /app

# Install FFmpeg
RUN apt-get update && \
    apt-get install -y ffmpeg

# Copy the requirements file into the container
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files into the container
COPY . .

# Expose the port that the Streamlit app will run on
EXPOSE 8501


# Command to run the Streamlit application
CMD ["streamlit", "run", "streamlit_app.py"]