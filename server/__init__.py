from flask import Flask, request, render_template, jsonify
import json
from pymongo import MongoClient
from datetime import datetime, timedelta
import os, sys

app = Flask(__name__)
client = MongoClient()
db = client['test']
posts = db['posts']
tasks_queue = db['queue']

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.json
        #print 'NODE: ' + str(data)
        data['time'] = datetime.now()
        
        doc_id = posts.insert(data)
        #print 'DOC_ID: ' + str(doc_id)

        # Check if there is any recent tasks
        uid = data['uid']        
        task = tasks_queue.find_one({'uid' : uid})
        if task is not None:
            tasks_queue.remove({'_id' : task['_id']}) # remove action from queue
            task.pop('_id', None)
            task.pop('uid', None)
            targets = task
        else:
            targets = None
        #print 'TASK: ' + str(task)

        # Push tasks to node
        response = {
            "status" : "ok",
            "doc_id" : str(doc_id),
            "targets" : targets #!TODO: send task to node
        }        
        #print 'RESPONSE: ' + str(response)
        return jsonify(response)
    elif request.method == 'GET':
        return render_template('index.html')
    else:
        return None

@app.route('/node/')
def show_nodes():
    return render_template('index.html')   

@app.route('/node/<node_id>')
def show_node_summary(node_id):
    """
    Grab the most recent data point provided by the node
    Update the JS/HTML webapp to show the current settings
    """
    dt = timedelta(minutes=1)
    time_a = datetime.now()
    time_b = datetime.now() - dt
    doc_template = {
        "uid" : node_id,
        "time" : {"$lt": time_a, "$gt": time_b} #!TODO search by time frame
    }
    # find the most recent data in the postsDB
    docs = posts.find(doc_template)
    if docs.count() > 0:
        for d in docs:
            print d
            watering = d['targets']['watering']
            cycle = d['targets']['cycle']
            photo1 = d['targets']['photo1']
            photo2 = d['targets']['photo2']
            smc1 = d['targets']['smc1']
            smc2 = d['targets']['smc2']
            smc3 = d['targets']['smc3']
            smc4 = d['targets']['smc4']
            lights_off = d['targets']['lights_off']
            lights_on = d['targets']['lights_on']
        print docs.count()
        snapshot = []
        return render_template('node_v1.html', node_id = node_id,
                                               snapshot = snapshot,
                                               watering = watering,
                                               cycle = cycle,
                                               photo1 = photo1,
                                               photo2 = photo2,
                                               lights_on = lights_on,
                                               lights_off = lights_off,
                                               smc1 = smc1,
                                               smc2 = smc2,
                                               smc3 = smc3,
                                               smc4 = smc4
        )
    else:
        return render_template('node_offline.html', node_id = node_id)

"""
API Functions
"""
@app.route('/api/update_queue', methods=['GET', 'POST'])
def update_queue():
    if request.method == "POST":
        try:
            data = request.form.to_dict()
            if data is not None:
                _id = tasks_queue.insert(data)
                status = "ok"
            else:
                status = "bad"
        except Exception as error:
            print str(error)
    else:
        status = "awful"
    response = {
        'status' : status    
    }
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
