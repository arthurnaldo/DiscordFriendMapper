// src/api.js

export const getServers = async () => {
    const response = await fetch('http://127.0.0.1:5000/api/servers');
    const data = await response.json();
    return data.servers;
  };
  
  export const updateGraph = async (serverName) => {
    const response = await fetch('http://127.0.0.1:5000/api/update_graph', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ server_name: serverName }),
    });
    return response.json();
  };
  
  export const getGraphUrl = (serverName) => {
    return `http://127.0.0.1:5000/api/graph/${serverName}`;
  };
  