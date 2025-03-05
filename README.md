# pvmachat
 A real time chat made with Python

# Steps to run pvmachat
- First you need to install the libraries: uvicorn, websockets, PyQt6 and FastAPI
'''bash
pip install uvicorn websockets[all] pyqt6 fastapi
'''

- Then you first execute the server (main.py) with the following command:
'''bash
uvicorn main:app --reload
'''

- Finally, execute the client (client.py):
'''bash
python client.py
'''