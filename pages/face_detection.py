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
    html.Img(id='detected-faces', hidden=True),
    dcc.Store(id='client-side-video-store'),
    dcc.Interval(id='interval', interval=500, n_intervals=0),
    dcc.Interval(id='interval2', interval=500, n_intervals=0),
    ]
    , fluid=True)

@dash.callback(
    Input("image-uploader", "contents"),
)
def generate_embeddings_callback(contents):
    print(contents)
    generate_embeddings(contents)

@dash.callback(
    Output('detected-faces', 'src'),
    Output('detected-faces', 'hidden'),
    Input('interval2', 'n_intervals'),
    State('client-side-video-store', 'data')
)
def detect_faces_callback(interval, image):
    if image is None:
        return None, True
    print('image:', image[:20])
    image = image.replace('data:image/jpeg;base64,', '')

    # turn the base64 image into a numpy array
    img = base64.b64decode(image)
    np_frame = np.frombuffer(img, dtype=np.uint8)
    img = cv2.imdecode(np_frame, cv2.IMREAD_COLOR)
    # detect faces in the image
    frame = detect_faces(img, embeddings)
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

