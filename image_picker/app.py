from flask import Flask, render_template, request, abort
import os

# from flask_cors import cross_origin
app = Flask(__name__, template_folder='templates', static_folder='/')

@app.route("/imgPicker")
# @cross_origin(supports_credentials=True)
def index():
    print(os.path.dirname(__file__))
    dataId = request.args.get('imgDir', default='', type=str)
    dirName = os.path.join('cvat/assets/cvat_data/data', dataId, 'raw/')

    return render_template('all_images.html',taskId=request.args.get('task', default='', type=str), dataId=dataId, name=request.args.get('name', default='', type=str),
                           projectId=request.args.get('project', default='0', type=str), dirName=dirName)

if __name__ == "__main__":
    app.run(debug=True, port=80)
