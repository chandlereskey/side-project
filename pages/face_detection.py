import base64
import dash
from dash import dcc, Input, Output, html, State
import dash_bootstrap_components as dbc
import numpy as np
import plotly.express as px
from face_detection.generate_embeddings import generate_embeddings
import cv2
from face_detection.detect_face_and_return_frame import embeddings, detect_faces


dash.register_page(__name__, path='/face-detection')



layout = dbc.Container([
    dbc.Row([dcc.Upload(id='image-uploader', children=dbc.Button('Upload Image'), multiple=True),
    dbc.Button('Start Camera', id='camera-toggle')]),
    html.Video(id='client-side-video', autoPlay=True, controls=True, hidden=True),
    dcc.Store(id='client-side-video-store'),
    dcc.Interval(id='interval', interval=1000, n_intervals=0),
    ]
    , fluid=True)

@dash.callback(
    Input("image-uploader", "contents"),
)
def generate_embeddings_callback(contents):
    print(contents)
    generate_embeddings(contents)

@dash.callback(
    Input('client-side-video-store', 'data'),
)
def detect_faces_callback(image):
    print(image)

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
            return null;
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
        return media;
    }
    """,
    Output('client-side-video-store', 'data'),
    Input('camera-toggle', 'n_clicks'),
    State('camera-toggle', 'children'),
    prevent_initial_call=True
)


# @dash.callback(
#     Output('live-webcam-feed', 'figure'),
#     Input('interval', 'n_intervals')
# )
# def detect_faces_callback(n):
#     cap = cv2.VideoCapture(0)
#     ret, frame = cap.read()
#     # Decode the frame data
#     frame = base64.b64decode(frame)
#     np_frame = np.frombuffer(frame, dtype=np.uint8)
#     img = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)
    
#     # Convert the image to a Plotly figure
#     fig = px.imshow(img)
#     fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
#     return fig

