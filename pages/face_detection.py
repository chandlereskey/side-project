import ast
import base64
import json
import dash
from dash import dcc, Input, Output, html, State
import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
from face_detection_helpers.generate_embeddings import generate_embeddings
import cv2
from face_detection_helpers.detect_face_and_return_frame import detect_faces
from connection import engine

dash.register_page(__name__, path='/face-detection')

def get_embeddings():
    embeddings_df = pd.read_sql('select * from dbo.user_image_embeddings', engine)
    embeddings = {}
    for i, row in embeddings_df.iterrows():
        print('getting embeddings dict', i, row)
        if row['user'] not in embeddings:
            embeddings[row['user']] = []
        
        embeddings[row['user']].append(json.loads(row['image_embedding']))
    for user, user_embeddings in embeddings.items():
        embeddings[user] = np.array(user_embeddings)
    return embeddings

embeddings_dict = get_embeddings()


layout = dbc.Container([
    html.H1('Face Detection'),
    dbc.Row([dbc.Input(id='user-name', placeholder='Enter your name'), dbc.Button(id='save-name', children='Save')]),
    dbc.Row([dcc.Upload(id='image-uploader', children=dbc.Button('Upload Image'), multiple=True, disabled=True),
    dbc.Button('Start Camera', id='camera-toggle')]),
    html.Video(id='client-side-video', autoPlay=True, controls=True, hidden=True),
    html.Img(id='detected-faces', hidden=True),
    dcc.Store(id='client-side-video-store'),
    dcc.Interval(id='interval', interval=500, n_intervals=0),
    dcc.Interval(id='interval2', interval=500, n_intervals=0),
    ]
    , fluid=True)

@dash.callback(
    Output('image-uploader', 'disabled'),
    Input('save-name', 'n_clicks'),
    prevent_initial_call=True
)
def show_image_uploader(n_clicks):
    if n_clicks is None:
        return True
    return False

@dash.callback(
    Input("image-uploader", "contents"),
    State("user-name", "value")
)
def generate_embeddings_callback(contents, user_name):
    embeddings = generate_embeddings(contents)
    user_input_list = [user_name for i in range(len(embeddings))]
    print(embeddings[0])
    emb_df = pd.DataFrame({
                'user': user_input_list,
                'image_embedding': [str(embedding) for embedding in embeddings]
            })
    with engine.connect() as connection:
        print('writing embeddings to db', emb_df['user'][0], emb_df['image_embedding'][0][:10])
        emb_df.to_sql('user_image_embeddings', connection, if_exists='append', index=False)
    global embeddings_dict
    embeddings_dict = get_embeddings()
    

@dash.callback(
    Output('detected-faces', 'src'),
    Output('detected-faces', 'hidden'),
    Input('interval2', 'n_intervals'),
    State('client-side-video-store', 'data')
)
def detect_faces_callback(interval, image):
    if image is None:
        return None, True
    image = image.replace('data:image/jpeg;base64,', '')

    # turn the base64 image into a numpy array
    img = base64.b64decode(image)
    np_frame = np.frombuffer(img, dtype=np.uint8)
    img = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)
    # detect faces in the image
    frame = detect_faces(img, embeddings_dict)
    # encode the frame back to base64
    _, buffer = cv2.imencode('.jpg', frame)
    frame = base64.b64encode(buffer).decode('utf-8')
    return 'data:image/jpeg;base64,' + frame, False
    


@dash.callback(
    Output('camera-toggle', 'children'),
    Output('client-side-video', 'hidden'),
    Input('camera-toggle', 'n_clicks'),
    State('camera-toggle', 'children'),
    State('client-side-video', 'hidden'),
    prevent_initial_call=True
)
def start_camera(n_clicks, button_text, hidden):
    if n_clicks is None:
        return button_text, hidden
    if button_text == 'Stop Camera':
        return 'Start Camera', True
    return 'Stop Camera', False


dash.clientside_callback(
    """
    async function(n_clicks, button_text) {
        var video = document.querySelector('video');

        if (button_text === 'Stop Camera') {
            console.log('Stopping camera')
            video.srcObject.getTracks().forEach(track => track.stop());
            video.srcObject = null;
        }

        navigator.getUserMedia = navigator.mediaDevices.getUserMedia ||
            navigator.webkitGetUserMedia ||
            navigator.mozGetUserMedia ||
            navigator.msGetUserMedia || null;

        var constraints = {
                video: true,
                audio:false
            };
        var media = null
        await navigator.mediaDevices.getUserMedia(constraints).then(function(stream) {
            media = stream
            video.srcObject = stream;
            video.onloadedmetadata = function(e) {
                video.play();  
            };
        }) 
        console.log('media data', media)
    }
    """,
    Input('camera-toggle', 'n_clicks'),
    State('camera-toggle', 'children'),
    prevent_initial_call=True
)

dash.clientside_callback(
    """
    function(n_intervals) {
        var video = document.getElementById('client-side-video');
        console.log('video:', video)
        if (!video || !video.srcObject) {
            return null;
        }
        

        var canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        var context = canvas.getContext('2d');
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        var frame = canvas.toDataURL('image/jpeg');
        console.log('frame:', frame)
        
        return frame; // Return base64 encoded image
    }
    """,
    Output('client-side-video-store', 'data'),
    Input('interval', 'n_intervals')
)

