# app.py

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS  # Import CORS for handling cross-origin requests
import os
import sqlite3
from discord_bot import create_interactive_graph_from_sql  # Import the function to generate graph from DB

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests (for React frontend)

# Route to get list of servers
@app.route('/api/servers', methods=['GET'])
def get_servers():
    """Return a list of all server names from the database"""
    conn = sqlite3.connect('interactions.db')
    c = conn.cursor()
    c.execute('SELECT DISTINCT server_name FROM messages')
    servers = [row[0] for row in c.fetchall()]
    conn.close()
    return jsonify({"servers": servers})

# Route to update graph for a specific server
@app.route('/api/update_graph', methods=['POST'])
def update_graph():
    """Regenerate the graph for a server and return success message"""
    server_name = request.json.get('server_name')  # Get the server name from JSON
    if not server_name:
        return jsonify({"error": "Server name is required!"}), 400

    create_interactive_graph_from_sql(server_name)  # Generate graph for that server
    return jsonify({"message": f"Graph for server {server_name} updated successfully!"})

# Route to serve the graph for a specific server
@app.route('/api/graph/<server_name>', methods=['GET'])
def graph(server_name):
    """Serve the graph for a specific server"""
    graph_filename = f'{server_name}_interaction_graph.html'
    graph_path = os.path.join('static', graph_filename)
    
    if os.path.exists(graph_path):
        return send_from_directory('static', graph_filename)
    
    return jsonify({"error": "Graph not found!"}), 404

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
